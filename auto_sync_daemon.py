#!/usr/bin/env python3
"""
Autonomous YouTube Auth Watcher & GitHub Secret Syncer
Monitors ~/Downloads for client_secret_*.json, immediately pops up the authorization window,
captures the refresh token, and pushes all secrets directly to GitHub Actions.
"""
import os
import sys
import glob
import json
import time
import urllib.request
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import subprocess

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
            html = "<html><body style='font-family:sans-serif;background:#0d1117;color:#fff;text-align:center;padding:50px;'><h1 style='color:#2ea043;'>Authorization Successful!</h1><p>Antigravity IDE is now uploading your secrets to GitHub Actions...</p></body></html>"
            self.wfile.write(html.encode("utf-8"))
        else:
            self.send_response(400)
            self.end_headers()

    def log_message(self, *args):
        pass


def upload_secrets_to_github(client_id, client_secret, refresh_token):
    try:
        from base64 import b64encode
        from nacl import encoding, public

        proc = subprocess.run(
            ["git", "credential-osxkeychain", "get"],
            input=b"protocol=https\nhost=github.com\n\n",
            capture_output=True
        )
        token = None
        for line in proc.stdout.decode().splitlines():
            if line.startswith("password="):
                token = line.split("=", 1)[1].strip()
        if not token:
            print("[ERROR] GitHub token not found in keychain.")
            return False

        repo = "simranlifeclub-cloud/instagram-daily-quotes"
        base_api = f"https://api.github.com/repos/{repo}/actions/secrets"
        req = urllib.request.Request(f"{base_api}/public-key", headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        })
        with urllib.request.urlopen(req) as resp:
            pk_info = json.load(resp)
        public_key = public.PublicKey(pk_info["key"].encode("utf-8"), encoding.Base64Encoder())
        sealed_box = public.SealedBox(public_key)

        def put_secret(name, val):
            enc = sealed_box.encrypt(val.encode("utf-8"))
            b64 = b64encode(enc).decode("utf-8")
            payload = json.dumps({"encrypted_value": b64, "key_id": pk_info["key_id"]}).encode("utf-8")
            r = urllib.request.Request(f"{base_api}/{name}", data=payload, headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "Content-Type": "application/json"
            }, method="PUT")
            with urllib.request.urlopen(r) as res:
                return res.status in [201, 204]

        print("\n[INFO] Uploading YOUTUBE_CLIENT_ID to GitHub Actions...")
        put_secret("YOUTUBE_CLIENT_ID", client_id)
        print("[INFO] Uploading YOUTUBE_CLIENT_SECRET to GitHub Actions...")
        put_secret("YOUTUBE_CLIENT_SECRET", client_secret)
        print("[INFO] Uploading YOUTUBE_REFRESH_TOKEN to GitHub Actions...")
        put_secret("YOUTUBE_REFRESH_TOKEN", refresh_token)
        print("🎉 [SUCCESS] All secrets successfully uploaded to GitHub Actions!\n")
        return True
    except Exception as e:
        print(f"[ERROR] Secret upload error: {e}")
        return False


def find_client_secret_file():
    d_dir = os.path.expanduser("~/Downloads")
    if not os.path.exists(d_dir):
        return None, None, None
    files = sorted(
        [os.path.join(d_dir, f) for f in os.listdir(d_dir) if f.startswith("client_secret") and f.endswith(".json")],
        key=os.path.getmtime,
        reverse=True
    )
    for path in files:
        try:
            with open(path) as fp:
                data = json.load(fp)
            key = "installed" if "installed" in data else "web"
            return data[key]["client_id"], data[key]["client_secret"], path
        except Exception:
            pass
    return None, None, None


def run_auth_flow(client_id, client_secret):
    global auth_code
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
    print(f"\n[INFO] Opening browser for channel authorization: {auth_url}\n")
    subprocess.run(["open", auth_url])

    server = HTTPServer(("localhost", PORT), OAuthCallbackHandler)
    server.timeout = 180
    print("[INFO] Waiting for you to click 'Allow' in Safari / Chrome...")
    server.handle_request()

    if not auth_code:
        print("[ERROR] Authorization failed or timed out.")
        return False

    print("\n[INFO] Exchanging code for refresh token...")
    token_url = "https://oauth2.googleapis.com/token"
    data = urllib.parse.urlencode({
        "client_id": client_id,
        "client_secret": client_secret,
        "code": auth_code,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri
    }).encode("utf-8")
    req = urllib.request.Request(token_url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req) as resp:
        tdata = json.load(resp)
    refresh_token = tdata.get("refresh_token")
    if not refresh_token:
        print("[ERROR] No refresh token returned. Revoke previous grant at https://myaccount.google.com/connections")
        return False

    upload_secrets_to_github(client_id, client_secret, refresh_token)
    return True


if __name__ == "__main__":
    cid, csec, path = find_client_secret_file()
    if cid and csec:
        print(f"[INFO] Found credentials in {path}!")
        run_auth_flow(cid, csec)
    else:
        print("[WATCHER] Waiting for client_secret_*.json to be downloaded to ~/Downloads...")
        while True:
            time.sleep(2)
            cid, csec, path = find_client_secret_file()
            if cid and csec:
                print(f"[INFO] Detected new credentials file: {path}!")
                if run_auth_flow(cid, csec):
                    print("🚀 ALL STEPS COMPLETED AUTONOMOUSLY!")
                    break
