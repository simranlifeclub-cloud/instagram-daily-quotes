# Complete Step-by-Step Setup Guide: 100% Free Daily Instagram Auto-Posting

This guide walks you through setting up your automated Instagram publishing pipeline using **GitHub Actions + Meta Graph API**. Once configured, this runs completely in the cloud every morning even when your Mac is turned off.

---

### Step 1: Switch Instagram Account to Professional (Free, 30 seconds)
1. Open the **Instagram** app on your phone.
2. Go to your **Profile** → Tap the ☰ menu (top right) → **Settings and privacy**.
3. Scroll down to **Account type and tools** → Tap **Switch to professional account**.
4. Select **Creator** (or Business) and finish the quick prompts.

---

### Step 2: Link a Facebook Page (Free, 1 minute)
1. In the Instagram app, go to **Edit profile**.
2. Under *Public business information*, tap **Page**.
3. Either connect an existing Facebook page or tap **Create Facebook Page** (e.g. "My Daily Motivation").
4. Complete the link.

---

### Step 3: Get Your Free Meta API Credentials (3 minutes)

1. Open [developers.facebook.com](https://developers.facebook.com/) and log in with your Facebook account.
2. Click **My Apps** (top right) → **Create App**.
3. Choose **Other** → Next → Choose **Business** as the app type → Next.
4. Enter an App Name (e.g., `DailyQuoteBot`) and click **Create App**.
5. Once in your app dashboard:
   - Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer/).
   - In the top-right dropdown, select your newly created app (`DailyQuoteBot`).
   - In the **User or Page** dropdown, select **Get User Access Token**.
   - Under **Permissions**, add these 4 permissions:
     - `instagram_basic`
     - `instagram_content_publish`
     - `pages_show_list`
     - `pages_read_engagement`
   - Click **Generate Access Token** and approve the popup.

6. **Find your Instagram Account ID (`IG_USER_ID`)**:
   - In the Graph API Explorer query box, run:
     ```text
     GET me/accounts?fields=name,instagram_business_account
     ```
   - In the JSON response, locate your `instagram_business_account.id` (a numeric string like `17841405829102938`). This is your **`IG_USER_ID`**.

7. **Generate a 60-Day Long-Lived Token (`META_ACCESS_TOKEN`)**:
   - Go to the [Meta Access Token Debugger](https://developers.facebook.com/tools/debug/accesstoken/).
   - Paste the short-lived token from the Explorer → Click **Debug**.
   - Scroll down to the bottom and click **Extend Access Token**.
   - Copy the resulting long string. This is your **`META_ACCESS_TOKEN`**.

---

### Step 4: Add Secrets to Your GitHub Repository (1 minute)

1. Create a new GitHub repository (can be **Private** or Public).
2. Push the files inside `Instagram_Auto_Poster/` to your repository:
   ```bash
   cd Instagram_Auto_Poster
   git init
   git add .
   git commit -m "feat: setup instagram auto poster"
   git branch -M main
   git remote add origin https://github.com/<YOUR_USERNAME>/<YOUR_REPO_NAME>.git
   git push -u origin main
   ```
3. In your GitHub repository:
   - Go to **Settings** → **Secrets and variables** → **Actions**.
   - Click **New repository secret**.
   - Add Secret 1:
     - Name: `IG_USER_ID`
     - Value: *(Your numeric Instagram account ID from Step 3.6)*
   - Add Secret 2:
     - Name: `META_ACCESS_TOKEN`
     - Value: *(Your Long-Lived Access Token from Step 3.7)*

---

### Step 5: Test & Activate!

1. In your GitHub repository, click the **Actions** tab.
2. Under workflows on the left, click **Daily Motivational Instagram Post**.
3. Click the **Run workflow** dropdown on the right → Click **Run workflow**.
4. The workflow will spin up, render today's motivational graphic, and publish it directly to your Instagram profile in ~20 seconds!
5. From then on, GitHub Actions will automatically run every morning at **08:00 AM IST (02:30 UTC)** without any manual intervention!
