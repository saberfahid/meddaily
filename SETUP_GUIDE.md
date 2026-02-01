# Setup Guide for Medical Education App

To fully automate the posting of content to YouTube and Telegram, you need to configure your own API credentials.

## 0. GitHub Automation (100% Hands-free)
This app is pre-configured to run every day at 09:00 UTC using **GitHub Actions**. To enable this:
1. Go to your GitHub Repository > **Settings** > **Secrets and variables** > **Actions**.
2. Add the following **Repository secrets**:
   - `PAT_TOKEN`: Your GitHub Personal Access Token (with `repo` and `workflow` scopes) so the action can update the database.
   - `OPENAI_API_KEY`: (Optional) If not using Mistral.
   - `MISTRAL_API_KEY`: Your Mistral AI API Key.
   - `YOUTUBE_CLIENT_ID`: Your Google Cloud Client ID.
   - `YOUTUBE_CLIENT_SECRET`: Your Google Cloud Client Secret.
   - `YOUTUBE_REFRESH_TOKEN`: Your YouTube Refresh Token.
   - `TELEGRAM_BOT_TOKEN`: Your Telegram Bot Token.
   - `TELEGRAM_CHANNEL_ID`: Your Telegram Channel ID (e.g., `@mychannel`).

The workflow file is located at `.github/workflows/daily_post.yml`.

## 1. OpenAI / Mistral AI
The app is currently configured to use Manus's internal AI. To use your own Mistral AI key:
1. Get an API key from [Mistral AI](https://console.mistral.ai/).
2. Update the `MISTRAL_API_KEY` in the `.env` file.
3. In `ai_generator.py`, you can revert the changes to use the Mistral client.

## 2. YouTube Data API v3
1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project and enable "YouTube Data API v3".
3. Create OAuth 2.0 credentials (Desktop app) and download the JSON.
4. Rename it to `youtube_credentials.json` and place it in the project folder.
5. Run `python3 youtube_uploader.py` once to authorize. This will create `youtube_token.pickle`.
6. For headless environments, extract `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET`, and `YOUTUBE_REFRESH_TOKEN` and add them to your `.env` file.

## 3. Telegram Bot API
1. Create a bot using [@BotFather](https://t.me/BotFather) on Telegram.
2. Create a channel and add your bot as an administrator.
3. Get your `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHANNEL_ID`.
4. Add these to your `.env` file.

## 4. Running the App
Once configured, you can run the app daily:
```bash
python3 main.py
```

Or schedule it using Cron:
```bash
0 9 * * * cd /path/to/meddaily && /usr/bin/python3 main.py
```
