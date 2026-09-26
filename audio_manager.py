import os
import sys
import math
import random
import struct
import wave

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(BASE_DIR, "assets", "audio")

# 8 Distinct Royalty-Free CC0 / Public Domain Music Tracks Catalog
AUDIO_CATALOG = {
    "lofi_chillhop.mp3": {
        "title": "Warm Rhodes & Lo-Fi Chillhop",
        "genre": "Lo-Fi Beats",
        "slots": ["evening", "afternoon"],
        "url": "https://raw.githubusercontent.com/uncle-sheepsky/duru-ai-cc0-bgm/main/mp3/duru-roomscene-lofi.mp3"
    },
    "boombap_groove.mp3": {
        "title": "Energetic 90s Boom-Bap Hip Hop",
        "genre": "Hip Hop / Motivation",
        "slots": ["morning", "midday"],
        "url": "https://raw.githubusercontent.com/uncle-sheepsky/duru-ai-cc0-bgm/main/mp3/korobeiniki-boombap-loop.mp3"
    },
    "cinematic_satie_piano.mp3": {
        "title": "Gymnopédie Serene Grand Piano",
        "genre": "Cinematic Piano",
        "slots": ["night", "morning"],
        "url": "https://upload.wikimedia.org/wikipedia/commons/2/20/Gymnopedie_No._2_%28ISRC_USUAN1100786%29.mp3"
    },
    "melodic_piano_rondo.mp3": {
        "title": "Uplifting Melodic Acoustic Rondo",
        "genre": "Acoustic Melody",
        "slots": ["morning", "midday"],
        "url": "https://raw.githubusercontent.com/uncle-sheepsky/duru-ai-cc0-bgm/main/mp3/duru-rondo.mp3"
    },
    "arcade_synthwave.mp3": {
        "title": "Retro Ambient Synthwave Vibe",
        "genre": "Synthwave / Cyber",
        "slots": ["midday", "evening"],
        "url": "https://raw.githubusercontent.com/uncle-sheepsky/duru-ai-cc0-bgm/main/mp3/duru-arcade-vibe.mp3"
    },
    "winter_celestial.mp3": {
        "title": "Celestial Chimes & Ambient Bells",
        "genre": "Ambient / Meditation",
        "slots": ["night", "evening"],
        "url": "https://raw.githubusercontent.com/uncle-sheepsky/duru-ai-cc0-bgm/main/mp3/duru-winter-arcade.mp3"
    },
    "stoic_mindset.mp3": {
        "title": "Stoic Cello & Deep Cinematic Pad",
        "genre": "Deep Wisdom",
        "slots": ["afternoon", "evening"],
        "url": "https://upload.wikimedia.org/wikipedia/commons/7/79/Stoic_Morning_%28ISRC_USUAN1100061%29.mp3"
    },
    "duru_tresillo_chill.mp3": {
        "title": "Dorian Tresillo Deep Flow",
        "genre": "Deep Focus",
        "slots": ["midday", "afternoon"],
        "url": "https://raw.githubusercontent.com/uncle-sheepsky/duru-ai-cc0-bgm/main/mp3/duru-ai-ep2-music.mp3"
    }
}

# Musical note to frequency helper (A4 = 440 Hz)
def m2f(note):
    return 440.0 * (2.0 ** ((note - 69.0) / 12.0))

# 8 Distinct Procedural Music Styles
MUSIC_STYLES = [
    {
        "id": "lofi_chill",
        "name": "Lo-Fi Chill & Warm Rhodes",
        "key": "Eb Major",
        "chords": [
            {"start": 0.0, "end": 4.0, "notes": [51, 55, 58, 62, 65], "bass": 39},   # Ebmaj9
            {"start": 4.0, "end": 8.0, "notes": [48, 55, 58, 62, 67], "bass": 36},   # Cm9
            {"start": 8.0, "end": 12.0, "notes": [49, 53, 56, 60, 65], "bass": 37}   # Fm9 -> Bb7
        ],
        "timbre": "rhodes"
    },
    {
        "id": "cinematic_piano",
        "name": "Cinematic Piano & Ambient Strings",
        "key": "D Major",
        "chords": [
            {"start": 0.0, "end": 4.0, "notes": [50, 57, 62, 66, 69], "bass": 38},   # Dmaj7
            {"start": 4.0, "end": 8.0, "notes": [47, 54, 59, 62, 66], "bass": 35},   # Bm7
            {"start": 8.0, "end": 12.0, "notes": [45, 52, 57, 61, 64], "bass": 33}   # Gmaj7 / A
        ],
        "timbre": "piano_strings"
    },
    {
        "id": "zen_meditation",
        "name": "Zen Meditation & Singing Bowl",
        "key": "F Lydian",
        "chords": [
            {"start": 0.0, "end": 4.0, "notes": [53, 60, 65, 67, 72], "bass": 41},   # F add9
            {"start": 4.0, "end": 8.0, "notes": [55, 60, 64, 67, 71], "bass": 43},   # C/G
            {"start": 8.0, "end": 12.0, "notes": [50, 57, 62, 65, 69], "bass": 38}   # Dm9
        ],
        "timbre": "singing_bowl"
    },
    {
        "id": "deep_focus_synth",
        "name": "Deep Focus & Warm Analog Pad",
        "key": "A Minor",
        "chords": [
            {"start": 0.0, "end": 4.0, "notes": [45, 52, 57, 60, 64], "bass": 33},   # Am7
            {"start": 4.0, "end": 8.0, "notes": [41, 48, 53, 57, 60], "bass": 29},   # Fmaj7
            {"start": 8.0, "end": 12.0, "notes": [43, 50, 55, 59, 62], "bass": 31}   # G6
        ],
        "timbre": "analog_pad"
    },
    {
        "id": "acoustic_plucks",
        "name": "Acoustic Pluck & Calming Harmonics",
        "key": "G Major",
        "chords": [
            {"start": 0.0, "end": 4.0, "notes": [55, 59, 62, 67, 71], "bass": 43},   # Gmaj7
            {"start": 4.0, "end": 8.0, "notes": [52, 55, 59, 64, 67], "bass": 40},   # Em7
            {"start": 8.0, "end": 12.0, "notes": [48, 55, 60, 64, 67], "bass": 36}   # Cmaj7
        ],
        "timbre": "acoustic_pluck"
    },
    {
        "id": "starlight_bells",
        "name": "Starlight Celeste & Celestial Pad",
        "key": "E Lydian",
        "chords": [
            {"start": 0.0, "end": 4.0, "notes": [52, 59, 63, 68, 71], "bass": 40},   # Emaj9
            {"start": 4.0, "end": 8.0, "notes": [49, 56, 61, 64, 68], "bass": 37},   # C#m7
            {"start": 8.0, "end": 12.0, "notes": [45, 52, 57, 61, 66], "bass": 33}   # A add9
        ],
        "timbre": "celeste_bells"
    },
    {
        "id": "morning_inspiration",
        "name": "Morning Inspiration & Bright Chimes",
        "key": "C Major",
        "chords": [
            {"start": 0.0, "end": 4.0, "notes": [48, 55, 59, 64, 67], "bass": 36},   # Cmaj9
            {"start": 4.0, "end": 8.0, "notes": [43, 50, 55, 59, 62], "bass": 31},   # G
            {"start": 8.0, "end": 12.0, "notes": [45, 52, 57, 60, 64], "bass": 33}   # Am7
        ],
        "timbre": "bright_chimes"
    },
    {
        "id": "sunset_chillhop",
        "name": "Sunset Chillhop & Gentle Vinyl Vibe",
        "key": "Bb Major",
        "chords": [
            {"start": 0.0, "end": 4.0, "notes": [46, 53, 57, 62, 65], "bass": 34},   # Bbmaj7
            {"start": 4.0, "end": 8.0, "notes": [50, 53, 57, 60, 65], "bass": 38},   # Dm7
            {"start": 8.0, "end": 12.0, "notes": [43, 50, 55, 58, 62], "bass": 31}   # Gm7
        ],
        "timbre": "sunset_vibe"
    }
]


def synthesize_style_audio(style_data, output_wav, duration=12.0, sample_rate=44100):
    """
    Synthesizes rich, multi-layered stereo audio for a given musical style
    with natural harmonics, stereo widening, and smooth envelope fades.
    """
    try:
        import numpy as np
        import scipy.io.wavfile as wavfile
        return _synthesize_numpy(style_data, output_wav, duration, sample_rate, np, wavfile)
    except ImportError:
        return _synthesize_pure_python(style_data, output_wav, duration, sample_rate)


def _synthesize_numpy(style_data, output_wav, duration, sample_rate, np, wavfile):
    num_samples = int(duration * sample_rate)
    left = np.zeros(num_samples, dtype=np.float32)
    right = np.zeros(num_samples, dtype=np.float32)
    
    chords = style_data["chords"]
    timbre = style_data.get("timbre", "rhodes")

    for c in chords:
        s_idx = int(c["start"] * sample_rate)
        e_idx = min(num_samples, int((c["end"] + 1.2) * sample_rate))
        seg_len = e_idx - s_idx
        dur = seg_len / sample_rate
        t_seg = np.linspace(0, dur, seg_len, endpoint=False)
        
        # Smooth attack & release envelope
        env = np.ones(seg_len, dtype=np.float32)
        att = min(seg_len // 3, int(1.1 * sample_rate))
        rel = min(seg_len // 3, int(1.2 * sample_rate))
        env[:att] = np.sin(np.linspace(0, np.pi / 2, att))
        env[-rel:] = np.cos(np.linspace(0, np.pi / 2, rel))
        
        c_l = np.zeros_like(t_seg)
        c_r = np.zeros_like(t_seg)

        for i, note in enumerate(c["notes"]):
            freq = m2f(note)
            pan = (i / max(1, len(c["notes"]) - 1)) * 0.6 + 0.2
            
            if timbre == "rhodes":
                # Warm electric piano with subtle tremolo
                tremolo = 1.0 + 0.15 * np.sin(2 * np.pi * 4.5 * t_seg)
                tone = (0.75 * np.sin(2 * np.pi * freq * t_seg) +
                        0.20 * np.sin(4 * np.pi * freq * t_seg) +
                        0.05 * np.sin(6 * np.pi * freq * t_seg)) * tremolo
            elif timbre == "singing_bowl":
                # Resonant acoustic beating (~8Hz alpha frequency)
                tone = (0.65 * np.sin(2 * np.pi * freq * t_seg) +
                        0.35 * np.sin(2 * np.pi * (freq + 7.5) * t_seg) +
                        0.10 * np.sin(6 * np.pi * freq * t_seg))
            elif timbre == "piano_strings":
                # Expressive piano attack + swelling string harmonics
                decay = np.exp(-t_seg * 0.9)
                piano = (0.7 * np.sin(2 * np.pi * freq * t_seg) + 0.3 * np.sin(4 * np.pi * freq * t_seg)) * decay
                strings = (0.5 * np.sin(2 * np.pi * freq * 1.002 * t_seg) + 0.25 * np.sin(4 * np.pi * freq * t_seg)) * (1.0 - decay * 0.4)
                tone = piano * 0.6 + strings * 0.5
            elif timbre == "analog_pad":
                # Detuned analog sawtooth-like warm pad
                tone = (0.5 * np.sin(2 * np.pi * freq * 0.998 * t_seg) +
                        0.5 * np.sin(2 * np.pi * freq * 1.002 * t_seg) +
                        0.2 * np.sin(4 * np.pi * freq * t_seg))
            elif timbre == "celeste_bells":
                # Sparkling bells with quick chime overtone
                decay = np.exp(-t_seg * 1.4)
                tone = (0.6 * np.sin(2 * np.pi * freq * t_seg) +
                        0.3 * np.sin(4 * np.pi * freq * t_seg) +
                        0.2 * np.sin(8 * np.pi * freq * t_seg)) * decay
            elif timbre == "bright_chimes":
                # Shimmering major chimes
                tone = (0.6 * np.sin(2 * np.pi * freq * t_seg) +
                        0.3 * np.sin(3 * np.pi * freq * t_seg) +
                        0.15 * np.sin(5 * np.pi * freq * t_seg))
            else:
                # Default acoustic pluck / warm tone
                decay = np.exp(-t_seg * 1.1)
                tone = (0.7 * np.sin(2 * np.pi * freq * t_seg) + 0.3 * np.sin(4 * np.pi * freq * t_seg)) * decay

            c_l += tone * (1.0 - pan)
            c_r += tone * pan

        # Grounding sub-bass root note
        root_f = m2f(c["bass"])
        sub = 0.5 * np.sin(2 * np.pi * root_f * t_seg)
        c_l += sub * 0.38
        c_r += sub * 0.38

        left[s_idx:e_idx] += c_l * env * 0.24
        right[s_idx:e_idx] += c_r * env * 0.24

    # Master Fade In & Fade Out
    fade_len = int(1.4 * sample_rate)
    left[:fade_len] *= np.linspace(0, 1, fade_len)
    right[:fade_len] *= np.linspace(0, 1, fade_len)
    left[-fade_len:] *= np.linspace(1, 0, fade_len)
    right[-fade_len:] *= np.linspace(1, 0, fade_len)

    # Master Normalization
    peak = max(np.max(np.abs(left)), np.max(np.abs(right)), 0.001)
    left = (left / peak) * 0.86
    right = (right / peak) * 0.86

    stereo = np.stack([left, right], axis=1)
    os.makedirs(os.path.dirname(os.path.abspath(output_wav)), exist_ok=True)
    wavfile.write(output_wav, sample_rate, (stereo * 32767.0).astype(np.int16))
    return output_wav


def _synthesize_pure_python(style_data, output_wav, duration, sample_rate):
    """Fallback standard-library synthesizer if numpy is unavailable."""
    num_samples = int(duration * sample_rate)
    left = [0.0] * num_samples
    right = [0.0] * num_samples
    
    chords = style_data["chords"]
    timbre = style_data.get("timbre", "rhodes")

    for c in chords:
        s_idx = int(c["start"] * sample_rate)
        e_idx = min(num_samples, int((c["end"] + 1.2) * sample_rate))
        seg_len = e_idx - s_idx
        
        att = min(seg_len // 3, int(1.1 * sample_rate))
        rel = min(seg_len // 3, int(1.2 * sample_rate))
        
        root_f = m2f(c["bass"])

        for j in range(seg_len):
            idx = s_idx + j
            t = j / sample_rate
            
            # Envelope
            if j < att:
                env = math.sin((j / att) * (math.pi / 2.0))
            elif j > seg_len - rel:
                env = math.cos(((j - (seg_len - rel)) / rel) * (math.pi / 2.0))
            else:
                env = 1.0

            c_l, c_r = 0.0, 0.0
            for i, note in enumerate(c["notes"]):
                freq = m2f(note)
                pan = (i / max(1, len(c["notes"]) - 1)) * 0.6 + 0.2
                
                # Harmonic tone
                decay = math.exp(-t * 0.8) if timbre in ["piano_strings", "celeste_bells", "acoustic_pluck"] else 1.0
                tone = (0.7 * math.sin(2 * math.pi * freq * t) + 0.3 * math.sin(4 * math.pi * freq * t)) * decay
                c_l += tone * (1.0 - pan)
                c_r += tone * pan

            sub = 0.5 * math.sin(2 * math.pi * root_f * t)
            c_l += sub * 0.38
            c_r += sub * 0.38

            left[idx] += c_l * env * 0.24
            right[idx] += c_r * env * 0.24

    fade_len = int(1.4 * sample_rate)
    for i in range(fade_len):
        f = i / fade_len
        left[i] *= f
        right[i] *= f
    for i in range(fade_len):
        f = (fade_len - i) / fade_len
        idx = num_samples - fade_len + i
        left[idx] *= f
        right[idx] *= f

    peak = max(max(abs(x) for x in left), max(abs(x) for x in right), 0.001)
    norm = 0.86 / peak

    os.makedirs(os.path.dirname(os.path.abspath(output_wav)), exist_ok=True)
    with wave.open(output_wav, "wb") as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        frames = bytearray()
        for i in range(num_samples):
            l_val = int(max(min(left[i] * norm * 32767.0, 32767.0), -32768.0))
            r_val = int(max(min(right[i] * norm * 32767.0, 32767.0), -32768.0))
            frames.extend(struct.pack("<hh", l_val, r_val))
        wav.writeframes(frames)

    return output_wav


def get_available_audio_files():
    """Returns list of user-provided or starter audio files in assets/audio/"""
    if not os.path.exists(AUDIO_DIR):
        os.makedirs(AUDIO_DIR, exist_ok=True)
        return []
    valid_exts = (".wav", ".mp3", ".m4a", ".ogg")
    files = [
        f for f in os.listdir(AUDIO_DIR)
        if f.lower().endswith(valid_exts) and not f.startswith(".")
    ]
    return sorted(files)


def select_dynamic_audio(history, quote_slot=None, output_temp_wav=None):
    """
    Selects a distinct, high-quality audio track for the reel.
    1. Checks if real audio files exist in assets/audio/ (auto-populates if missing)
    2. Strictly avoids repeating recent tracks from history['used_audio']
    3. Guarantees that the last-posted audio track is NEVER repeated consecutively
    4. Matches slot mood (morning=uplifting/boom-bap, evening/night=lo-fi/piano/ambient)
    Returns: (audio_path, audio_display_name, audio_id)
    """
    if history is None:
        history = {}

    audio_files = get_available_audio_files()
    if not audio_files:
        populate_starter_audio_library()
        audio_files = get_available_audio_files()

    # Mode A: User / Starter library has real audio files in assets/audio/
    if audio_files:
        used_audio = history.get("used_audio", [])
        
        # Filter used_audio to only keep tracks that currently exist in assets/audio/
        valid_used = [f for f in used_audio if f in audio_files]
        last_track = valid_used[-1] if valid_used else None

        # Tracks unused in the current cycle
        unused_files = [f for f in audio_files if f not in valid_used]

        # If all tracks have been used at least once, reset cycle
        if not unused_files:
            unused_files = list(audio_files)

        # STRICT NON-REPETITION: Never pick the track that was just posted
        if len(unused_files) > 1 and last_track in unused_files:
            unused_files.remove(last_track)

        # Slot-based affinity matching if slot is provided
        slot_candidates = []
        if quote_slot:
            slot_candidates = [
                f for f in unused_files
                if quote_slot in AUDIO_CATALOG.get(f, {}).get("slots", [])
            ]

        # Pick with 75% affinity for slot mood, or fallback to any unused track
        if slot_candidates and random.random() < 0.75:
            chosen_file = random.choice(slot_candidates)
        else:
            chosen_file = random.choice(unused_files)

        audio_path = os.path.join(AUDIO_DIR, chosen_file)
        catalog_info = AUDIO_CATALOG.get(chosen_file, {})
        display_name = catalog_info.get("title") or os.path.splitext(chosen_file)[0].replace("_", " ").title()
        
        return audio_path, display_name, chosen_file

    # Mode B: High-Fidelity Procedural Synthesis Fallback (if completely offline & empty)
    used_styles = history.get("used_audio", [])
    unused_styles = [s for s in MUSIC_STYLES if s["id"] not in used_styles]
    if not unused_styles:
        unused_styles = MUSIC_STYLES
        used_styles = []

    chosen_style = random.choice(unused_styles)
    if not output_temp_wav:
        temp_dir = os.path.join(BASE_DIR, "output", "temp")
        os.makedirs(temp_dir, exist_ok=True)
        output_temp_wav = os.path.join(temp_dir, f"audio_{chosen_style['id']}.wav")

    synthesize_style_audio(chosen_style, output_temp_wav, duration=15.0)
    return output_temp_wav, chosen_style["name"], chosen_style["id"]


def populate_starter_audio_library():
    """
    Ensures the audio library in assets/audio/ is populated with genuine, high-quality
    royalty-free CC0 and public domain audio tracks.
    Auto-downloads missing tracks from direct reliable URLs.
    """
    import urllib.request
    os.makedirs(AUDIO_DIR, exist_ok=True)
    existing = get_available_audio_files()
    
    missing = [f for f in AUDIO_CATALOG.keys() if f not in existing]
    if not missing:
        return

    print(f"[INFO] Populating audio library ({len(missing)} tracks to acquire)...")
    headers = {"User-Agent": "Mozilla/5.0 (Instagram Auto Poster Bot)"}
    
    for fname in missing:
        url = AUDIO_CATALOG[fname].get("url")
        if not url:
            continue
        dest = os.path.join(AUDIO_DIR, fname)
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=20) as resp, open(dest, "wb") as f:
                f.write(resp.read())
            print(f"  ✓ Downloaded {fname}: {AUDIO_CATALOG[fname]['title']}")
        except Exception as e:
            print(f"  [WARN] Failed to download {fname}: {e}")

    # Offline emergency fallback: if no audio files could be acquired
    if not get_available_audio_files():
        print("[WARN] Offline: generating procedural fallback tracks...")
        for style in MUSIC_STYLES[:4]:
            out_name = f"{style['id']}.wav"
            target_path = os.path.join(AUDIO_DIR, out_name)
            if not os.path.exists(target_path):
                synthesize_style_audio(style, target_path, duration=15.0)
                print(f"  + Generated: {out_name}")


if __name__ == "__main__":
    populate_starter_audio_library()
    print("Available audio files:", get_available_audio_files())
