import os
import sys
import subprocess
import random
import shutil

from card_renderer import render_quote_card, get_theme_for_background
from background_manager import select_dynamic_background, get_available_backgrounds
from audio_manager import select_dynamic_audio, populate_starter_audio_library

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


def build_mp4_reel(
    quote_data,
    output_mp4,
    duration=12,
    bg_image_path=None,
    audio_path=None,
    theme_name=None,
    history=None
):
    """
    Renders a stunning 1080x1920 Instagram Reel with:
    1. Fresh atmospheric background image (from 9+ aesthetic landscapes)
    2. Complementary visual card theme & custom typography
    3. Fresh audio soundtrack (from audio library or 8-style procedural engine)
    4. Cinematic Ken Burns camera motion
    """
    if history is None:
        history = {}

    temp_dir = os.path.join(BASE_DIR, "output", "temp")
    os.makedirs(temp_dir, exist_ok=True)
    slot = quote_data.get("slot", "morning")

    # 1. Select Background
    if not bg_image_path:
        bg_image_path, bg_filename = select_dynamic_background(history, slot=slot)
    else:
        bg_filename = os.path.basename(bg_image_path)

    # 2. Select Audio Track / Synthesized Style
    audio_display_name = "Ambient Soundtrack"
    audio_id = "default_audio"
    if not audio_path:
        temp_audio = os.path.join(temp_dir, f"audio_{quote_data['id']}.wav")
        audio_path, audio_display_name, audio_id = select_dynamic_audio(
            history, quote_slot=slot, output_temp_wav=temp_audio
        )
    else:
        audio_display_name = os.path.splitext(os.path.basename(audio_path))[0].replace("_", " ").title()
        audio_id = os.path.basename(audio_path)

    # 3. Render Custom Themed Cover Card Thumbnail
    card_img = os.path.join(temp_dir, f"card_{quote_data['id']}.jpg")
    _, applied_theme = render_quote_card(
        quote_data, card_img, bg_image_path=bg_image_path, theme_name=theme_name
    )

    # 4. Select Camera Motion
    motion = random.choice(MOTION_PRESETS)
    fps = 30
    total_frames = int(duration * fps)
    vf_filter = f"scale=1080:1920,{motion['expr'](total_frames)}"

    # 5. Build FFmpeg command with smooth audio fade-in & fade-out
    af_filter = f"afade=t=in:st=0:d=1.2,afade=t=out:st={duration - 1.8}:d=1.8,volume=0.92"

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-framerate", str(fps), "-t", str(duration), "-i", card_img,
        "-i", audio_path,
        "-vf", vf_filter,
        "-af", af_filter,
        "-c:v", "libx264", "-preset", "medium", "-crf", "22", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-t", str(duration),
        output_mp4
    ]

    print("\n-------------------------------------------------------")
    print(f"[REEL ENGINE] Rendering High-Retention MP4 Reel ({duration}s)")
    print(f"  • Background: {bg_filename}")
    print(f"  • Theme:      {applied_theme}")
    print(f"  • Music:      {audio_display_name}")
    print(f"  • Motion:     {motion['name']}")
    print("-------------------------------------------------------")

    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        # Fallback without zoompan in case of older FFmpeg build
        fallback_cmd = [
            "ffmpeg", "-y",
            "-loop", "1", "-framerate", str(fps), "-t", str(duration), "-i", card_img,
            "-i", audio_path,
            "-af", af_filter,
            "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-t", str(duration),
            output_mp4
        ]
        fb_res = subprocess.run(fallback_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if fb_res.returncode != 0:
            raise RuntimeError(f"FFmpeg failed: {fb_res.stderr}")

    metadata = {
        "background": bg_filename,
        "theme": applied_theme,
        "audio": audio_display_name,
        "audio_id": audio_id,
        "motion": motion["id"]
    }

    print(f"[SUCCESS] Fresh Look Reel Ready: {output_mp4}\n")
    return output_mp4, card_img, metadata
