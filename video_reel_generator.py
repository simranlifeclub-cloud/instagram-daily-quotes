import os
import sys
import subprocess
import random
import numpy as np
import scipy.io.wavfile as wavfile
from card_renderer import render_quote_card, create_procedural_background

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_BG = os.path.join(BASE_DIR, "assets", "backgrounds", "serene_sunrise.jpg")

# 5 Aesthetic Color Schemes for Visual Variety
VISUAL_STYLES = [
    {"name": "golden_sunrise", "base": (20, 16, 28), "glow": (245, 199, 108)},
    {"name": "midnight_obsidian", "base": (8, 12, 22), "glow": (100, 180, 245)},
    {"name": "emerald_forest", "base": (10, 22, 18), "glow": (120, 225, 160)},
    {"name": "crimson_dusk", "base": (24, 12, 18), "glow": (255, 130, 110)},
    {"name": "celestial_violet", "base": (18, 12, 28), "glow": (200, 140, 255)}
]

# Musical Chord Palettes for Audio Variety
CHORD_PALETTES = [
    # 1. Sunrise Hope (Fmaj7 -> Am9 -> Bbmaj9)
    [
        {"start": 0.0, "end": 4.0, "notes": [53, 57, 60, 64, 67], "root": 41},
        {"start": 4.0, "end": 8.0, "notes": [45, 60, 64, 67, 71], "root": 45},
        {"start": 8.0, "end": 12.0, "notes": [46, 58, 62, 65, 69], "root": 46}
    ],
    # 2. Stoic Deep Focus (Dm9 -> Gm7 -> Cmaj7)
    [
        {"start": 0.0, "end": 4.0, "notes": [50, 57, 60, 64, 69], "root": 38},
        {"start": 4.0, "end": 8.0, "notes": [55, 58, 62, 65, 69], "root": 43},
        {"start": 8.0, "end": 12.0, "notes": [48, 55, 60, 64, 67], "root": 36}
    ],
    # 3. Night Peace & Serenity (Dbmaj7 -> Abmaj7 -> Bbm9)
    [
        {"start": 0.0, "end": 4.0, "notes": [49, 56, 60, 65, 68], "root": 37},
        {"start": 4.0, "end": 8.0, "notes": [44, 56, 60, 63, 67], "root": 44},
        {"start": 8.0, "end": 12.0, "notes": [46, 53, 58, 61, 65], "root": 46}
    ]
]


def synthesize_ambient_audio(output_wav, duration=12.0, sample_rate=44100):
    num_samples = int(duration * sample_rate)
    t = np.linspace(0, duration, num_samples, endpoint=False)
    
    left = np.zeros(num_samples, dtype=np.float32)
    right = np.zeros(num_samples, dtype=np.float32)
    
    def m2f(n): return 440.0 * (2.0 ** ((n - 69.0) / 12.0))
    
    chords = random.choice(CHORD_PALETTES)
    
    for c in chords:
        s_idx = int(c["start"] * sample_rate)
        e_idx = min(num_samples, int((c["end"] + 1.0) * sample_rate))
        dur = (e_idx - s_idx) / sample_rate
        t_seg = np.linspace(0, dur, e_idx - s_idx, endpoint=False)
        
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
            pan = (i / max(1, len(c["notes"]) - 1)) * 0.6 + 0.2
            c_l += tone_l * (1.0 - pan)
            c_r += tone_r * pan
            
        root_f = m2f(c["root"])
        sub = 0.45 * np.sin(2 * np.pi * root_f * t_seg)
        c_l += sub * 0.4
        c_r += sub * 0.4
        
        left[s_idx:e_idx] += c_l * env * 0.22
        right[s_idx:e_idx] += c_r * env * 0.22
        
    fade_len = int(1.2 * sample_rate)
    left[:fade_len] *= np.linspace(0, 1, fade_len)
    right[:fade_len] *= np.linspace(0, 1, fade_len)
    left[-fade_len:] *= np.linspace(1, 0, fade_len)
    right[-fade_len:] *= np.linspace(1, 0, fade_len)
    
    peak = max(np.max(np.abs(left)), np.max(np.abs(right)))
    if peak > 0:
        left = (left / peak) * 0.85
        right = (right / peak) * 0.85
        
    stereo = np.stack([left, right], axis=1)
    wavfile.write(output_wav, sample_rate, (stereo * 32767.0).astype(np.int16))
    return output_wav


def build_mp4_reel(quote_data, output_mp4, duration=12):
    temp_dir = os.path.join(BASE_DIR, "output", "temp")
    os.makedirs(temp_dir, exist_ok=True)
    
    card_img = os.path.join(temp_dir, f"card_{quote_data['id']}.png")
    audio_wav = os.path.join(temp_dir, f"audio_{quote_data['id']}.wav")
    
    # Render with background
    render_quote_card(quote_data, card_img, DEFAULT_BG)
    synthesize_ambient_audio(audio_wav, duration=duration)
    
    fps = 30
    total_frames = int(duration * fps)
    
    # Randomize zoom direction (slow zoom in OR slow zoom out)
    zoom_expr = "min(zoom+0.0003,1.06)" if random.random() > 0.5 else "max(1.06-0.0003*on,1.0)"
    
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-framerate", str(fps), "-t", str(duration), "-i", card_img,
        "-i", audio_wav,
        "-vf", f"scale=1080:1920,zoompan=z='{zoom_expr}':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps={fps}",
        "-c:v", "libx264", "-preset", "medium", "-crf", "22", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-shortest",
        output_mp4
    ]
    
    print(f"[INFO] Rendering unique MP4 Reel: {output_mp4} ({duration}s)...")
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
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
            raise RuntimeError(f"FFmpeg failed: {fb_res.stderr}")
            
    print(f"[SUCCESS] High-retention Reel ready: {output_mp4}")
    return output_mp4
