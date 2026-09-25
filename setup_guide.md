# Complete Step-by-Step Setup Guide: Daily Instagram Reels Auto-Poster

This system automatically publishes **5 unique, high-retention Instagram Reels every day** using **GitHub Actions + FFmpeg + Instagrapi / Meta Graph API**.

Every reel features:
- **Different Background Every Time**: Rotates across 9+ curated aesthetic 9:16 vertical landscapes matching time-of-day slots (or auto-fetches online).
- **Different Music Every Time**: Seamlessly rotates between 6+ bundled royalty-free tracks, user custom MP3s, and an 8-style algorithmic music composer.
- **Fresh Visual Look Every Time**: Automatically pairs each reel with one of 8 luxurious glassmorphic themes, custom typography palettes, dynamic quote marks, and cinematic Ken Burns camera motion.
- **Zero Consecutive Repetitions**: Backgrounds, audio tracks, and quotes are tracked in `history.json` and cycle systematically.

---

### Daily Schedule (Indian Standard Time - IST)

| Slot | Time (IST) | Schedule (UTC) | Content Focus | Atmosphere / Preferred Background |
|---|---|---|---|---|
| **Reel 1** | **07:00 AM** | 01:30 UTC | Morning Mindset & Ambition | Golden Mountain Sunrise, Misty Forest |
| **Reel 2** | **10:30 AM** | 05:00 UTC | Relentless Focus & Work Ethic | Powerful Ocean Waves, Minimalist Architecture |
| **Reel 3** | **01:30 PM** | 08:00 UTC | Resilience & Overcoming Doubts | Sahara Desert Dunes, Emerald Waterfall |
| **Reel 4** | **06:00 PM** | 12:30 UTC | Evening Discipline & Reflection | Twilight City Skyline, Coastal Golden Dusk |
| **Reel 5** | **09:30 PM** | 16:00 UTC | Night Peace & Self-Belief | Starry Milky Way Lake, Moody City Bokeh |

---

### Adding Your Own Backgrounds & Music (Optional)

#### How to Add New Backgrounds:
Simply drop any vertical `1080x1920` image (`.jpg`, `.jpeg`, `.png`, `.webp`) into:
```
assets/backgrounds/
```
The bot will automatically discover it, add it to the rotation, and select complementary visual themes!

#### How to Add New Audio / Music:
Simply drop any royalty-free background music track (`.mp3`, `.wav`, `.m4a`, `.ogg`) into:
```
assets/audio/
```
The bot will automatically pick from your audio library, trim it to 12s, and apply a 1.2s fade-in and 1.8s fade-out so it loops seamlessly on Instagram Reels!

---

### 8 Luxury Aesthetic Visual Themes

Each reel dynamically adapts to one of 8 complementary themes:
1. **`GOLDEN_LUXURY`**: 24k Obsidian & Gold glass card, warm champagne accents.
2. **`EMERALD_MINT`**: Deep spruce glass card, mint green & sage highlights.
3. **`CYAN_HORIZON`**: Deep oceanic navy glass card, electric cyan & ice-blue accents.
4. **`SUNSET_EMBER`**: Twilight bronze glass card, warm rose gold & apricot peach tones.
5. **`ROYAL_AMETHYST`**: Midnight velvet purple glass card, lilac & lavender luminescence.
6. **`FROSTED_SILVER`**: Modern arctic frosted glass card, platinum chrome borders & crisp typography.
7. **`DESERT_TERRACOTTA`**: Warm espresso glass card, golden terracotta & dune sand accents.
8. **`MONOCHROME_SLATE`**: Brutalist graphite slate card, diamond silver highlights.

---

### Step 1: Switch Instagram Account to Professional (Free, 30 seconds)
1. Open the **Instagram** app on your phone.
2. Go to your **Profile** → Tap the ☰ menu (top right) → **Settings and privacy**.
3. Scroll down to **Account type and tools** → Tap **Switch to professional account**.
4. Select **Creator** (or Business) and finish the quick prompts.

---

### Step 2: Configure Authentication Secrets in GitHub

Go to your repository on GitHub:
**Settings** → **Secrets and variables** → **Actions** → **New repository secret**.

Add the following secret:
- **`IG_SESSIONID`** *(Recommended - 100% bypasses Instagram 429 login limits)*:
  1. Open [instagram.com](https://www.instagram.com) on your computer browser and log in.
  2. Press `F12` (or Right-click → **Inspect**), go to **Application** (or **Storage**) → **Cookies** → `https://www.instagram.com`.
  3. Find the cookie named **`sessionid`**, copy its value (a long alphanumeric string), and paste it as `IG_SESSIONID`.

- *(Optional Fallback)* **`IG_USERNAME`** & **`IG_PASSWORD`**:
  Your Instagram login username and password.

---

### Step 3: Test & Trigger Anytime!

1. In your GitHub repository, click the **Actions** tab.
2. Under workflows on the left, click **Auto Instagram Reels Daily Publisher (5 Reels/Day)**.
3. Click the **Run workflow** dropdown on the right → Click **Run workflow**.
4. The workflow will:
   - Pick the next unposted quote matching the current IST time slot.
   - Select an unposted background image and complementary visual theme.
   - Select an unposted audio soundtrack or synthesize a fresh musical style.
   - Render a 1080x1920 MP4 Reel with cinematic camera motion.
   - Upload the reel with custom cover card thumbnail and optimized caption/hashtags directly to Instagram!
   - Update `history.json` and push it back to GitHub to prevent repetition.
