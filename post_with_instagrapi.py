import os
import sys
import json
import time
import random
import argparse
import shutil
from datetime import datetime, timezone, timedelta

from background_manager import select_dynamic_background, get_available_backgrounds
from audio_manager import select_dynamic_audio, populate_starter_audio_library
from video_manager import select_dynamic_video

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
QUOTES_FILE = os.path.join(BASE_DIR, "quotes_database.json")
HISTORY_FILE = os.path.join(BASE_DIR, "history.json")
SESSION_FILE = os.path.join(BASE_DIR, "session.json")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")


def load_quotes():
    if not os.path.exists(QUOTES_FILE):
        raise FileNotFoundError(f"Quotes file not found at: {QUOTES_FILE}")
    with open(QUOTES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_history():
    default_state = {
        "posted_ids": [],
        "used_backgrounds": [],
        "used_videos": [],
        "used_audio": [],
        "used_themes": [],
        "used_formats": [],
        "used_voices": [],
        "youtube_shorts_ids": [],
        "last_posted_date": None
    }
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                for k, v in default_state.items():
                    if k not in data:
                        data[k] = v
                return data
        except Exception:
            return default_state
    return default_state


def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)


def get_current_ist_slot():
    ist_tz = timezone(timedelta(hours=5, minutes=30))
    now_ist = datetime.now(ist_tz)
    hour = now_ist.hour
    
    # Morning window (03:00 to 14:00 IST)
    if 3 <= hour < 14:
        return "morning"
    # Evening window (14:00 to 03:00 IST)
    else:
        return "evening"


def select_dynamic_quote(quotes, history, quote_id=None, lang=None):
    if quote_id is not None:
        matching = [q for q in quotes if q["id"] == quote_id]
        if matching:
            print(f"[INFO] Selected forced quote #{quote_id} [{matching[0].get('language', 'en')}].")
            return matching[0]
        print(f"[WARN] Quote ID #{quote_id} not found, falling back to dynamic rotation.")

    filtered_quotes = quotes
    if lang is not None:
        filtered = [q for q in quotes if q.get("language", "en") == lang]
        if filtered:
            filtered_quotes = filtered

    posted_ids = set(history.get("posted_ids", []))
    current_slot = get_current_ist_slot()

    # Map current schedule to compatible categories
    if current_slot == "morning":
        preferred_slots = ["morning", "midday"]
    else:
        preferred_slots = ["evening", "afternoon", "night"]
    
    slot_available = [q for q in filtered_quotes if q.get("slot") in preferred_slots and q["id"] not in posted_ids]
    if slot_available:
        selected = random.choice(slot_available)
        print(f"[INFO] Selected '{selected.get('slot')}' quote #{selected['id']} [{selected.get('language', 'en')}].")
        return selected

    general_available = [q for q in filtered_quotes if q["id"] not in posted_ids]
    if general_available:
        selected = random.choice(general_available)
        print(f"[INFO] Preferred slots exhausted. Selected unposted quote #{selected['id']} [{selected.get('language', 'en')}].")
        return selected

    print("[INFO] Full library of quotes has been published! Resetting rotation cycle.")
    history["posted_ids"] = []
    return random.choice(filtered_quotes)


def format_growth_optimized_caption(quote):
    """
    Formats captions engineered for the Instagram recommendation algorithm:
    - Retains the core inspirational text.
    - Appends high-conversion CTAs for Saves & DM Shares (Instagram's #1 & #2 ranking signals).
    - Focuses on targeted, high-intent discovery hashtags.
    """
    raw_caption = quote.get("caption", "")
    if "\n.\n." in raw_caption:
        body = raw_caption.split("\n.\n.")[0].strip()
    elif "\n#" in raw_caption:
        body = raw_caption.split("\n#")[0].strip()
    else:
        body = raw_caption.strip()

    growth_cta = (
        "\n\n"
        "📌 Save this reminder for when you need quiet strength.\n"
        "↗️ Send this to someone who needs to hear it today.\n\n"
        "Follow @simranlifeclub for daily wisdom, clarity & peace. 🌿\n"
        ".\n"
        ".\n"
        "#simranlifeclub #innerpeace #mindsetshift #selfgrowthjourney #quietstrength #perspective #mentalclarity #stoicmindset #dailywisdom"
    )
    return body + growth_cta


def get_authenticated_client(username, password):
    from instagrapi import Client
    cl = Client()
    cl.delay_range = [2, 5]

    cl.set_country("IN")
    cl.set_locale("en_IN")
    cl.set_timezone_offset(int(5.5 * 3600))
    cl.set_user_agent(
        "Instagram 340.0.0.38.109 Android (33/13; 420dpi; 1080x2400; Xiaomi; M2101K6G; sweet; qcom; en_US; 618585954)"
    )

    # 1. Direct sessionid cookie (100% bypasses login 429 rate limit!)
    sessionid = os.getenv("IG_SESSIONID")
    if sessionid and sessionid.strip():
        try:
            print("[INFO] Authenticating using trusted IG_SESSIONID cookie...")
            cl.login_by_sessionid(sessionid.strip())
            print("[SUCCESS] Successfully authenticated via session ID! Zero 429 blocks.")
            return cl
        except Exception as e:
            print(f"[WARN] Session ID login error: {e}. Falling back...")

    # 2. Check saved session from env
    session_env = os.getenv("IG_SESSION_DATA")
    if session_env and session_env.strip():
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
    print(f"[INFO] Logging in with credentials as: {username}...")
    try:
        cl.login(username, password)
        print("[SUCCESS] Successfully logged into Instagram!")
    except Exception as e:
        err_str = str(e)
        if "Please wait a few minutes" in err_str or "429" in err_str:
            print("\n" + "=" * 60)
            print("[NOTICE] Instagram temporarily rate-limited password logins from cloud IPs.")
            print("To bypass this instantly, add your 'IG_SESSIONID' to GitHub Secrets!")
            print("=" * 60 + "\n")
        raise e

    try:
        cl.dump_settings(SESSION_FILE)
    except Exception:
        pass

    return cl


def main():
    parser = argparse.ArgumentParser(description="Instagram Multi-Format Reel Publisher")
    parser.add_argument("--dry-run", action="store_true", help="Render video/image without uploading")
    parser.add_argument("--no-jitter", action="store_true", help="Disable human posting time jitter")
    parser.add_argument("--format", type=str, choices=["VOICEOVER", "SHORT_VIDEO", "PURE_CINEMATIC", "TEXT_POSTER"], default=None, help="Force specific reel format")
    parser.add_argument("--bg", type=str, default=None, help="Force specific background image filename")
    parser.add_argument("--video", type=str, default=None, help="Force specific background video filename")
    parser.add_argument("--theme", type=str, default=None, help="Force specific visual theme")
    parser.add_argument("--audio", type=str, default=None, help="Force specific audio filename")
    parser.add_argument("--voice", type=str, default=None, help="Force specific voice id")
    parser.add_argument("--quote-id", type=int, default=None, help="Force specific quote ID")
    parser.add_argument("--lang", type=str, choices=["en", "hi"], default=None, help="Filter quotes by language (en or hi)")
    parser.add_argument("--storyboard", type=str, choices=["reality_check"], default=None, help="Publish a dedicated multi-scene narrative reel")
    parser.add_argument("--no-youtube", action="store_true", help="Skip YouTube Shorts publication")
    parser.add_argument("--youtube-only", action="store_true", help="Publish only to YouTube Shorts (skip Instagram)")
    args = parser.parse_args()

    # Pre-populate starter audio files if needed
    populate_starter_audio_library()

    username = os.getenv("IG_USERNAME")
    password = os.getenv("IG_PASSWORD")
    sessionid = os.getenv("IG_SESSIONID")

    is_manual = os.getenv("GITHUB_EVENT_NAME") == "workflow_dispatch"
    
    # Only add delay on automatic cron schedules (instant for manual tests)
    if not args.dry_run and not args.no_jitter and not is_manual:
        jitter_seconds = random.randint(60, 480)
        print(f"[INFO] Adding natural human jitter: waiting {jitter_seconds // 60}m {jitter_seconds % 60}s before publishing...")
        time.sleep(jitter_seconds)
    else:
        print("[INFO] Manual run or test detected: publishing immediately without delay!")

    history = load_history()
    is_storyboard = args.storyboard or os.getenv("STORYBOARD_REEL")

    if is_storyboard == "reality_check":
        from reality_check_reel_builder import build_reality_check_reel
        media_path = os.path.join(OUTPUT_DIR, "reality_check_reset_reel.mp4")
        media_path, thumb_path, caption = build_reality_check_reel(output_mp4=media_path)
        is_video = True
        meta = {
            "format": "STORYBOARD_MULTI_SCENE",
            "title": "The Reality Check & Reset",
            "voice": "en-US-EricNeural",
            "audio": "Ambient Piano & Lo-Fi",
            "duration": 30.0,
            "motion": "Ken Burns Camera Tracking"
        }
        quote = {"id": "reality_check_reset", "slot": "special"}
    else:
        quotes = load_quotes()
        quote = select_dynamic_quote(quotes, history, quote_id=args.quote_id, lang=args.lang)

        print("\n=======================================================")
        print(f" Daily Motivational Reel: #{quote['id']} [{quote.get('slot', 'general').upper()}]")
        print(f" Category: {quote.get('category', 'MOTIVATION')}")
        print("=======================================================")

        os.makedirs(OUTPUT_DIR, exist_ok=True)
        caption = format_growth_optimized_caption(quote)

        has_ffmpeg = shutil.which("ffmpeg") is not None
        thumb_path = None
        
        if has_ffmpeg:
            from video_reel_generator import build_mp4_reel
            media_path = os.path.join(OUTPUT_DIR, f"daily_reel_{quote['id']}.mp4")
            media_path, thumb_path, meta = build_mp4_reel(
                quote,
                media_path,
                duration=7,
                reel_format=args.format,
                bg_image_path=args.bg,
                bg_video_path=args.video,
                audio_path=args.audio,
                voice_id=args.voice,
                theme_name=args.theme,
                history=history
            )
            is_video = True
        else:
            from card_renderer import render_quote_card
            bg_path, bg_name = select_dynamic_background(history, slot=quote.get("slot"))
            media_path = os.path.join(OUTPUT_DIR, f"daily_post_{quote['id']}.jpg")
            media_path, applied_theme = render_quote_card(
                quote, media_path, bg_image_path=bg_path, theme_name=args.theme
            )
            meta = {
                "format": "PHOTO_FALLBACK",
                "background": bg_name,
                "theme": applied_theme,
                "voice": None,
                "audio": "N/A (Photo Mode)",
                "audio_id": None,
                "motion": "Static Photo"
            }
            is_video = False

    if args.dry_run:
        print("\n[DRY RUN MODE]")
        print("Media file:    ", media_path)
        print("Format:        ", meta.get("format", "Instagram Reel"))
        print("Time Slot:     ", quote.get("slot"))
        print("Background:    ", meta.get("background"))
        print("Visual Theme:  ", meta.get("theme"))
        print("Voiceover:     ", meta.get("voice") or "None (Music Only)")
        print("Soundtrack:    ", meta.get("audio"))
        print("Camera Motion: ", meta.get("motion"))
        print("Thumbnail:     ", thumb_path)
        print("\nCaption preview:\n", caption)
        return

    if getattr(args, "youtube_only", False):
        if not is_video:
            print("[WARN] Photo mode fallback active. YouTube Shorts requires video. Skipping.")
            return
        from youtube_uploader import maybe_upload_to_youtube_shorts
        yt_id = maybe_upload_to_youtube_shorts(
            video_path=media_path,
            quote=quote,
            caption=caption,
            meta=meta
        )
        if yt_id:
            history.setdefault("youtube_shorts_ids", []).append(yt_id)
            history["last_posted_date"] = time.strftime("%Y-%m-%d %H:%M:%S UTC")
            save_history(history)
        return

    if not sessionid and (not username or not password):
        print("\n[ERROR] Missing Instagram credentials!")
        print("Please set IG_USERNAME & IG_PASSWORD (or IG_SESSIONID) in GitHub Secrets.")
        sys.exit(1)

    cl = get_authenticated_client(username, password)

    if is_video:
        print(f"[INFO] Uploading MP4 Reel to Instagram with custom cover thumbnail...")
        media = cl.clip_upload(
            path=media_path,
            caption=caption,
            thumbnail=thumb_path
        )
        print(f"\n🎉 [SUCCESS] REEL is LIVE on Instagram! Reel PK: {media.pk}")

        # Automatically publish as YouTube Short as well
        if not getattr(args, "no_youtube", False):
            try:
                from youtube_uploader import maybe_upload_to_youtube_shorts
                yt_id = maybe_upload_to_youtube_shorts(
                    video_path=media_path,
                    quote=quote,
                    caption=caption,
                    meta=meta
                )
                if yt_id:
                    history.setdefault("youtube_shorts_ids", []).append(yt_id)
            except Exception as yt_err:
                print(f"[WARN] YouTube Shorts upload error: {yt_err}")
    else:
        print(f"[INFO] Uploading Photo to Instagram Feed...")
        media = cl.photo_upload(path=media_path, caption=caption)
        print(f"\n🎉 [SUCCESS] Post is LIVE on Instagram! Media PK: {media.pk}")

    # Track History across all dimensions
    history["posted_ids"].append(quote["id"])
    if meta.get("format"):
        history["used_formats"].append(meta["format"])
    if meta.get("voice"):
        history["used_voices"].append(meta["voice"])
    if meta.get("background"):
        history["used_backgrounds"].append(meta["background"])
    if meta.get("audio_id"):
        history["used_audio"].append(meta["audio_id"])
    elif meta.get("audio"):
        history["used_audio"].append(meta["audio"])
    if meta.get("theme"):
        history["used_themes"].append(meta["theme"])

    history["last_posted_date"] = time.strftime("%Y-%m-%d %H:%M:%S UTC")
    save_history(history)
    print(f"[INFO] Recorded quote #{quote['id']} [{meta.get('format')}] in history!")


if __name__ == "__main__":
    main()
