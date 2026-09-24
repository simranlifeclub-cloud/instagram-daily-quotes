import os
import sys
import json
import time
import random
import argparse
import shutil
from datetime import datetime, timezone, timedelta

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


def get_current_ist_slot():
    ist_tz = timezone(timedelta(hours=5, minutes=30))
    now_ist = datetime.now(ist_tz)
    hour = now_ist.hour
    
    if 5 <= hour < 10:
        return "morning"
    elif 10 <= hour < 13:
        return "midday"
    elif 13 <= hour < 17:
        return "afternoon"
    elif 17 <= hour < 21:
        return "evening"
    else:
        return "night"


def select_dynamic_quote(quotes, history):
    posted_ids = set(history.get("posted_ids", []))
    current_slot = get_current_ist_slot()
    
    slot_available = [q for q in quotes if q.get("slot") == current_slot and q["id"] not in posted_ids]
    if slot_available:
        selected = random.choice(slot_available)
        print(f"[INFO] Selected '{current_slot}' slot quote #{selected['id']}.")
        return selected

    general_available = [q for q in quotes if q["id"] not in posted_ids]
    if general_available:
        selected = random.choice(general_available)
        print(f"[INFO] Slot exhausted. Selected general unposted quote #{selected['id']}.")
        return selected

    print("[INFO] Full library of quotes has been published! Resetting rotation cycle.")
    history["posted_ids"] = []
    return random.choice(quotes)


def get_authenticated_client(username, password):
    from instagrapi import Client
    cl = Client()
    cl.delay_range = [2, 5]

    # Configure modern device settings to avoid 'version out of date' errors
    cl.set_country("IN")
    cl.set_locale("en_IN")
    cl.set_timezone_offset(int(5.5 * 3600))
    cl.set_user_agent(
        "Instagram 340.0.0.38.109 Android (33/13; 420dpi; 1080x2400; Xiaomi; M2101K6G; sweet; qcom; en_US; 618585954)"
    )

    # 1. Check if direct sessionid cookie is provided (Bypasses all app version checks!)
    sessionid = os.getenv("IG_SESSIONID")
    if sessionid:
        try:
            print("[INFO] Attempting authentication via IG_SESSIONID cookie...")
            cl.login_by_sessionid(sessionid.strip())
            print("[SUCCESS] Authenticated cleanly via session ID!")
            return cl
        except Exception as e:
            print(f"[WARN] Session ID login failed: {e}. Trying username/password...")

    # 2. Check saved session from env
    session_env = os.getenv("IG_SESSION_DATA")
    if session_env:
        try:
            cl.set_settings(json.loads(session_env))
            cl.login(username, password)
            print("[SUCCESS] Authenticated via IG_SESSION_DATA.")
            return cl
        except Exception as e:
            print(f"[WARN] IG_SESSION_DATA error: {e}")

    # 3. Check saved session from local file
    if os.path.exists(SESSION_FILE):
        try:
            cl.load_settings(SESSION_FILE)
            cl.login(username, password)
            print("[SUCCESS] Authenticated via session.json.")
            return cl
        except Exception as e:
            print(f"[WARN] session.json error: {e}")

    # 4. Standard Username & Password Login
    print(f"[INFO] Logging in with modern CAA flow as: {username}...")
    try:
        cl.login(username, password)
        print("[SUCCESS] Successfully logged into Instagram!")
    except Exception as e:
        err_str = str(e)
        if "out of date" in err_str.lower() or "upgrade your app" in err_str.lower():
            print("[WARN] Encountered version warning, refreshing device profile and retrying...")
            cl.set_user_agent("Instagram 350.0.0.42.92 Android (34/14; 480dpi; 1080x2340; samsung; SM-S911B; dm1q; qcom; en_US; 634918239)")
            cl.login(username, password)
            print("[SUCCESS] Successfully logged in on retry!")
        else:
            raise e

    try:
        cl.dump_settings(SESSION_FILE)
    except Exception:
        pass

    return cl


def main():
    parser = argparse.ArgumentParser(description="Instagram Daily Reel & Post Publisher")
    parser.add_argument("--dry-run", action="store_true", help="Render video/image without uploading")
    parser.add_argument("--no-jitter", action="store_true", help="Disable human posting time jitter")
    args = parser.parse_args()

    username = os.getenv("IG_USERNAME")
    password = os.getenv("IG_PASSWORD")
    sessionid = os.getenv("IG_SESSIONID")

    # Add random organic delay (1 to 8 minutes) unless disabled
    if not args.dry_run and not args.no_jitter:
        jitter_seconds = random.randint(60, 480)
        print(f"[INFO] Adding natural human jitter: waiting {jitter_seconds // 60}m {jitter_seconds % 60}s before publishing...")
        time.sleep(jitter_seconds)

    quotes = load_quotes()
    history = load_history()
    quote = select_dynamic_quote(quotes, history)

    print("\n=======================================================")
    print(f" Daily Motivational Reel: #{quote['id']} [{quote.get('slot', 'general').upper()}]")
    print(f" Category: {quote['category']}")
    print("=======================================================")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    caption = quote["caption"]

    has_ffmpeg = shutil.which("ffmpeg") is not None
    
    if has_ffmpeg:
        from video_reel_generator import build_mp4_reel
        media_path = os.path.join(OUTPUT_DIR, f"daily_reel_{quote['id']}.mp4")
        build_mp4_reel(quote, media_path, duration=12)
        is_video = True
    else:
        from card_renderer import render_quote_card
        media_path = os.path.join(OUTPUT_DIR, f"daily_post_{quote['id']}.jpg")
        render_quote_card(quote, media_path, DEFAULT_BG)
        is_video = False

    if args.dry_run:
        print("\n[DRY RUN MODE]")
        print("Media file:", media_path)
        print("Format:", "Instagram REEL (MP4 Video)" if is_video else "Instagram PHOTO (JPEG)")
        print("Time Slot:", quote.get("slot"))
        print("Caption preview:\n", caption)
        print("\nReady! Set IG_USERNAME and IG_PASSWORD in GitHub Secrets to post live.")
        return

    if not sessionid and (not username or not password):
        print("\n[ERROR] Missing Instagram credentials!")
        print("Please set IG_USERNAME & IG_PASSWORD (or IG_SESSIONID) in GitHub Secrets.")
        sys.exit(1)

    cl = get_authenticated_client(username, password)

    if is_video:
        print(f"[INFO] Uploading MP4 Reel to Instagram...")
        media = cl.clip_upload(path=media_path, caption=caption)
        print(f"\n🎉 [SUCCESS] REEL is LIVE on Instagram! Reel PK: {media.pk}")
    else:
        print(f"[INFO] Uploading Photo to Instagram Feed...")
        media = cl.photo_upload(path=media_path, caption=caption)
        print(f"\n🎉 [SUCCESS] Post is LIVE on Instagram! Media PK: {media.pk}")

    history["posted_ids"].append(quote["id"])
    history["last_posted_date"] = time.strftime("%Y-%m-%d %H:%M:%S UTC")
    save_history(history)
    print(f"[INFO] Recorded quote #{quote['id']} in posting history. Will not repeat!")


if __name__ == "__main__":
    main()
