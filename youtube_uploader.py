"""
YouTube Shorts Automated Publisher Module
Handles authentication via OAuth 2.0 refresh token and uploads vertical videos
as YouTube Shorts with SEO-optimized titles, descriptions, and hashtags.
"""

import os
import sys
import time
import random
import argparse
from typing import Optional, Dict, Any, List

# Optional Google API client imports with safe fallback
try:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    from googleapiclient.http import MediaFileUpload
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False


# Default viral tags for YouTube Shorts recommendation engine
SHORTS_DEFAULT_TAGS = [
    "Shorts",
    "YouTube Shorts",
    "Motivation",
    "Daily Motivation",
    "Inspirational Quotes",
    "Mindset",
    "Self Growth",
    "Inner Peace",
    "Daily Wisdom",
    "Simran Life Club"
]

RETRIABLE_STATUS_CODES = [500, 502, 503, 504]
MAX_RETRIES = 5


def get_youtube_service(client_id: Optional[str] = None,
                        client_secret: Optional[str] = None,
                        refresh_token: Optional[str] = None):
    """
    Constructs an authorized YouTube Resource using the OAuth2 Refresh Token.
    Returns None if credentials are missing or google client is not installed.
    """
    if not GOOGLE_API_AVAILABLE:
        print("[WARN] Google API client libraries not installed. Run: pip install google-api-python-client google-auth-oauthlib google-auth-httplib2")
        return None

    cid = client_id or os.getenv("YOUTUBE_CLIENT_ID")
    csecret = client_secret or os.getenv("YOUTUBE_CLIENT_SECRET")
    rtoken = refresh_token or os.getenv("YOUTUBE_REFRESH_TOKEN")

    if not (cid and csecret and rtoken):
        return None

    creds = Credentials(
        token=None,
        refresh_token=rtoken.strip(),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=cid.strip(),
        client_secret=csecret.strip(),
        scopes=["https://www.googleapis.com/auth/youtube.upload"]
    )

    return build("youtube", "v3", credentials=creds, cache_discovery=False)


def format_youtube_shorts_title(quote: Optional[Dict[str, Any]] = None,
                                title_override: Optional[str] = None) -> str:
    """
    Constructs a compelling YouTube Shorts title (< 100 characters).
    Always contains #Shorts for instant algorithm categorization.
    """
    if title_override:
        t = title_override.strip()
        if "#Shorts" not in t:
            t = f"{t} #Shorts"
        return t[:100]

    if not quote:
        return "Daily Motivation & Quiet Strength ✨ #Shorts"

    hero_lines = quote.get("hero_lines", [])
    if hero_lines and len(hero_lines) > 0:
        first_line = hero_lines[0].strip().rstrip(",.- ")
    elif quote.get("quote_text"):
        first_line = quote["quote_text"].split(".")[0].strip()
    elif quote.get("category"):
        first_line = quote["category"].title()
    else:
        first_line = "Daily Motivation"

    if len(first_line) > 55:
        first_line = first_line[:52] + "..."

    title = f"{first_line} ✨ #Shorts #DailyMotivation"
    return title[:100]


def format_youtube_shorts_description(quote: Optional[Dict[str, Any]] = None,
                                      caption_override: Optional[str] = None) -> str:
    """
    Formats the Shorts description with the quote text, growth CTAs,
    channel subscribe link, and SEO discovery hashtags.
    """
    if caption_override:
        clean = caption_override.strip()
        if "\n.\n." in clean:
            clean = clean.split("\n.\n.")[0].strip()
        body = clean
    elif quote:
        parts = []
        if quote.get("hero_lines"):
            parts.extend(quote["hero_lines"])
        elif quote.get("quote_text"):
            parts.append(quote["quote_text"])
        if quote.get("subtext"):
            parts.append(quote["subtext"])
        body = "\n".join(parts)
    else:
        body = "Daily motivation, calm mindset, and personal growth reminder."

    growth_block = (
        "\n\n"
        "📌 Save this Short whenever you need quiet strength.\n"
        "↗️ Share this with someone who needs to hear this today.\n\n"
        "🔔 Subscribe to @simranlifeclub for daily wisdom, clarity & peace. 🌿\n\n"
        "#Shorts #YouTubeShorts #Motivation #DailyMotivation #Mindset #SelfGrowth "
        "#InnerPeace #InspirationalQuotes #DailyWisdom #SimranLifeClub"
    )

    return body + growth_block


def upload_video_to_youtube(video_path: str,
                            title: str,
                            description: str,
                            tags: Optional[List[str]] = None,
                            category_id: str = "27",
                            privacy_status: str = "public",
                            made_for_kids: bool = False,
                            youtube_service=None) -> str:
    """
    Uploads a video to YouTube using resumable chunked upload.
    Returns the YouTube video ID on success.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    yt = youtube_service or get_youtube_service()
    if yt is None:
        raise ValueError("YouTube service could not be initialized. Check credentials.")

    tags_list = tags or SHORTS_DEFAULT_TAGS

    body = {
        "snippet": {
            "title": title[:100],
            "description": description,
            "tags": tags_list,
            "categoryId": category_id
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": made_for_kids
        }
    }

    media = MediaFileUpload(
        video_path,
        chunksize=1024 * 1024 * 2,
        resumable=True,
        mimetype="video/mp4"
    )

    request = yt.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )

    print(f"\n[YOUTUBE] Initializing upload for: '{title[:60]}...'")
    print(f"[YOUTUBE] Video Path: {video_path} ({os.path.getsize(video_path) / (1024*1024):.2f} MB)")
    print(f"[YOUTUBE] Privacy:    {privacy_status.upper()}")

    response = None
    error = None
    retry = 0

    while response is None:
        try:
            status, response = request.next_chunk()
            if status:
                print(f"[YOUTUBE] Uploading Short... {int(status.progress() * 100)}%")
        except HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = f"Retriable HTTP error {e.resp.status}: {e.content}"
            else:
                raise e
        except Exception as e:
            error = f"Retriable network exception: {e}"

        if error:
            retry += 1
            if retry > MAX_RETRIES:
                raise RuntimeError(f"Exceeded max retries uploading to YouTube: {error}")
            sleeptime = random.random() * (2 ** retry)
            print(f"[YOUTUBE] {error}. Retrying in {sleeptime:.1f}s (attempt {retry}/{MAX_RETRIES})...")
            time.sleep(sleeptime)
            error = None

    if "id" in response:
        video_id = response["id"]
        print("\n🎉 [SUCCESS] SHORTS is LIVE on YouTube!")
        print(f"🎬 Video ID:  {video_id}")
        print(f"🔗 Shorts URL: https://youtube.com/shorts/{video_id}\n")
        return video_id
    else:
        raise RuntimeError(f"Unexpected upload response from YouTube API: {response}")


def maybe_upload_to_youtube_shorts(video_path: str,
                                   quote: Optional[Dict[str, Any]] = None,
                                   caption: Optional[str] = None,
                                   meta: Optional[Dict[str, Any]] = None,
                                   title_override: Optional[str] = None,
                                   privacy_status: Optional[str] = None) -> Optional[str]:
    """
    Graceful wrapper used by posting workflows:
    - Checks whether YouTube credentials are provided.
    - If credentials are NOT configured: logs an informative note and returns None.
    - If credentials ARE configured: automatically formats title/description and publishes Short.
    """
    cid = os.getenv("YOUTUBE_CLIENT_ID")
    csecret = os.getenv("YOUTUBE_CLIENT_SECRET")
    rtoken = os.getenv("YOUTUBE_REFRESH_TOKEN")

    if not (cid and csecret and rtoken):
        print("\n[INFO] YouTube credentials not set (YOUTUBE_CLIENT_ID / YOUTUBE_CLIENT_SECRET / YOUTUBE_REFRESH_TOKEN).")
        print("[INFO] Skipping YouTube Shorts publication. (See setup_youtube_guide.md to enable YouTube Shorts)\n")
        return None

    if not GOOGLE_API_AVAILABLE:
        print("\n[WARN] Google API Client not installed. Skipping YouTube Shorts.\n")
        return None

    privacy = privacy_status or os.getenv("YOUTUBE_PRIVACY_STATUS", "public")

    if title_override:
        title = format_youtube_shorts_title(title_override=title_override)
    elif meta and meta.get("title"):
        title = format_youtube_shorts_title(title_override=meta["title"])
    else:
        title = format_youtube_shorts_title(quote=quote)

    description = format_youtube_shorts_description(quote=quote, caption_override=caption)

    try:
        video_id = upload_video_to_youtube(
            video_path=video_path,
            title=title,
            description=description,
            privacy_status=privacy
        )
        return video_id
    except Exception as e:
        print(f"\n[ERROR] Failed to upload Short to YouTube: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="Upload MP4 Video as YouTube Short")
    parser.add_argument("--video", type=str, required=True, help="Path to vertical MP4 video file")
    parser.add_argument("--title", type=str, default=None, help="Video Title (defaults to auto-generated)")
    parser.add_argument("--description", type=str, default=None, help="Video Description")
    parser.add_argument("--privacy", type=str, choices=["public", "unlisted", "private"], default="public", help="Privacy status")
    args = parser.parse_args()

    title = args.title or "Daily Motivation & Calm Mindset ✨ #Shorts"
    desc = args.description or (
        "Daily reminder for quiet strength and peace.\n\n"
        "Subscribe to @simranlifeclub for daily wisdom & self growth. 🌿\n\n"
        "#Shorts #YouTubeShorts #Motivation #Mindset"
    )

    upload_video_to_youtube(
        video_path=args.video,
        title=title,
        description=desc,
        privacy_status=args.privacy
    )


if __name__ == "__main__":
    main()
