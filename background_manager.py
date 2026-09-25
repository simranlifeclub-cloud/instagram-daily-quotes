import os
import random
import urllib.request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BG_DIR = os.path.join(BASE_DIR, "assets", "backgrounds")
DEFAULT_BG = os.path.join(BG_DIR, "serene_sunrise.jpg")

SLOT_BG_PREFERENCES = {
    "morning": [
        "golden_mountain.jpg",
        "misty_forest.jpg",
        "serene_sunrise.jpg",
        "emerald_waterfall.jpg"
    ],
    "midday": [
        "ocean_waves.jpg",
        "minimalist_arch.jpg",
        "emerald_waterfall.jpg",
        "desert_dunes.jpg"
    ],
    "afternoon": [
        "desert_dunes.jpg",
        "ocean_waves.jpg",
        "minimalist_arch.jpg",
        "golden_mountain.jpg"
    ],
    "evening": [
        "city_twilight.jpg",
        "desert_dunes.jpg",
        "golden_mountain.jpg",
        "starry_night.jpg"
    ],
    "night": [
        "starry_night.jpg",
        "city_twilight.jpg",
        "misty_forest.jpg"
    ]
}


def get_available_backgrounds():
    """Returns list of image filenames in assets/backgrounds/"""
    if not os.path.exists(BG_DIR):
        os.makedirs(BG_DIR, exist_ok=True)
        return []
    valid_exts = (".jpg", ".jpeg", ".png", ".webp")
    files = [
        f for f in os.listdir(BG_DIR)
        if f.lower().endswith(valid_exts) and not f.startswith(".")
    ]
    return sorted(files)


def fetch_fresh_online_background(slot="morning", timeout=4):
    """
    Optional online fetcher: pulls a fresh royalty-free 9:16 vertical HD photo
    from Unsplash with strict timeout. Falls back immediately on any error.
    """
    slot_keywords = {
        "morning": ["sunrise", "misty-mountains", "foggy-forest", "golden-hour"],
        "midday": ["ocean-cliff", "modern-architecture", "clean-nature", "waterfall"],
        "afternoon": ["desert-dunes", "canyon", "skyline-clouds", "golden-sand"],
        "evening": ["city-twilight", "sunset-horizon", "blue-hour-street", "dusk"],
        "night": ["starry-night-sky", "milky-way", "dark-water-reflection", "neon-night"]
    }
    kw = random.choice(slot_keywords.get(slot, ["nature", "landscape", "calm"]))
    query_url = f"https://source.unsplash.com/1080x1920/?{kw}"
    try:
        req = urllib.request.Request(query_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            content = resp.read()
            if len(content) > 50000:
                filename = f"online_{slot}_{random.randint(1000, 9999)}.jpg"
                target_path = os.path.join(BG_DIR, filename)
                with open(target_path, "wb") as f:
                    f.write(content)
                print(f"[INFO] Downloaded fresh online background: {filename} (Theme: {kw})")
                return target_path, filename
    except Exception:
        pass
    return None


def select_dynamic_background(history, slot=None, allow_online=False):
    """
    Selects a fresh background that has not been used recently.
    - Honors time-of-day slot atmosphere
    - Ensures no consecutive repetitions
    - Resets rotation cycle once all backgrounds have been shown
    """
    all_bgs = get_available_backgrounds()
    if not all_bgs:
        if os.path.exists(DEFAULT_BG):
            return DEFAULT_BG, os.path.basename(DEFAULT_BG)
        return None, None

    used_bgs = set(history.get("used_backgrounds", []))

    # 1. Optionally try fetching a new online photo if enabled
    if allow_online:
        online_result = fetch_fresh_online_background(slot=slot or "morning")
        if online_result:
            return online_result

    # 2. Check preferred backgrounds for current slot
    if slot and slot in SLOT_BG_PREFERENCES:
        slot_candidates = [
            bg for bg in SLOT_BG_PREFERENCES[slot]
            if bg in all_bgs and bg not in used_bgs
        ]
        if slot_candidates:
            chosen = random.choice(slot_candidates)
            return os.path.join(BG_DIR, chosen), chosen

    # 3. If slot preferences exhausted, pick any unposted background
    unused_bgs = [bg for bg in all_bgs if bg not in used_bgs]
    if unused_bgs:
        chosen = random.choice(unused_bgs)
        return os.path.join(BG_DIR, chosen), chosen

    # 4. If all backgrounds have been posted, reset rotation cycle
    print("[INFO] Full library of backgrounds cycled! Resetting background rotation.")
    history["used_backgrounds"] = []
    chosen = random.choice(all_bgs)
    return os.path.join(BG_DIR, chosen), chosen


if __name__ == "__main__":
    sample_history = {"used_backgrounds": []}
    for s in ["morning", "midday", "afternoon", "evening", "night"]:
        path, name = select_dynamic_background(sample_history, slot=s)
        sample_history["used_backgrounds"].append(name)
        print(f"Slot [{s:9s}]: {name}")
