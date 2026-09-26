# Complete Step-by-Step Setup Guide: Daily Instagram Reels Auto-Poster

This system automatically publishes **5 unique, high-retention Instagram Reels every day** using **GitHub Actions + FFmpeg + Instagrapi / Meta Graph API**.

### 3 High-Retention Reel Formats Published Automatically:

1. 🎙️ **VOICEOVER REELS (Spoken Audio + Music)**:
   - Studio-grade AI motivational narrator recites the quote with inspiring cadence and dramatic pauses.
   - Background lo-fi/ambient music is automatically ducked underneath and swells at the end.
   - Uses Microsoft Edge Neural Voices (`en-US-ChristopherNeural`, `en-US-GuyNeural`, `en-GB-RyanNeural`, `en-US-EricNeural`, `en-US-JennyNeural`).

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

| Slot | Time (IST) | Schedule (UTC) | Content Focus | Format | Theme / Atmosphere |
|---|---|---|---|---|---|
| **Reel 1** | **07:00 AM** | 01:30 UTC | Morning Mindset & Ambition | 🎙️ **VOICEOVER** | Golden Mountain Sunrise, Misty Forest |
| **Reel 2** | **10:30 AM** | 05:00 UTC | Relentless Focus & Work Ethic | 🎬 **SHORT VIDEO** | Motion Video / Ocean Waves, Modern Architecture |
| **Reel 3** | **01:30 PM** | 08:00 UTC | Resilience & Overcoming Doubts | 🖼️ **TEXT POSTER** | Sahara Desert Dunes, Emerald Waterfall |
| **Reel 4** | **06:00 PM** | 12:30 UTC | Evening Discipline & Reflection | 🎙️ **VOICEOVER** | Twilight City Skyline, Coastal Golden Dusk |
| **Reel 5** | **09:30 PM** | 16:00 UTC | Night Peace & Self-Belief | 🎬 **SHORT VIDEO** | Motion Video / Starry Milky Way Lake |

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
2. Go to the **Actions** tab → **Auto Instagram Reels Daily Publisher (5 Reels/Day)**.
3. Click **Run workflow**.
