import os
import sys
import subprocess
import random
import shutil

from card_renderer import render_quote_card, render_quote_card_overlay, get_theme_for_background
from background_manager import select_dynamic_background, get_available_backgrounds
from audio_manager import select_dynamic_audio, populate_starter_audio_library
from voice_synthesizer import synthesize_quote_speech, mix_voice_and_music
from video_manager import select_dynamic_video, generate_motion_video_from_image, prepare_looping_video_background

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BG_DIR = os.path.join(BASE_DIR, "assets", "backgrounds")
DEFAULT_BG = os.path.join(BG_DIR, "serene_sunrise.jpg")

# 5 Cinematic Camera Motion Presets
MOTION_PRESETS = [
    {
        "id": "ZOOM_IN",
        "name": "Slow Cinematic Push-In",
        "expr": lambda total_frames: (
            f"zoompan=z='min(zoom+0.00035,1.07)':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30"
        )
    },
    {
        "id": "ZOOM_OUT",
        "name": "Slow Scenery Reveal Pull-Back",
        "expr": lambda total_frames: (
            f"zoompan=z='max(1.07-0.00035*on,1.0)':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30"
        )
    },
    {
        "id": "PAN_UP",
        "name": "Slow Vertical Horizon Pan Up",
        "expr": lambda total_frames: (
            f"zoompan=z='1.05':d={total_frames}:x='iw/2-(iw/zoom/2)':y='max(0,ih/2-(ih/zoom/2)-0.08*on)':s=1080x1920:fps=30"
        )
    },
    {
        "id": "PAN_DOWN",
        "name": "Slow Vertical Horizon Pan Down",
        "expr": lambda total_frames: (
            f"zoompan=z='1.05':d={total_frames}:x='iw/2-(iw/zoom/2)':y='min(ih-ih/zoom,ih/2-(ih/zoom/2)+0.08*on)':s=1080x1920:fps=30"
        )
    },
    {
        "id": "BREATHE",
        "name": "Subtle Ambient Camera Pulse",
        "expr": lambda total_frames: (
            f"zoompan=z='1.03+0.025*sin(2*3.14159*on/{total_frames})':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30"
        )
    }
]

REEL_FORMATS = ["SHORT_VIDEO", "PURE_CINEMATIC", "VOICEOVER"]


def select_dynamic_reel_format(history, slot=None):
    """
    Selects the next reel format matching the aesthetic reels grid:
    1. SHORT_VIDEO (70%): Aesthetic nature/lifestyle video loop + minimalist white centered quote
    2. PURE_CINEMATIC (15%): Pure scenic visual mood reel + ambient music (no text)
    3. VOICEOVER (15%): Aesthetic motion video + spoken wisdom + ducked music
    """
    slot_map = {
        "morning": "SHORT_VIDEO",
        "midday": "SHORT_VIDEO",
        "afternoon": "PURE_CINEMATIC",
        "evening": "SHORT_VIDEO",
        "night": "VOICEOVER"
    }
    preferred = slot_map.get(slot, "SHORT_VIDEO")
    used_formats = history.get("used_formats", [])
    
    # Don't repeat non-standard formats consecutively
    if used_formats and used_formats[-1] in ("PURE_CINEMATIC", "VOICEOVER"):
        return "SHORT_VIDEO"

    return preferred or "SHORT_VIDEO"


def build_mp4_reel(
    quote_data,
    output_mp4,
    duration=12,
    reel_format=None,
    bg_image_path=None,
    bg_video_path=None,
    audio_path=None,
    voice_id=None,
    theme_name=None,
    history=None
):
    """
    Builds an Instagram Reel matching the aesthetic nature & lifestyle grid:
    - SHORT_VIDEO (Aesthetic motion video loop + clean white centered quote)
    - PURE_CINEMATIC (Pure scenic landscape B-roll + ambient soundtrack)
    - VOICEOVER (Aesthetic footage + spoken voice narration + ducked music)
    """
    if history is None:
        history = {}

    temp_dir = os.path.join(BASE_DIR, "output", "temp")
    os.makedirs(temp_dir, exist_ok=True)
    slot = quote_data.get("slot", "morning")

    # 1. Resolve Reel Format
    if not reel_format:
        reel_format = select_dynamic_reel_format(history, slot=slot)

    # 2. Resolve Background Photo & Theme
    if not bg_image_path:
        bg_image_path, bg_filename = select_dynamic_background(history, slot=slot)
    else:
        bg_filename = os.path.basename(bg_image_path)

    # 3. Resolve Music Soundtrack
    audio_display_name = "Ambient Soundtrack"
    audio_id = "default_audio"
    if not audio_path:
        temp_audio = os.path.join(temp_dir, f"music_{quote_data['id']}.wav")
        audio_path, audio_display_name, audio_id = select_dynamic_audio(
            history, quote_slot=slot, output_temp_wav=temp_audio
        )
    else:
        audio_display_name = os.path.splitext(os.path.basename(audio_path))[0].replace("_", " ").title()
        audio_id = os.path.basename(audio_path)

    # 4. Resolve Voiceover Narration if format is VOICEOVER
    voice_name = None
    final_audio_path = audio_path
    if reel_format == "VOICEOVER":
        voice_temp = os.path.join(temp_dir, f"voice_{quote_data['id']}.mp3")
        voice_res, voice_name = synthesize_quote_speech(quote_data, voice_temp, voice_id=voice_id)
        if voice_res and os.path.exists(voice_res):
            mixed_audio = os.path.join(temp_dir, f"mixed_audio_{quote_data['id']}.wav")
            final_audio_path = mix_voice_and_music(voice_res, audio_path, mixed_audio, duration=duration)
        else:
            reel_format = "SHORT_VIDEO"

    # 5. Render Cover Card Thumbnail
    card_img = os.path.join(temp_dir, f"card_{quote_data['id']}.jpg")
    _, applied_theme = render_quote_card(
        quote_data, card_img, bg_image_path=bg_image_path, theme_name=theme_name
    )

    fps = 30
    total_frames = int(duration * fps)

    # Prepare motion background video
    if not bg_video_path:
        bg_video_path, video_filename = select_dynamic_video(history, slot=slot)
        
    video_bg_temp = os.path.join(temp_dir, f"prepared_video_{quote_data['id']}.mp4")
    if bg_video_path and os.path.exists(bg_video_path):
        prepare_looping_video_background(bg_video_path, video_bg_temp, duration=duration)
        used_video_label = os.path.basename(bg_video_path)
    else:
        # Generate smooth cinematic camera motion video loop from high-res photograph
        generate_motion_video_from_image(bg_image_path, video_bg_temp, duration=duration, fps=fps)
        used_video_label = f"Motion Loop ({bg_filename})"

    # -------------------------------------------------------------
    # FORMAT 1 & 2: SHORT_VIDEO & VOICEOVER (Video loop + Minimalist Text Overlay)
    # -------------------------------------------------------------
    if reel_format in ("SHORT_VIDEO", "VOICEOVER"):
        overlay_png = os.path.join(temp_dir, f"overlay_{quote_data['id']}.png")
        render_quote_card_overlay(quote_data, overlay_png, theme_name=applied_theme)

        cmd = [
            "ffmpeg", "-y",
            "-i", video_bg_temp,
            "-i", overlay_png,
            "-i", final_audio_path,
            "-filter_complex", "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920[bg];[bg][1:v]overlay=0:0[v]",
            "-map", "[v]",
            "-map", "2:a",
            "-af", f"afade=t=in:st=0:d=1.2,afade=t=out:st={duration-1.8}:d=1.8",
            "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k",
            "-t", str(duration),
            output_mp4
        ]
        motion_name = f"Cinematic Video + Aesthetic Overlay [{used_video_label}]"

    # -------------------------------------------------------------
    # FORMAT 3: PURE_CINEMATIC (Pure scenic B-roll mood reel, no text)
    # -------------------------------------------------------------
    elif reel_format == "PURE_CINEMATIC":
        cmd = [
            "ffmpeg", "-y",
            "-i", video_bg_temp,
            "-i", final_audio_path,
            "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
            "-map", "0:v",
            "-map", "1:a",
            "-af", f"afade=t=in:st=0:d=1.2,afade=t=out:st={duration-1.8}:d=1.8",
            "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k",
            "-t", str(duration),
            output_mp4
        ]
        motion_name = f"Pure Scenic B-Roll [{used_video_label}]"

    # -------------------------------------------------------------
    # FORMAT 4: TEXT_POSTER FALLBACK
    # -------------------------------------------------------------
    else:
        motion = random.choice(MOTION_PRESETS)
        motion_name = motion["name"]
        vf_filter = f"scale=1080:1920,{motion['expr'](total_frames)}"
        af_filter = f"afade=t=in:st=0:d=1.0,afade=t=out:st={duration-1.8}:d=1.8"

        cmd = [
            "ffmpeg", "-y",
            "-loop", "1", "-framerate", str(fps), "-t", str(duration), "-i", card_img,
            "-i", final_audio_path,
            "-vf", vf_filter,
            "-af", af_filter,
            "-c:v", "libx264", "-preset", "medium", "-crf", "22", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k",
            "-t", str(duration),
            output_mp4
        ]

    print("\n-------------------------------------------------------")
    print(f"[REEL ENGINE] Rendering Multi-Format MP4 Reel ({duration}s)")
    print(f"  • Format:     {reel_format}")
    print(f"  • Background: {bg_filename}")
    print(f"  • Theme:      {applied_theme}")
    print(f"  • Voiceover:  {voice_name or 'None (Music Only)'}")
    print(f"  • Music:      {audio_display_name}")
    print(f"  • Motion:     {motion_name}")
    print("-------------------------------------------------------")

    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        # Fallback simpler encode
        fallback_cmd = [
            "ffmpeg", "-y",
            "-loop", "1", "-framerate", str(fps), "-t", str(duration), "-i", card_img,
            "-i", final_audio_path,
            "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k",
            "-t", str(duration),
            output_mp4
        ]
        fb_res = subprocess.run(fallback_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if fb_res.returncode != 0:
            raise RuntimeError(f"FFmpeg failed: {fb_res.stderr}")

    metadata = {
        "format": reel_format,
        "background": bg_filename,
        "theme": applied_theme,
        "voice": voice_name,
        "audio": audio_display_name,
        "audio_id": audio_id,
        "motion": motion_name
    }

    print(f"[SUCCESS] High-Retention Reel Ready: {output_mp4}\n")
    return output_mp4, card_img, metadata
