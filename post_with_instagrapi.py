import os
import sys
import json
import time
import argparse
from card_renderer import render_quote_card

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
    """
    Initializes and authenticates the instagrapi Client.
    Uses saved session if available to avoid triggering login challenges.
    """
    from instagrapi import Client
    cl = Client()
    cl.delay_range = [2, 5]

    # 1. Try loading session from environment secret
    session_env = os.getenv("IG_SESSION_DATA")
    if session_env:
        try:
            print("[INFO] Loading Instagram session from IG_SESSION_DATA secret...")
            cl.set_settings(json.loads(session_env))
            cl.login(username, password)
            print("[SUCCESS] Session authenticated via IG_SESSION_DATA.")
            return cl
        except Exception as e:
            print(f"[WARN] Failed to use IG_SESSION_DATA: {e}. Falling back to standard login...")

    # 2. Try loading session from local file
    if os.path.exists(SESSION_FILE):
        try:
            print("[INFO] Loading Instagram session from session.json file...")
            cl.load_settings(SESSION_FILE)
            cl.login(username, password)
            print("[SUCCESS] Session authenticated via session.json.")
            return cl
        except Exception as e:
            print(f"[WARN] Failed to load session.json: {e}. Proceeding with fresh login...")

    # 3. Standard Login
    print(f"[INFO] Logging into Instagram as: {username}...")
    cl.login(username, password)
    print("[SUCCESS] Successfully logged into Instagram!")

    # Save session for next runs
    try:
        cl.dump_settings(SESSION_FILE)
        print(f"[INFO] Saved updated session to {SESSION_FILE}")
    except Exception as e:
        print(f"[WARN] Could not dump session: {e}")

    return cl


def main():
    parser = argparse.ArgumentParser(description="GitHub Actions Instagram Direct Publisher")
    parser.add_argument("--dry-run", action="store_true", help="Render without publishing")
    args = parser.parse_args()

    username = os.getenv("IG_USERNAME")
    password = os.getenv("IG_PASSWORD")

    quotes = load_quotes()
    history = load_history()
    quote = select_daily_quote(quotes, history)

    print("\n=======================================================")
    print(f" Daily Motivational Post: #{quote['id']} - {quote['category']}")
    print("=======================================================")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_image_path = os.path.join(OUTPUT_DIR, f"daily_post_{quote['id']}.jpg")
    
    # Render graphic as JPEG (required by Instagram mobile API)
    render_quote_card(quote, out_image_path, DEFAULT_BG)
    caption = quote["caption"]

    if args.dry_run:
        print("\n[DRY RUN MODE]")
        print("Image:", out_image_path)
        print("Caption preview:\n", caption)
        print("\nReady! Set IG_USERNAME and IG_PASSWORD in GitHub Secrets to publish.")
        return

    if not username or not password:
        print("\n[ERROR] Missing Instagram credentials!")
        print("Please set IG_USERNAME and IG_PASSWORD in your GitHub Repository Secrets.")
        sys.exit(1)

    # Authenticate and publish
    cl = get_authenticated_client(username, password)

    print(f"[INFO] Uploading photo to Instagram feed...")
    media = cl.photo_upload(
        path=out_image_path,
        caption=caption
    )
    print(f"\n🎉 [SUCCESS] Post is LIVE on Instagram! Media ID: {media.pk}")

    history["posted_ids"].append(quote["id"])
    history["last_posted_date"] = time.strftime("%Y-%m-%d %H:%M:%S UTC")
    save_history(history)
    print(f"[INFO] Recorded quote #{quote['id']} in posting history.")


if __name__ == "__main__":
    main()
