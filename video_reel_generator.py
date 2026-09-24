import os
import sys
import subprocess
import numpy as np
import scipy.io.wavfile as wavfile
from card_renderer import render_quote_card

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_BG = os.path.join(BASE_DIR, "assets", "backgrounds", "serene_sunrise.jpg")


def synthesize_ambient_audio(output_wav, duration=12.0, sample_rate=44100):
    """
    Synthesizes a 12-second serene ambient soundtrack with warm chords,
    ethereal pad swells, and celestial chimes.
    """
    num_samples = int(duration * sample_rate)
    t = np.linspace(0, duration, num_samples, endpoint=False)
    
    left = np.zeros(num_samples, dtype=np.float32)
    right = np.zeros(num_samples, dtype=np.float32)
    
    def m2f(n): return 440.0 * (2.0 ** ((n - 69.0) / 12.0))
    
    # 3 Progressing warm chords (Fmaj7 -> Am9 -> Bbmaj9)
    chords = [
        {"start": 0.0, "end": 4.0, "notes": [53, 57, 60, 64, 67], "root": 41},
        {"start": 4.0, "end": 8.0, "notes": [45, 60, 64, 67, 71], "root": 45},
        {"start": 8.0, "end": 12.0, "notes": [46, 58, 62, 65, 69], "root": 46}
    ]
    
    for c in chords:
        s_idx = int(c["start"] * sample_rate)
        e_idx = min(num_samples, int((c["end"] + 1.0) * sample_rate))
        dur = (e_idx - s_idx) / sample_rate
        t_seg = np.linspace(0, dur, e_idx - s_idx, endpoint=False)
        
        # Soft envelope
        env = np.ones(len(t_seg), dtype=np.float32)
        att = min(len(t_seg) // 3, int(1.0 * sample_rate))
        rel = min(len(t_seg) // 3, int(1.0 * sample_rate))
        env[:att] = np.sin(np.linspace(0, np.pi/2, att))
        env[-rel:] = np.cos(np.linspace(0, np.pi/2, rel))
        
        c_l, c_r = np.zeros_like(t_seg), np.zeros_like(t_seg)
        for i, n in enumerate(c["notes"]):
            freq = m2f(n)
            tone_l = 0.7 * np.sin(2 * np.pi * freq * 0.999 * t_seg) + 0.3 * np.sin(4 * np.pi * freq * t_seg)
            tone_r = 0.7 * np.sin(2 * np.pi * freq * 1.001 * t_seg) + 0.3 * np.sin(4 * np.pi * freq * t_seg)
            pan = (i / len(c["notes"])) * 0.6 + 0.2
            c_l += tone_l * (1.0 - pan)
            c_r += tone_r * pan
            
        root_f = m2f(c["root"])
        sub = 0.45 * np.sin(2 * np.pi * root_f * t_seg)
        c_l += sub * 0.4
        c_r += sub * 0.4
        
        left[s_idx:e_idx] += c_l * env * 0.22
        right[s_idx:e_idx] += c_r * env * 0.22
        
    # Subtle chime notes
    chimes = [(1.0, 76), (4.5, 79), (8.5, 81)]
    for c_time, c_note in chimes:
        s_idx = int(c_time * sample_rate)
        e_idx = min(num_samples, s_idx + int(3.0 * sample_rate))
        seg_len = e_idx - s_idx
        if seg_len > 0:
            t_chime = np.linspace(0, seg_len / sample_rate, seg_len, endpoint=False)
            f_chime = m2f(c_note)
            c_env = np.exp(-t_chime / 0.7)
            c_wave = (0.7 * np.sin(2 * np.pi * f_chime * t_chime) + 0.3 * np.sin(2 * np.pi * 2.76 * f_chime * t_chime)) * c_env
            left[s_idx:e_idx] += c_wave * 0.12 * 0.6
            right[s_idx:e_idx] += c_wave * 0.12 * 0.4

    # Master Fade In & Out
    fade_len = int(1.2 * sample_rate)
    left[:fade_len] *= np.linspace(0, 1, fade_len)
    right[:fade_len] *= np.linspace(0, 1, fade_len)
    left[-fade_len:] *= np.linspace(1, 0, fade_len)
    right[-fade_len:] *= np.linspace(1, 0, fade_len)
    
    # Headroom Normalization
    peak = max(np.max(np.abs(left)), np.max(np.abs(right)))
    if peak > 0:
        left = (left / peak) * 0.85
        right = (right / peak) * 0.85
        
    stereo = np.stack([left, right], axis=1)
    wavfile.write(output_wav, sample_rate, (stereo * 32767.0).astype(np.int16))
    return output_wav


def build_mp4_reel(quote_data, output_mp4, duration=12, bg_path=DEFAULT_BG):
    """
    Renders an animated 1080x1920 MP4 Reel with soft audio using ffmpeg.
    Applies cinematic slow Ken Burns zoom to the background.
    """
    temp_dir = os.path.join(BASE_DIR, "output", "temp")
    os.makedirs(temp_dir, exist_ok=True)
    
    card_img = os.path.join(temp_dir, f"card_{quote_data['id']}.png")
    audio_wav = os.path.join(temp_dir, f"audio_{quote_data['id']}.wav")
    
    # 1. Render high-res graphic card
    render_quote_card(quote_data, card_img, bg_path)
    
    # 2. Synthesize ambient audio
    synthesize_ambient_audio(audio_wav, duration=duration)
    
    # 3. Render video using ffmpeg with cinematic slow zoom (Ken Burns)
    fps = 30
    total_frames = int(duration * fps)
    
    # ffmpeg command:
    # - Loops the card image
    # - Applies subtle zoompan: zoom from 1.0 to 1.05 over 12 seconds
    # - Encodes with H.264 (yuv420p for maximum Instagram compatibility)
    # - Pairs with AAC stereo audio
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-framerate", str(fps), "-t", str(duration), "-i", card_img,
        "-i", audio_wav,
        "-vf", f"scale=1080:1920,zoompan=z='min(zoom+0.0003,1.06)':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps={fps}",
        "-c:v", "libx264", "-preset", "medium", "-crf", "22", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-shortest",
        output_mp4
    ]
    
    print(f"[INFO] Rendering MP4 Reel: {output_mp4} ({duration}s)...")
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        # Fallback to simple static image video without zoompan filter if zoompan fails
        print("[WARN] Advanced zoom filter failed. Using clean static frame video encoding...")
        fallback_cmd = [
            "ffmpeg", "-y",
            "-loop", "1", "-framerate", str(fps), "-t", str(duration), "-i", card_img,
            "-i", audio_wav,
            "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-shortest",
            output_mp4
        ]
        fb_res = subprocess.run(fallback_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if fb_res.returncode != 0:
            raise RuntimeError(f"FFmpeg Reel generation failed: {fb_res.stderr}")
            
    print(f"[SUCCESS] MP4 Reel generated: {output_mp4}")
    return output_mp4
