# TheKoiiBot

TheKoiiBot is a fully automated Python bot that posts informative, unique tweets about the KOII ecosystem every 2 hours. It uses Google Gemini to generate high-quality content, posts via Playwright browser automation (not the Twitter API), and includes a modern Windows 11-style dashboard to monitor status and view all posted tweets.

---

## 🚀 Features

- **Automated KOII Tweets:** Posts a new, unique, and helpful tweet about KOII every 2 hours
- **AI-Generated Content:** Uses Gemini to pull varied, up-to-date info from KOII's website, GitHub, and Twitter
- **No Twitter API Needed:** Uses Playwright browser automation to post directly on Twitter/X
- **Modern Dashboard:** Clean, Windows 11-inspired UI shows bot status, all posted tweets, and counters
- **Daily Tweet Counter:** Tracks and displays how many tweets have been sent today (resets at midnight)
- **Manual STOP Button:** Prominent red STOP badge lets you safely shut down the bot (with 10s delay and auto-close)

---

## ⚡️ Setup Instructions

### 1. Install Python 3.12
- Download and install from: https://www.python.org/downloads/
- ⚠️ Make sure to check **"Add Python to PATH"** during installation.

### 2. Clone the Repository
```
git clone https://github.com/TheKoiiBot/TheKoiiBot
cd koiibot
```

### 3. Install Python Dependencies
```
pip install -r requirements.txt
```

### 4. Install Playwright Browser Drivers
```
playwright install
```

### 5. Create a `.env` File in the Project Root
Add the following keys (replace with your credentials):
```
GEMINI_API_KEY=your_api_key
TWITTER_USERNAME=your_twitter_username
TWITTER_PASSWORD=your_twitter_password
HEADLESS=true
```

### 6. Start the Bot
- **Via Python:**
  ```
  python main.py
  ```
- **Or on Windows:**
  Double-click `start_koiibot.cmd`

---

## 🧠 Developer Notes
- **Edit Gemini Prompt:**
  - To change tweet style/content, edit the prompt in `gemini.py` (see `generate_tweet` method)
- **Dashboard Styling:**
  - UI colors, fonts, and layout can be customized in `dashboard.py` (`_build_ui` method)

---

## 🚫 Limitations & Warnings
- **No Twitter API:**
  - KoiiBot does NOT use the official Twitter API, so there are no API rate limits
- **2FA/MFA:**
  - If your Twitter account uses 2FA, you may need to use an app password or test with an account that does not have MFA enabled
- **Browser Automation:**
  - The bot controls a real browser window in the background (headless or visible, depending on `.env`)

---

## 💡 Summary
- KoiiBot is a plug-and-play, open-source solution for automated KOII ecosystem tweets with a beautiful dashboard and robust AI content generation. Follow the setup steps above and you'll be live in minutes!

## FAQ / Troubleshooting

- **Q: The bot can't find the tweet box or post button.**
  - A: Make sure your Twitter account is in English and you are not using experimental UI features. If Twitter changes their UI, update the selectors in `twitter_web.py`.
- **Q: The browser doesn't open.**
  - A: Set `HEADLESS=false` in your `.env` to see the browser window.
- **Q: Tweets are not being posted.**
  - A: Check your credentials, ensure you are not rate-limited, and review the console logs for errors.
- **Q: How do I stop the bot?**
  - A: Press `Ctrl+C` in the terminal window.

## Contributing
Pull requests and suggestions are welcome! Please open an issue for feature requests or bug reports. 