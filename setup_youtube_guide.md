# 🎬 YouTube Shorts Automation Setup Guide

This guide walks you through connecting your **YouTube Channel** to the automated publisher. Once configured, every scheduled run (and manual trigger) will automatically publish your high-retention 9:16 vertical videos as **YouTube Shorts** alongside your Instagram Reels!

---

## ⚡ Quick 4-Step Setup (Takes ~5 Minutes)

### Step 1: Enable the YouTube Data API v3 in Google Cloud
1. Go to the **[Google Cloud Console](https://console.cloud.google.com/)**.
2. Sign in with the Google Account that owns or manages your YouTube channel.
3. In the top bar, click the project dropdown and click **"New Project"** (name it e.g., `YouTube-Shorts-Bot`), then click **Create**.
4. Go to **APIs & Services** -> **Library** (or search for `YouTube Data API v3`).
5. Select **YouTube Data API v3** and click **"Enable"**.

---

### Step 2: Configure OAuth Consent Screen & Create Credentials
1. In Google Cloud Console, navigate to **APIs & Services** -> **OAuth consent screen**.
2. Select **External** and click **Create**.
3. Fill in:
   - **App name**: `YouTube Shorts Publisher`
   - **User support email**: Select your email.
   - **Developer contact email**: Enter your email.
   - Click **Save and Continue**.
4. **Scopes**: Click **Add or Remove Scopes**, find and check `.../auth/youtube.upload`, then click **Save and Continue**.
5. **Test users**: Click **Add Users**, enter your Google/YouTube account email address, and click **Save and Continue**.
6. Navigate to **APIs & Services** -> **Credentials**.
7. Click **+ Create Credentials** -> **OAuth client ID**.
8. Set **Application type** to **Desktop app**.
9. Set Name to `Shorts Uploader Desktop` and click **Create**.
10. Copy your **Client ID** and **Client Secret**.

---

### Step 3: Run the 1-Click Token Generator
In your terminal, navigate to this project and run:

```bash
python3 get_youtube_token.py
```

1. Enter your **Client ID** and **Client Secret** when prompted.
2. The script will automatically open your default browser (Safari/Chrome).
3. Select your YouTube channel account and click **Continue / Allow**.
4. The local server will capture your authorization and display your generated **Refresh Token**!

The script will print a box with your credentials:
```text
========================================================
🎉 SUCCESS! Your YouTube Refresh Token has been generated!
========================================================
1. YOUTUBE_CLIENT_ID:     <your_client_id>
2. YOUTUBE_CLIENT_SECRET: <your_client_secret>
3. YOUTUBE_REFRESH_TOKEN: <your_refresh_token>
========================================================
```

---

### Step 4: Add the Secrets to GitHub
1. Open your GitHub Repository in your browser:
   **[GitHub Repository Secrets](https://github.com/simranlifeclub-cloud/instagram-daily-quotes/settings/secrets/actions)**
2. Click **"New repository secret"** and add each of the 3 keys:

| Secret Name | Value |
|---|---|
| `YOUTUBE_CLIENT_ID` | Your OAuth Client ID from Google Cloud |
| `YOUTUBE_CLIENT_SECRET` | Your OAuth Client Secret from Google Cloud |
| `YOUTUBE_REFRESH_TOKEN` | The refresh token output by `get_youtube_token.py` |

*(Optional)* If you want videos to be uploaded as **Unlisted** first before making them public, you can add a Repository Variable:
- Go to **Settings** -> **Secrets and variables** -> **Actions** -> **Variables** tab.
- Click **New repository variable**:
  - Name: `YOUTUBE_PRIVACY_STATUS`
  - Value: `unlisted` (or leave default `public`)

---

## 🚀 How It Works Automatically

- **Dual Publishing**: Whenever GitHub Actions runs, it renders the 1080x1920 MP4 vertical video with background motion, cinematic typography, and neural voiceover.
- **Instagram**: Published to **@simranlifeclub** as an Instagram Reel.
- **YouTube**: Published to your YouTube channel as a **YouTube Short** with:
  - Snappy title with `#Shorts` (<100 characters).
  - Engaging description with Save & Subscribe CTAs.
  - High-ranking SEO tags (`#Shorts`, `#YouTubeShorts`, `#Motivation`, `#DailyWisdom`, `#Mindset`).
  - Safe-Zone branding visible above YouTube's bottom overlay.
- **Zero Interruption**: If YouTube secrets are not added yet, the script automatically skips YouTube and still posts to Instagram smoothly. Once you add the secrets, YouTube Shorts publishing turns on automatically!
