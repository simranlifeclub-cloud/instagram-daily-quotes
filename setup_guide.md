# Complete Step-by-Step Setup Guide: Daily Instagram Reels Auto-Poster

This system automatically publishes **5 unique, high-retention Instagram Reels every day** using **GitHub Actions + FFmpeg + Instagrapi / Meta Graph API**.

### 3 High-Retention Reel Formats Published Automatically:

1. 🎙️ **VOICEOVER REELS (Spoken Audio + Music)**:
   - Studio-grade AI motivational narrator recites the quote with inspiring cadence and dramatic pauses.
   - Background lo-fi/ambient music is automatically ducked underneath and swells at the end.
   - Automatically supports English & Hindi voices:
     - English: (`en-US-ChristopherNeural`, `en-US-GuyNeural`, `en-GB-RyanNeural`, `en-US-EricNeural`, `en-US-JennyNeural`).
     - Hindi: (`hi-IN-MadhurNeural` - deep & grounded motivational male, `hi-IN-SwaraNeural` - serene & clear inspiring female).
   - Audio duration dynamically scales for bigger quotes so speech is never cut off.

2. 🎬 **SHORT VIDEO REELS (Full Motion Video Backgrounds)**:
   - Full motion 9:16 vertical video background (flowing water, moving clouds, ocean waves, city time-lapse).
   - Semi-transparent glassmorphic quote card overlaid cleanly on top of the moving footage.
   - Syncs with background music.
   - Drop any `.mp4` into `assets/videos/` and it will automatically be included in rotation!

3. 🖼️ **TEXT & POSTER REELS (Aesthetic Landscape + Luxury Theme)**:
   - Curated high-resolution landscape photography from 9+ diverse nature and city aesthetics.
   - 8 complementary glassmorphic color themes (24k Gold, Emerald Mint, Cyan Horizon, Sunset Ember, Royal Amethyst, etc.).
   - Cinematic Ken Burns camera motion (Slow Push-In, Reveal Pull-Back, Horizon Pan Up/Down, Ambient Pulse).

---

### Daily Schedule & Format Rotation (Indian Standard Time - IST)

To prevent self-cannibalization of views and give each Reel 12 hours of runway to trigger non-follower recommendations, posting is tuned to the 2 peak golden hours:

| Slot | Time (IST) | Schedule (UTC) | Content Focus | Format | Retention Strategy |
|---|---|---|---|---|---|
| **Reel 1 (Morning)** | **07:30 AM** | 02:00 UTC | Morning Mindset & Purpose | 🎬 **SHORT VIDEO** / 🎙️ **VOICEOVER** | 6–8s viral loop for 100%+ watch time |
| **Reel 2 (Evening)** | **07:30 PM** | 14:00 UTC | Evening Reflection & Inner Peace | 🎬 **SHORT VIDEO** / 🎙️ **VOICEOVER** | Spoken wisdom & calm lo-fi aesthetic |

---

### Adding Your Own Custom Media (Optional)

#### How to Add Custom Videos:
Simply drop any vertical or horizontal video (`.mp4`, `.mov`, `.webm`) into:
```
assets/videos/
```
The bot will automatically loop, scale, and crop it to vertical 1080x1920 (9:16) with floating quote text overlaid!

#### How to Add Custom Background Images:
Drop any vertical 1080x1920 image (`.jpg`, `.jpeg`, `.png`, `.webp`) into:
```
assets/backgrounds/
```

#### How to Add Custom Music Tracks:
Drop any audio track (`.mp3`, `.wav`, `.m4a`, `.ogg`) into:
```
assets/audio/
```

---

### 8 Luxury Aesthetic Visual Themes

1. **`GOLDEN_LUXURY`**: 24k Obsidian & Gold glass card, warm champagne accents.
2. **`EMERALD_MINT`**: Deep forest glass card, mint green & sage highlights.
3. **`CYAN_HORIZON`**: Deep oceanic navy glass card, electric cyan & ice-blue accents.
4. **`SUNSET_EMBER`**: Twilight bronze glass card, warm rose gold & apricot peach tones.
5. **`ROYAL_AMETHYST`**: Midnight velvet purple glass card, lilac & lavender luminescence.
6. **`FROSTED_SILVER`**: Modern arctic frosted glass card, platinum chrome borders & crisp typography.
7. **`DESERT_TERRACOTTA`**: Warm espresso glass card, golden terracotta & dune sand accents.
8. **`MONOCHROME_SLATE`**: Brutalist graphite slate card, diamond silver highlights.

---

### GitHub Actions Deployment
 
All daily reels are generated in the cloud using GitHub Actions.
To test manually anytime:
1. Open your repository on GitHub.
2. Go to the **Actions** tab → **Auto Instagram Reels Daily Publisher (2 Reels/Day - Growth Optimized)**.
3. Click **Run workflow**.

---

### Local Testing & Custom Triggers

Test reel and cover generation locally or with dry-run mode:
```bash
# Test a specific quote
python post_with_instagrapi.py --dry-run --quote-id 23

# Test Hindi quote rendering
python post_with_instagrapi.py --dry-run --quote-id 32

# Force Hindi or English rotation
python post_with_instagrapi.py --dry-run --lang hi
python post_with_instagrapi.py --dry-run --lang en
```

---

### 🚀 Instagram Algorithm & Follower Conversion Blueprint

To turn Reel views into loyal followers, the algorithm relies on specific viewer behaviors:

#### 1. The 6–8s "Viral Loop" Mechanism
* **The Math:** Viewers take approximately 4–6 seconds to read a 15–20 word inspirational quote. 
* By keeping the video length at **6.5–8.0 seconds**, the reel naturally loops into a second view while the viewer is still absorbing the message.
* This results in an **Average Percentage Watched of >100%**, which triggers Instagram's recommendation engine to push the Reel to non-followers.

#### 2. Saves & DM Shares are King
* Instagram weighs **Saves** and **DM Shares** up to 5x higher than likes or comments for distribution.
* Every automated caption now ends with clear algorithmic prompts:
  * *"📌 Save this reminder for when you need quiet strength."*
  * *"↗️ Send this to someone who needs to hear it today."*
  * *"Follow @simranlifeclub for daily wisdom, clarity & peace."*

#### 3. Branding in the "Safe Zone"
* Instagram Reels place account handles, captions, audio tickers, and action buttons in the bottom 250px (`y=1650` to `1920`).
* Our `@simranlifeclub` branding is placed at `y=1580`, ensuring it is 100% visible and un-obscured on all phone screens.

#### 4. The Native Trending Audio Trick
* Reels with "Original Audio" often get lower default reach than Reels tagged with an Instagram Trending sound (arrow ↗️ icon).
* **Pro-Tip:** If a reel starts picking up traction, open it in the Instagram mobile app, tap **Edit** or use the audio replacer to select a trending ambient track with volume set to 3–5%. The Reel will immediately appear under the trending audio hashtag page!

#### 5. Profile Optimization (Convert Visitors into Followers)
When someone taps on your profile from a viral reel, you have 3 seconds to convert them:
* **Bio Line 1 (Niche Promise):** Daily mental resets, inner peace & quiet strength.
* **Bio Line 2 (Audience):** For thinkers, builders & seekers of clarity.
* **Bio Line 3 (CTA):** Follow @simranlifeclub to elevate your daily mindset.
* **Pinned Posts:** Pin your top 3 highest-quality, most inspiring reels to the top of your grid.
