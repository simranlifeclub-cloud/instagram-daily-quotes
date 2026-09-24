import os
import sys
import json
import time
import argparse
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
QUOTES_FILE = os.path.join(BASE_DIR, "quotes_database.json")
HISTORY_FILE = os.path.join(BASE_DIR, "history.json")
SESSION_FILE = os.path.join(BASE_DIR, "session.json")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
DEFAULT_BG = os.path.join(BASE_DIR, "assets", "backgrounds", "serene_sunrise.jpg")


def load_quotes():
    if not os.path.exists(QUOTES_FILE):
        raise FileNotFoundError(f"Quotes file not found at: {QUOTES_FILE}")
    with open(QUOTES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"posted_ids": [], "last_posted_date": None}
    return {"posted_ids": [], "last_posted_date": None}


def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)


def select_daily_quote(quotes, history):
    posted_ids = set(history.get("posted_ids", []))
    available = [q for q in quotes if q["id"] not in posted_ids]
    if not available:
        print("[INFO] All quotes have been posted! Resetting cycle for fresh rotation.")
        history["posted_ids"] = []
        available = quotes
    return available[0]


def get_authenticated_client(username, password):
    from instagrapi import Client
    cl = Client()
    cl.delay_range = [2, 5]

    # 1. Load session from env if provided
    session_env = os.getenv("IG_SESSION_DATA")
    if session_env:
        try:
            print("[INFO] Loading Instagram session from IG_SESSION_DATA secret...")
            cl.set_settings(json.loads(session_env))
            cl.login(username, password)
            print("[SUCCESS] Session authenticated via IG_SESSION_DATA.")
            return cl
        except Exception as e:
            print(f"[WARN] Failed to use IG_SESSION_DATA: {e}")

    # 2. Load session from local file if exists
    if os.path.exists(SESSION_FILE):
        try:
            print("[INFO] Loading Instagram session from session.json...")
            cl.load_settings(SESSION_FILE)
            cl.login(username, password)
            print("[SUCCESS] Session authenticated via session.json.")
            return cl
        except Exception as e:
            print(f"[WARN] Failed to load session.json: {e}")

    # 3. Standard Login
    print(f"[INFO] Logging into Instagram as: {username}...")
    cl.login(username, password)
    print("[SUCCESS] Successfully logged into Instagram!")

    try:
        cl.dump_settings(SESSION_FILE)
        print(f"[INFO] Saved session to {SESSION_FILE}")
    except Exception as e:
        print(f"[WARN] Could not dump session: {e}")

    return cl


def main():
    parser = argparse.ArgumentParser(description="Instagram Daily Reel & Post Publisher")
    parser.add_argument("--dry-run", action="store_true", help="Render video/image without uploading")
    parser.add_argument("--force-photo", action="store_true", help="Force static photo upload instead of Reel")
    args = parser.parse_args()

    username = os.getenv("IG_USERNAME")
    password = os.getenv("IG_PASSWORD")

    quotes = load_quotes()
    history = load_history()
    quote = select_daily_quote(quotes, history)

    print("\n=======================================================")
    print(f" Daily Motivational Reel: #{quote['id']} - {quote['category']}")
    print("=======================================================")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    caption = quote["caption"]

    # Check if ffmpeg is available for generating MP4 Reel
    has_ffmpeg = shutil.which("ffmpeg") is not None
    is_reel = has_ffmpeg and not args.force_photo

    if is_reel:
        from video_reel_generator import build_mp4_reel
        media_path = os.path.join(OUTPUT_DIR, f"daily_reel_{quote['id']}.mp4")
        build_mp4_reel(quote, media_path, duration=12, bg_path=DEFAULT_BG)
        print(f"[INFO] 12-second MP4 Reel successfully generated: {media_path}")
    else:
        from card_renderer import render_quote_card
        media_path = os.path.join(OUTPUT_DIR, f"daily_post_{quote['id']}.jpg")
        render_quote_card(quote, media_path, DEFAULT_BG)
        print(f"[INFO] Image card rendered: {media_path}")

    if args.dry_run:
        print("\n[DRY RUN MODE]")
        print("Media file:", media_path)
        print("Type:", "Instagram REEL (Video)" if is_reel else "Instagram PHOTO")
        print("Caption preview:\n", caption)
        print("\nReady! Set IG_USERNAME and IG_PASSWORD in GitHub Secrets to post live.")
        return

    if not username or not password:
        print("\n[ERROR] Missing Instagram credentials!")
        print("Please set IG_USERNAME and IG_PASSWORD in your GitHub Repository Secrets.")
        sys.exit(1)

    cl = get_authenticated_client(username, password)

    if is_reel:
        print(f"[INFO] Uploading MP4 video to Instagram REELS...")
        media = cl.clip_upload(
            path=media_path,
            caption=caption
        )
        print(f"\n🎉 [SUCCESS] REEL is LIVE on Instagram! Reel PK: {media.pk}")
    else:
        print(f"[INFO] Uploading Photo to Instagram Feed...")
        media = cl.photo_upload(
            path=media_path,
            caption=caption
        )
        print(f"\n🎉 [SUCCESS] Post is LIVE on Instagram! Media PK: {media.pk}")

    history["posted_ids"].append(quote["id"])
    history["last_posted_date"] = time.strftime("%Y-%m-%d %H:%M:%S UTC")
    save_history(history)
    print(f"[INFO] Recorded quote #{quote['id']} in posting history.")


if __name__ == "__main__":
    main()
