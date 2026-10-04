"""
Zero-Dependency YouTube Channel Authorization Helper
Uses Python standard libraries (urllib, http.server, webbrowser) to generate
the permanent OAuth 2.0 Refresh Token needed for automated YouTube Shorts publishing.
"""

import os
import sys
import json
import urllib.request
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import webbrowser

SCOPES = "https://www.googleapis.com/auth/youtube.upload"
PORT = 8080
auth_code = None


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        parsed_url = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(parsed_url.query)

        if "code" in query:
            auth_code = query["code"][0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            success_html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>YouTube Authorization Successful</title>
                <style>
                    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                           background: #0d1117; color: #e6edf3; display: flex; align-items: center;
                           justify-content: center; height: 100vh; margin: 0; }
                    .card { background: #161b22; border: 1px solid #30363d; padding: 40px; border-radius: 12px;
                            box-shadow: 0 8px 24px rgba(0,0,0,0.5); text-align: center; max-width: 480px; }
                    h1 { color: #2ea043; margin-top: 0; font-size: 24px; }
                    p { font-size: 16px; color: #8b949e; line-height: 1.5; }
                    .badge { background: #238636; color: white; padding: 6px 12px; border-radius: 20px; font-weight: 600; }
                </style>
            </head>
            <body>
                <div class="card">
                    <h1>✅ Authorization Successful!</h1>
                    <p>Your YouTube Channel has been successfully authenticated for automated Shorts publishing.</p>
                    <p><span class="badge">Return to Antigravity IDE</span> to view your generated secrets.</p>
                </div>
            </body>
            </html>
            """
            self.wfile.write(success_html.encode("utf-8"))
        else:
            self.send_response(400)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            err_msg = query.get("error", ["Unknown error"])[0]
            self.wfile.write(f"<h1>Authorization Failed</h1><p>{err_msg}</p>".encode("utf-8"))

    def log_message(self, format, *args):
        # Silence local server request logs
        return


def main():
    global auth_code
    print("\n" + "=" * 65)
    print("🎬 YouTube Shorts 1-Click Channel Authorization")
    print("=" * 65)
    print("This script generates your permanent YOUTUBE_REFRESH_TOKEN so")
    print("GitHub Actions can automatically publish Shorts to your channel.\n")

    client_id = os.getenv("YOUTUBE_CLIENT_ID")
    client_secret = os.getenv("YOUTUBE_CLIENT_SECRET")

    # Check client_secrets.json
    if os.path.exists("client_secrets.json"):
        try:
            with open("client_secrets.json", "r") as f:
                cdata = json.load(f)
            key = "installed" if "installed" in cdata else "web"
            client_id = cdata[key]["client_id"]
            client_secret = cdata[key]["client_secret"]
            print("[INFO] Loaded Client ID & Secret from 'client_secrets.json'.")
        except Exception as e:
            print(f"[WARN] Error reading client_secrets.json: {e}")

    # Check .env
    if (not client_id or not client_secret) and os.path.exists(".env"):
        with open(".env", "r") as f:
            for line in f:
                if line.startswith("YOUTUBE_CLIENT_ID="):
                    client_id = line.split("=", 1)[1].strip()
                elif line.startswith("YOUTUBE_CLIENT_SECRET="):
                    client_secret = line.split("=", 1)[1].strip()

    if not client_id or not client_secret:
        print("Please enter your Google Cloud OAuth Client Credentials:")
        print("(From Google Cloud Console -> APIs & Services -> Credentials -> OAuth 2.0 Client ID)")
        print("-" * 65)
        client_id = input("Enter YouTube Client ID: ").strip()
        client_secret = input("Enter YouTube Client Secret: ").strip()

    if not client_id or not client_secret:
        print("[ERROR] Client ID and Client Secret are required.")
        sys.exit(1)

    redirect_uri = f"http://localhost:{PORT}/"

    auth_params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": SCOPES,
        "access_type": "offline",
        "prompt": "consent"
    }

    auth_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(auth_params)

    server = HTTPServer(("localhost", PORT), OAuthCallbackHandler)
    server.timeout = 180  # 3 minutes timeout

    print(f"\n[INFO] Opening your browser to authorize your YouTube Channel...")
    print(f"If your browser doesn't open automatically, visit this URL:\n\n{auth_url}\n")
    webbrowser.open(auth_url)

    print(f"[INFO] Waiting for browser authorization on http://localhost:{PORT}/...")
    server.handle_request()

    if not auth_code:
        print("\n[ERROR] Did not receive authorization code from Google.")
        sys.exit(1)

    print("\n[INFO] Exchanging authorization code for permanent Refresh Token...")
    token_url = "https://oauth2.googleapis.com/token"
    token_data = urllib.parse.urlencode({
        "client_id": client_id,
        "client_secret": client_secret,
        "code": auth_code,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri
    }).encode("utf-8")

    req = urllib.request.Request(token_url, data=token_data, headers={
        "Content-Type": "application/x-www-form-urlencoded"
    })

    try:
        with urllib.request.urlopen(req) as resp:
            token_json = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"\n[ERROR] Failed to exchange code with Google OAuth endpoint: {e}")
        sys.exit(1)

    refresh_token = token_json.get("refresh_token")

    if not refresh_token:
        print("\n[WARN] No refresh token returned by Google.")
        print("This happens if you previously authorized this OAuth Client without revoking it.")
        print("Please visit: https://myaccount.google.com/connections, remove this app,")
        print("and re-run this script to receive a fresh refresh token.")
        sys.exit(1)

    # Save to local .env
    env_file = ".env"
    lines = []
    if os.path.exists(env_file):
        with open(env_file, "r") as f:
            lines = f.readlines()

    lines = [l for l in lines if not any(l.startswith(k) for k in [
        "YOUTUBE_CLIENT_ID=", "YOUTUBE_CLIENT_SECRET=", "YOUTUBE_REFRESH_TOKEN="
    ])]
    lines.append(f"YOUTUBE_CLIENT_ID={client_id}\n")
    lines.append(f"YOUTUBE_CLIENT_SECRET={client_secret}\n")
    lines.append(f"YOUTUBE_REFRESH_TOKEN={refresh_token}\n")

    with open(env_file, "w") as f:
        f.writelines(lines)

    print("\n" + "=" * 65)
    print("🎉 SUCCESS! Your YouTube Refresh Token has been generated!")
    print("=" * 65)
    print("Credentials saved to your local .env file.\n")
    print("Now add these 3 Secrets to your GitHub Repository:")
    print("➡️  https://github.com/simranlifeclub-cloud/instagram-daily-quotes/settings/secrets/actions\n")
    print(f"1. Name:  YOUTUBE_CLIENT_ID\n   Value: {client_id}\n")
    print(f"2. Name:  YOUTUBE_CLIENT_SECRET\n   Value: {client_secret}\n")
    print(f"3. Name:  YOUTUBE_REFRESH_TOKEN\n   Value: {refresh_token}\n")
    print("=" * 65)
    print("Once added to GitHub Secrets, every daily run will automatically")
    print("publish your Shorts to YouTube as well as Instagram Reels!")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    main()
