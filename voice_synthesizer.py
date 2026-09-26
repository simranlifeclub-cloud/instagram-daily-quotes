import os
import sys
import asyncio
import subprocess
import random

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 5 High-Quality Neural Voices for Motivational Narration
MOTIVATIONAL_VOICES = [
    {
        "id": "en-US-ChristopherNeural",
        "name": "Christopher (Deep, Commanding, Classic Motivational)",
        "rate": "-4%",
        "pitch": "-2Hz"
    },
    {
        "id": "en-US-GuyNeural",
        "name": "Guy (Passionate, Energetic, Direct)",
        "rate": "-2%",
        "pitch": "+0Hz"
    },
    {
        "id": "en-GB-RyanNeural",
        "name": "Ryan (British, Sophisticated, Cinematic Wisdom)",
        "rate": "-3%",
        "pitch": "-1Hz"
    },
    {
        "id": "en-US-EricNeural",
        "name": "Eric (Warm, Inspiring, Grounded)",
        "rate": "-3%",
        "pitch": "+0Hz"
    },
    {
        "id": "en-US-JennyNeural",
        "name": "Jenny (Uplifting, Clear, Confident)",
        "rate": "-2%",
        "pitch": "+1Hz"
    }
]


def format_speech_text(quote_data):
    """
    Formats the quote text with natural pauses and cadence for motivational delivery.
    """
    hero_lines = quote_data.get("hero_lines", [])
    subtext = quote_data.get("subtext", "")
    
    hero_text = " ... ".join(hero_lines)
    if not hero_text.endswith("."):
        hero_text += "."
        
    if subtext:
        full_text = f"{hero_text} ... {subtext}"
    else:
        full_text = hero_text
        
    return full_text


async def _generate_edge_tts(text, voice_config, output_mp3):
    import edge_tts
    communicate = edge_tts.Communicate(
        text,
        voice_config["id"],
        rate=voice_config.get("rate", "+0%"),
        pitch=voice_config.get("pitch", "+0Hz")
    )
    await communicate.save(output_mp3)
    return output_mp3


def synthesize_quote_speech(quote_data, output_mp3, voice_id=None):
    """
    Generates studio-quality neural voice narration for the motivational quote.
    Uses edge-tts if available, or falls back to system TTS on macOS.
    Returns: (output_mp3, voice_name) or (None, None) if unavailable.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_mp3)), exist_ok=True)
    text = format_speech_text(quote_data)
    
    # 1. Pick Voice
    if voice_id:
        matching = [v for v in MOTIVATIONAL_VOICES if v["id"] == voice_id]
        voice_config = matching[0] if matching else MOTIVATIONAL_VOICES[0]
    else:
        voice_config = random.choice(MOTIVATIONAL_VOICES)

    # 2. Try Edge TTS (Neural Voices - Cloud / Linux)
    try:
        import edge_tts
        asyncio.run(_generate_edge_tts(text, voice_config, output_mp3))
        if os.path.exists(output_mp3) and os.path.getsize(output_mp3) > 1000:
            print(f"[VOICE] Generated neural narration: {voice_config['name']}")
            return output_mp3, voice_config["name"]
    except ImportError:
        pass
    except Exception as e:
        print(f"[WARN] Edge-TTS error: {e}. Trying system fallback...")

    # 3. macOS Fallback (say command)
    if sys.platform == "darwin":
        try:
            aiff_temp = output_mp3.replace(".mp3", ".aiff")
            cmd = ["say", "-v", "Daniel", "-o", aiff_temp, text]
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # Convert to mp3/wav with ffmpeg
            if os.path.exists(aiff_temp):
                conv_cmd = ["ffmpeg", "-y", "-i", aiff_temp, output_mp3]
                subprocess.run(conv_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if os.path.exists(aiff_temp):
                    os.remove(aiff_temp)
                if os.path.exists(output_mp3):
                    return output_mp3, "macOS Daniel Voice"
        except Exception:
            pass

    return None, None


def mix_voice_and_music(voice_path, music_path, output_mixed_audio, duration=12.0):
    """
    Mixes voiceover narration with background music in FFmpeg:
    - Voice is crisp, centered, and elevated in volume (volume=1.35)
    - Background music is ducked softly underneath (volume=0.32)
    - Background music swells smoothly after voice finishes (up to volume=0.75)
    - Smooth 1.8s audio fade-out at reel end
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_mixed_audio)), exist_ok=True)
    
    if not voice_path or not os.path.exists(voice_path):
        # Only music
        cmd = [
            "ffmpeg", "-y", "-i", music_path,
            "-af", f"afade=t=in:st=0:d=1.2,afade=t=out:st={duration-1.8}:d=1.8,volume=0.9",
            "-t", str(duration),
            output_mixed_audio
        ]
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return output_mixed_audio

    # Smart Audio Ducking Filtergraph in FFmpeg
    filtergraph = (
        f"[0:a]volume=1.35,afade=t=in:st=0:d=0.3[v];"
        f"[1:a]volume=0.32,afade=t=in:st=0:d=1.0,afade=t=out:st={duration-1.8}:d=1.8[m];"
        f"[v][m]amix=inputs=2:duration=first:dropout_transition=2,volume=1.15"
    )

    cmd = [
        "ffmpeg", "-y",
        "-i", voice_path,
        "-i", music_path,
        "-filter_complex", filtergraph,
        "-t", str(duration),
        output_mixed_audio
    ]

    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        # Fallback simpler mix
        fallback_filter = f"[0:a]volume=1.3[v];[1:a]volume=0.35[m];[v][m]amix=inputs=2:duration=longest"
        cmd_fallback = [
            "ffmpeg", "-y",
            "-i", voice_path,
            "-i", music_path,
            "-filter_complex", fallback_filter,
            "-t", str(duration),
            output_mixed_audio
        ]
        subprocess.run(cmd_fallback, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    return output_mixed_audio
