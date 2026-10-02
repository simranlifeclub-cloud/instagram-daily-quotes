import os
import sys
import asyncio
import subprocess
import shutil
import math
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCENES_DIR = os.path.join(BASE_DIR, "assets", "scenes")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
TEMP_DIR = os.path.join(OUTPUT_DIR, "temp_reality_check")
AUDIO_DIR = os.path.join(BASE_DIR, "assets", "audio")
FONTS_DIR = os.path.join(BASE_DIR, "assets", "fonts")

# 4 Storyboard Scenes: "The Reality Check & Reset (Calm & Grounding)"
STORYBOARD_SCENES = [
    {
        "id": 1,
        "image_file": os.path.join(SCENES_DIR, "scene1_typing_fast.jpg"),
        "lines": ["Stop scrolling", "for 10 seconds."],
        "speech": "Drop your shoulders. ... Unclench your jaw. ... Take a real breath.",
        "duration": 4.5,
        "motion": "ZOOM_IN"
    },
    {
        "id": 2,
        "image_file": os.path.join(SCENES_DIR, "scene2_closing_laptop.jpg"),
        "lines": ["That email can wait."],
        "speech": "That urgent email? It can wait ten minutes. The world won't end if a spreadsheet isn't done right this second.",
        "duration": 6.8,
        "motion": "PAN_DOWN"
    },
    {
        "id": 3,
        "image_file": os.path.join(SCENES_DIR, "scene3_walking_outside.jpg"),
        "lines": ["Work pays bills.", "It shouldn't cost peace."],
        "speech": "You traded your time for a paycheck. Not your health, not your mental peace, and definitely not your life.",
        "duration": 8.7,
        "motion": "ZOOM_OUT"
    },
    {
        "id": 4,
        "image_file": os.path.join(SCENES_DIR, "scene4_calm_smile.jpg"),
        "lines": ["You are doing enough."],
        "speech": "Do your job with honesty, but remember to leave work at work. You're building a life, not just a career.",
        "duration": 10.0,
        "motion": "BREATHE"
    }
]

REALITY_CHECK_CAPTION = (
    "Drop your shoulders. Unclench your jaw. Take a real breath. 🌿✨\n\n"
    "That urgent email? It can wait 10 minutes. The world will keep spinning if that spreadsheet isn't finished right this second.\n\n"
    "You traded your time for a paycheck—not your nervous system, not your peace of mind, and definitely not your life.\n\n"
    "Work hard, be honest, and execute well. But when the workday ends, remember to leave work at work.\n\n"
    "You are building a life, not just a career.\n\n"
    ".\n"
    ".\n"
    "📌 Save this reminder for the next time your workday overwhelms you.\n"
    "↗️ Send this to a coworker or friend who needs to take a breath today.\n\n"
    "Follow @simranlifeclub for daily inner peace, calm perspective & strength.\n"
    ".\n"
    ".\n"
    "#simranlifeclub #workplacewellness #burnoutprevention #mindsetshift #innerpeace #mentalclarity #worklifebalance #takeabreath #quietstrength"
)


def get_font(font_name, size):
    font_path = os.path.join(FONTS_DIR, font_name)
    if os.path.exists(font_path):
        try:
            return ImageFont.truetype(font_path, size)
        except Exception:
            pass
    # System fallbacks
    fallbacks = [
        "/System/Library/Fonts/Supplemental/Georgia.ttf",
        "/System/Library/Fonts/Supplemental/Georgia Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
    ]
    for fb in fallbacks:
        if os.path.exists(fb):
            try:
                return ImageFont.truetype(fb, size)
            except Exception:
                pass
    return ImageFont.load_default()


def render_scene_overlay(lines, output_png):
    """Renders a transparent 1080x1920 overlay with crisp white typography in the center."""
    target_w, target_h = 1080, 1920
    im = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)

    font_title = get_font("Georgia Bold.ttf", 52)
    font_watermark = get_font("Georgia.ttf", 22)

    # Line spacing & measurements
    line_height = 68
    total_text_h = len(lines) * line_height
    start_y = (target_h - total_text_h) // 2 - 40

    # Draw soft diffused shadow first
    shadow_offsets = [(0, 3, 140), (0, -2, 60), (-2, 0, 60), (2, 0, 60), (0, 6, 90)]
    for ox, oy, alpha in shadow_offsets:
        curr_y = start_y + oy
        for line in lines:
            draw.text((target_w // 2 + ox, curr_y), line, font=font_title, fill=(0, 0, 0, alpha), anchor="ma")
            curr_y += line_height

    # Draw primary crisp white text
    curr_y = start_y
    for line in lines:
        draw.text((target_w // 2, curr_y), line, font=font_title, fill=(255, 255, 255, 255), anchor="ma")
        curr_y += line_height

    # Branding in safe-zone (y=1580, completely clear of Instagram UI)
    watermark = "@simranlifeclub"
    draw.text((target_w // 2, 1582), watermark, font=font_watermark, fill=(0, 0, 0, 160), anchor="ma")
    draw.text((target_w // 2, 1580), watermark, font=font_watermark, fill=(255, 255, 255, 175), anchor="ma")

    os.makedirs(os.path.dirname(os.path.abspath(output_png)), exist_ok=True)
    im.save(output_png, "PNG")
    return output_png


def generate_scene_motion_clip(image_path, overlay_png, output_mp4, duration=5.0, motion="ZOOM_IN", fps=30):
    """Generates an animated 1080x1920 MP4 video clip with Ken Burns camera tracking and text overlay."""
    total_frames = int(duration * fps)

    if motion == "ZOOM_IN":
        zoom_expr = f"zoompan=z='min(zoom+0.00030,1.06)':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps={fps}"
    elif motion == "ZOOM_OUT":
        zoom_expr = f"zoompan=z='max(1.06-0.00030*on,1.0)':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps={fps}"
    elif motion == "PAN_DOWN":
        zoom_expr = f"zoompan=z='1.05':d={total_frames}:x='iw/2-(iw/zoom/2)':y='min(ih-ih/zoom,ih/2-(ih/zoom/2)+0.07*on)':s=1080x1920:fps={fps}"
    else:  # BREATHE
        zoom_expr = f"zoompan=z='1.03+0.02*sin(2*3.14159*on/{total_frames})':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps={fps}"

    filter_complex = (
        f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,{zoom_expr}[bg];"
        f"[bg][1:v]overlay=0:0[v]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-framerate", str(fps), "-t", str(duration), "-i", image_path,
        "-loop", "1", "-framerate", str(fps), "-t", str(duration), "-i", overlay_png,
        "-filter_complex", filter_complex,
        "-map", "[v]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p",
        "-t", str(duration),
        output_mp4
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    return output_mp4


async def _synthesize_voice_edgetts(full_text, output_mp3, voice_id="en-US-EricNeural"):
    import edge_tts
    comm = edge_tts.Communicate(full_text, voice_id, rate="-3%", pitch="+0Hz")
    await comm.save(output_mp3)
    return output_mp3


def synthesize_full_voiceover(output_mp3, voice_id="en-US-EricNeural"):
    """Synthesizes the complete voiceover narration with calming pacing."""
    os.makedirs(os.path.dirname(os.path.abspath(output_mp3)), exist_ok=True)
    # Combine scene speech with natural calming pauses
    full_speech = " ... ".join([s["speech"] for s in STORYBOARD_SCENES])

    try:
        import edge_tts
        asyncio.run(_synthesize_voice_edgetts(full_speech, output_mp3, voice_id=voice_id))
        if os.path.exists(output_mp3) and os.path.getsize(output_mp3) > 1000:
            print(f"[VOICE] Neural Voiceover synthesized successfully with {voice_id}.")
            return output_mp3
    except Exception as e:
        print(f"[WARN] Edge-TTS voice generation fallback: {e}")

    # Fallback to macOS say if available
    if sys.platform == "darwin":
        try:
            aiff_temp = output_mp3.replace(".mp3", ".aiff")
            cmd = ["say", "-v", "Daniel", "-r", "160", "-o", aiff_temp, full_speech]
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            subprocess.run(["ffmpeg", "-y", "-i", aiff_temp, output_mp3], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if os.path.exists(aiff_temp):
                os.remove(aiff_temp)
            if os.path.exists(output_mp3):
                return output_mp3
        except Exception:
            pass

    return None


def build_reality_check_reel(output_mp4=None, voice_id="en-US-EricNeural"):
    """
    Builds the complete 30-second multi-scene 'Reality Check & Reset' Reel:
    - 4 motion scenes with Ken Burns camera tracking
    - Crisp typography on-screen text
    - Studio neural voiceover narration
    - Soft acoustic piano / lo-fi background music ducked underneath
    """
    os.makedirs(TEMP_DIR, exist_ok=True)
    if not output_mp4:
        output_mp4 = os.path.join(OUTPUT_DIR, "reality_check_reset_reel.mp4")
    os.makedirs(os.path.dirname(os.path.abspath(output_mp4)), exist_ok=True)

    print("\n" + "=" * 65)
    print("🎬 Rendering: The Reality Check & Reset (Calm & Grounding Reel)")
    print("=" * 65)

    # 1. Synthesize Full Voiceover Audio
    voice_path = os.path.join(TEMP_DIR, "voiceover.mp3")
    synthesize_full_voiceover(voice_path, voice_id=voice_id)

    # 2. Select Ambient / Piano Music
    bg_music = None
    candidate_audio = [
        os.path.join(AUDIO_DIR, "cinematic_satie_piano.mp3"),
        os.path.join(AUDIO_DIR, "lofi_chillhop.mp3"),
        os.path.join(AUDIO_DIR, "melodic_piano_rondo.mp3")
    ]
    for c in candidate_audio:
        if os.path.exists(c):
            bg_music = c
            break

    # 3. Render Each Scene Motion Video Clip
    clip_files = []
    concat_list_file = os.path.join(TEMP_DIR, "concat_scenes.txt")
    with open(concat_list_file, "w") as f_list:
        for scene in STORYBOARD_SCENES:
            scene_id = scene["id"]
            img_path = scene["image_file"]
            if not os.path.exists(img_path):
                raise FileNotFoundError(f"Missing scene image: {img_path}")

            overlay_png = os.path.join(TEMP_DIR, f"scene_{scene_id}_overlay.png")
            render_scene_overlay(scene["lines"], overlay_png)

            clip_mp4 = os.path.join(TEMP_DIR, f"scene_{scene_id}_clip.mp4")
            print(f"[SCENE {scene_id}] Rendering motion clip ({scene['duration']}s): {' '.join(scene['lines'])}...")
            generate_scene_motion_clip(
                img_path,
                overlay_png,
                clip_mp4,
                duration=scene["duration"],
                motion=scene["motion"]
            )
            clip_files.append(clip_mp4)
            f_list.write(f"file '{clip_mp4}'\n")

    # 4. Concatenate Video Scenes
    concatenated_video = os.path.join(TEMP_DIR, "scenes_combined.mp4")
    concat_cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", concat_list_file,
        "-c", "copy",
        concatenated_video
    ]
    subprocess.run(concat_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    total_duration = sum(s["duration"] for s in STORYBOARD_SCENES)

    # 5. Composite Mixed Audio (Voiceover + Ducked Music)
    print("[AUDIO] Compositing voiceover narration and ambient piano soundtrack...")
    final_audio = os.path.join(TEMP_DIR, "final_audio.wav")
    has_voice = voice_path and os.path.exists(voice_path)

    if has_voice and bg_music and os.path.exists(bg_music):
        audio_cmd = [
            "ffmpeg", "-y",
            "-i", voice_path,
            "-stream_loop", "-1", "-i", bg_music,
            "-filter_complex",
            (
                f"[0:a]volume=1.4[voice];"
                f"[1:a]volume=0.22,afade=t=in:st=0:d=1.0,afade=t=out:st={total_duration-2.0}:d=2.0[music];"
                f"[voice][music]amix=inputs=2:duration=first:dropout_transition=2[out]"
            ),
            "-map", "[out]",
            "-t", str(total_duration),
            final_audio
        ]
        subprocess.run(audio_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    elif bg_music and os.path.exists(bg_music):
        audio_cmd = [
            "ffmpeg", "-y",
            "-stream_loop", "-1", "-i", bg_music,
            "-af", f"volume=0.8,afade=t=in:st=0:d=1.0,afade=t=out:st={total_duration-2.0}:d=2.0",
            "-t", str(total_duration),
            final_audio
        ]
        subprocess.run(audio_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    elif has_voice:
        final_audio = voice_path

    # 6. Final Assemble into Finished Reel
    print(f"[EXPORT] Assembling final 1080x1920 MP4 Reel ({total_duration:.1f}s)...")
    cmd_final = [
        "ffmpeg", "-y",
        "-i", concatenated_video,
        "-i", final_audio,
        "-map", "0:v",
        "-map", "1:a",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-t", str(total_duration),
        output_mp4
    ]
    subprocess.run(cmd_final, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # 7. Generate Cover Thumbnail from Scene 2 or 3
    thumb_path = os.path.join(OUTPUT_DIR, "reality_check_cover.jpg")
    shutil.copy(STORYBOARD_SCENES[1]["image_file"], thumb_path)

    print(f"🎉 [SUCCESS] Finished Reel created at: {output_mp4}")
    print(f"📸 Cover thumbnail at: {thumb_path}")
    return output_mp4, thumb_path, REALITY_CHECK_CAPTION


if __name__ == "__main__":
    build_reality_check_reel()
