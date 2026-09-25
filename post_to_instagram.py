import os
import sys
import json
import time
import argparse
import requests
from card_renderer import render_quote_card
from background_manager import select_dynamic_background

# Constants & Defaults
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
QUOTES_FILE = os.path.join(BASE_DIR, "quotes_database.json")
HISTORY_FILE = os.path.join(BASE_DIR, "history.json")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")


def load_quotes():
    """Loads quotes from database."""
    if not os.path.exists(QUOTES_FILE):
        raise FileNotFoundError(f"Quotes file not found at: {QUOTES_FILE}")
    with open(QUOTES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_history():
    """Loads posting history."""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"posted_ids": [], "last_posted_date": None}
    return {"posted_ids": [], "last_posted_date": None}


def save_history(history):
    """Saves updated posting history."""
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)


def select_daily_quote(quotes, history):
    """Selects the next unposted quote, or recycles if all have been posted."""
    posted_ids = set(history.get("posted_ids", []))
    available = [q for q in quotes if q["id"] not in posted_ids]
    
    if not available:
        print("[INFO] All quotes have been posted! Resetting cycle for fresh rotation.")
        posted_ids = set()
        history["posted_ids"] = []
        available = quotes
        
    selected = available[0]
    return selected


def upload_image_to_public_host(image_path):
    """
    Uploads the rendered image to a free public host (Catbox.moe / Freeimage.host)
    so Meta Graph API can download and publish it.
    """
    print(f"[INFO] Uploading {image_path} to public host for Meta API access...")
    
    # 1. Catbox.moe (Zero auth required, fast and permanent)
    try:
        url = "https://catbox.moe/user/api.php"
        with open(image_path, "rb") as f:
            files = {"fileToUpload": f}
            data = {"reqtype": "fileupload"}
            resp = requests.post(url, files=files, data=data, timeout=30)
            if resp.status_code == 200 and resp.text.startswith("http"):
                public_url = resp.text.strip()
                print(f"[SUCCESS] Public image URL: {public_url}")
                return public_url
    except Exception as e:
        print(f"[WARN] Primary image host upload failed: {e}")

    # 2. Fallback to freeimage.host if Catbox is unreachable
    try:
        url = "https://freeimage.host/api/1/upload"
        with open(image_path, "rb") as f:
            files = {"source": f}
            data = {"key": "6d207e02198a847aa98d0a2a901485a5", "format": "json"}
            resp = requests.post(url, files=files, data=data, timeout=30)
            if resp.status_code == 200:
                result = resp.json()
                public_url = result["image"]["url"]
                print(f"[SUCCESS] Fallback public image URL: {public_url}")
                return public_url
    except Exception as e:
        print(f"[WARN] Fallback image host failed: {e}")

    raise RuntimeError("Could not upload image to any public host. Meta requires a public HTTP/HTTPS image URL.")


def post_to_instagram_graph_api(image_url, caption, ig_user_id, access_token):
    """
    Official Meta Content Publishing API Workflow:
    Step 1: Create media container
    Step 2: Poll status until FINISHED
    Step 3: Publish container to Instagram
    """
    graph_version = "v21.0"
    base_url = f"https://graph.facebook.com/{graph_version}"
    
    print(f"\n[INFO] Starting Meta Graph API Publishing to Instagram Account ID: {ig_user_id}")
    
    # --- Step 1: Create Container ---
    container_endpoint = f"{base_url}/{ig_user_id}/media"
    container_payload = {
        "image_url": image_url,
        "caption": caption,
        "access_token": access_token
    }
    
    res = requests.post(container_endpoint, data=container_payload, timeout=30)
    data = res.json()
    
    if res.status_code != 200 or "id" not in data:
        error_msg = data.get("error", {}).get("message", str(data))
        raise RuntimeError(f"Failed to create Instagram media container: {error_msg}")
        
    container_id = data["id"]
    print(f"[SUCCESS] Created Instagram Media Container ID: {container_id}")
    
    # --- Step 2: Poll Container Status ---
    print("[INFO] Waiting for Meta server processing...")
    status_endpoint = f"{base_url}/{container_id}"
    ready = False
    
    for attempt in range(12):
        time.sleep(3)
        status_res = requests.get(
            status_endpoint,
            params={"fields": "status_code", "access_token": access_token},
            timeout=20
        )
        status_data = status_res.json()
        code = status_data.get("status_code", "UNKNOWN")
        print(f"  Container processing status: {code} (Check {attempt+1}/12)")
        
        if code == "FINISHED":
            ready = True
            break
        elif code in ["ERROR", "EXPIRED"]:
            raise RuntimeError(f"Meta container processing failed with status: {code}")
            
    if not ready:
        print("[WARN] Status poll timed out, attempting publish directly...")

    # --- Step 3: Publish Media ---
    publish_endpoint = f"{base_url}/{ig_user_id}/media_publish"
    publish_payload = {
        "creation_id": container_id,
        "access_token": access_token
    }
    
    pub_res = requests.post(publish_endpoint, data=publish_payload, timeout=30)
    pub_data = pub_res.json()
    
    if pub_res.status_code != 200 or "id" not in pub_data:
        err = pub_data.get("error", {}).get("message", str(pub_data))
        raise RuntimeError(f"Failed to publish to Instagram: {err}")
        
    media_id = pub_data["id"]
    print(f"\n🎉 [SUCCESS] Post is LIVE on Instagram! Media ID: {media_id}")
    return media_id


def main():
    parser = argparse.ArgumentParser(description="Automated Daily Instagram Motivational Quote Poster")
    parser.add_argument("--dry-run", action="store_true", help="Render image and preview without making live API calls")
    parser.add_argument("--force-id", type=int, help="Force post a specific quote ID from database")
    args = parser.parse_args()

    # Load credentials from environment
    ig_user_id = os.getenv("IG_USER_ID")
    access_token = os.getenv("META_ACCESS_TOKEN")

    quotes = load_quotes()
    history = load_history()

    if args.force_id:
        matching = [q for q in quotes if q["id"] == args.force_id]
        if not matching:
            print(f"[ERROR] Quote ID {args.force_id} not found in database.")
            sys.exit(1)
        quote = matching[0]
    else:
        quote = select_daily_quote(quotes, history)

    print(f"\n=======================================================")
    print(f" Daily Motivational Post: #{quote['id']} - {quote['category']}")
    print(f"=======================================================")
    print(f"Hero: {quote['hero_lines']}")
    print(f"Subtext: {quote['subtext']}")

    # Select dynamic background
    bg_path, bg_name = select_dynamic_background(history, slot=quote.get("slot"))

    # Render Image
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_image_path = os.path.join(OUTPUT_DIR, f"daily_post_{quote['id']}.png")
    out_image_path, applied_theme = render_quote_card(quote, out_image_path, bg_image_path=bg_path)

    caption = quote["caption"]

    if args.dry_run:
        print("\n[DRY RUN MODE ENABLED]")
        print("1. Image successfully generated at:", out_image_path)
        print("   Background: ", bg_name)
        print("   Visual Theme:", applied_theme)
        print("2. Instagram Caption preview:")
        print("-------------------------------------------------------")
        print(caption)
        print("-------------------------------------------------------")
        print("3. Simulated Meta Graph API call: SKIPPED (--dry-run flag active)")
        print("\nAll systems verified! To publish live, provide IG_USER_ID and META_ACCESS_TOKEN.")
        return

    if not ig_user_id or not access_token:
        print("\n[ERROR] Missing Instagram credentials!")
        print("Please set the following environment variables (or in GitHub Secrets):")
        print("  - IG_USER_ID (Your numeric Instagram Creator/Business Account ID)")
        print("  - META_ACCESS_TOKEN (Your Meta Long-Lived Graph API Access Token)")
        print("\nTip: Run with --dry-run to test image rendering and caption output without credentials.")
        sys.exit(1)

    # 1. Upload image to public URL
    public_url = upload_image_to_public_host(out_image_path)

    # 2. Publish to Instagram
    media_id = post_to_instagram_graph_api(public_url, caption, ig_user_id, access_token)

    # 3. Update History
    if "posted_ids" not in history:
        history["posted_ids"] = []
    if "used_backgrounds" not in history:
        history["used_backgrounds"] = []
    if "used_themes" not in history:
        history["used_themes"] = []

    history["posted_ids"].append(quote["id"])
    if bg_name:
        history["used_backgrounds"].append(bg_name)
    if applied_theme:
        history["used_themes"].append(applied_theme)

    history["last_posted_date"] = time.strftime("%Y-%m-%d %H:%M:%S UTC")
    save_history(history)
    print(f"[INFO] History updated. Quote #{quote['id']} recorded.")


if __name__ == "__main__":
    main()
