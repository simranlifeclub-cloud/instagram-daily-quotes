import os
import random
import subprocess
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VIDEOS_DIR = os.path.join(BASE_DIR, "assets", "videos")


def get_available_videos():
    """Returns list of video filenames in assets/videos/"""
    if not os.path.exists(VIDEOS_DIR):
        os.makedirs(VIDEOS_DIR, exist_ok=True)
        return []
    valid_exts = (".mp4", ".mov", ".m4v", ".webm")
    files = [
        f for f in os.listdir(VIDEOS_DIR)
        if f.lower().endswith(valid_exts) and not f.startswith(".")
    ]
    return sorted(files)


def select_dynamic_video(history, slot=None):
    """
    Selects a short video from assets/videos/ or returns None if no local video files exist.
    Tracks used videos in history to prevent repetition.
    """
    videos = get_available_videos()
    if not videos:
        return None, None

    used_videos = set(history.get("used_videos", []))
    unused_videos = [v for v in videos if v not in used_videos]
    if not unused_videos:
        unused_videos = videos
        history["used_videos"] = []

    chosen = random.choice(unused_videos)
    video_path = os.path.join(VIDEOS_DIR, chosen)
    return video_path, chosen


def generate_motion_video_from_image(image_path, output_mp4, duration=12, fps=30):
    """
    Transforms a static 1080x1920 image into a true cinematic 60/30fps motion video loop
    with continuous multi-axis camera tracking and subtle atmospheric breathing in FFmpeg.
    """
    total_frames = int(duration * fps)
    
    # Motion presets for image-to-video conversion
    pan_effects = [
        # Floating gentle pan and zoom
        f"zoompan=z='1.04+0.03*sin(2*3.14159*on/{total_frames})':d={total_frames}:x='iw/2-(iw/zoom/2)+15*sin(2*3.14159*on/{total_frames})':y='ih/2-(ih/zoom/2)+10*cos(2*3.14159*on/{total_frames})':s=1080x1920:fps={fps}",
        # Slow rising drone effect
        f"zoompan=z='min(1.0+0.00035*on,1.08)':d={total_frames}:x='iw/2-(iw/zoom/2)':y='max(0,ih/2-(ih/zoom/2)-0.12*on)':s=1080x1920:fps={fps}",
        # Slow descending tilt
        f"zoompan=z='min(1.0+0.00035*on,1.08)':d={total_frames}:x='iw/2-(iw/zoom/2)':y='min(ih-ih/zoom,ih/2-(ih/zoom/2)+0.12*on)':s=1080x1920:fps={fps}"
    ]
    chosen_effect = random.choice(pan_effects)
    
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-framerate", str(fps), "-t", str(duration), "-i", image_path,
        "-vf", f"scale=1080:1920,{chosen_effect}",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
        "-t", str(duration),
        output_mp4
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    return output_mp4


def prepare_looping_video_background(input_video, output_prepared_mp4, duration=12):
    """
    Prepares any input video (loops, trims to duration, and scales/crops to exact 1080x1920 9:16).
    """
    # Scale to fill 1080x1920 and center crop
    vf = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"
    cmd = [
        "ffmpeg", "-y",
        "-stream_loop", "-1", "-i", input_video,
        "-vf", vf,
        "-c:v", "libx264", "-preset", "fast", "-crf", "22", "-pix_fmt", "yuv420p",
        "-an",
        "-t", str(duration),
        output_prepared_mp4
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    return output_prepared_mp4
