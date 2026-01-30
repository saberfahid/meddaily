# Quick Start Guide

Get your Medical Education App running in under 30 minutes!

## Prerequisites Checklist

Before you begin, ensure you have:

- [ ] Linux server (Ubuntu 22.04 recommended) or macOS
- [ ] Python 3.11+ installed
- [ ] FFmpeg installed
- [ ] OpenAI/Mistral AI API key
- [ ] YouTube OAuth2 credentials
- [ ] Telegram bot token and channel ID

## Step-by-Step Setup

### 1. Download and Extract (2 minutes)

```bash
# Download the project archive
# Extract to your desired location
cd /opt
sudo mkdir medical-edu-app
sudo chown $USER:$USER medical-edu-app
cd medical-edu-app

# Upload/extract all project files here
```

### 2. Install Dependencies (5 minutes)

```bash
# Install system packages
sudo apt update
sudo apt install python3.11 python3-pip ffmpeg -y

# Install Python packages
pip3 install -r requirements.txt
```

Or use the automated setup script:

```bash
chmod +x setup.sh
./setup.sh
```

### 3. Configure Environment Variables (5 minutes)

Create a `.env` file or export variables:

```bash
# Create .env file
cat > .env << 'EOF'
# OpenAI/Mistral API
OPENAI_API_KEY=your_openai_api_key_here

# YouTube API
YOUTUBE_CLIENT_ID=your_youtube_client_id
YOUTUBE_CLIENT_SECRET=your_youtube_client_secret
YOUTUBE_REFRESH_TOKEN=your_youtube_refresh_token

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHANNEL_ID=@your_channel_or_chat_id
EOF

# Load environment variables
source .env
export $(cat .env | xargs)
```

### 4. Import Medical Topics (2 minutes)

```bash
# Import topics from the provided file
python3 topic_ingestion.py medicaltopics.txt.txt

# Verify import
python3 main.py stats
```

Expected output:
```
Total Subjects: 4
Total Topics: 1076
Topics by Subject:
  Internal Medicine: 192
  Surgery: 225
  Pediatrics: 511
  Gynecology: 148
```

### 5. Test the System (3 minutes)

```bash
# Run a test workflow
python3 main.py
```

This will:
1. Select a subject and topic
2. Generate content with AI
3. Create a video
4. Upload to YouTube
5. Post to Telegram
6. Update database

Watch for ✅ success indicators!

### 6. Set Up Daily Automation (5 minutes)

#### Option A: Cron Job (Linux)

```bash
# Edit crontab
crontab -e

# Add this line (runs daily at 9 AM)
0 9 * * * cd /opt/medical-edu-app && /usr/bin/python3 main.py >> /var/log/medical-edu.log 2>&1
```

#### Option B: Systemd Timer (Linux)

```bash
# Create service file
sudo tee /etc/systemd/system/medical-edu.service << 'EOF'
[Unit]
Description=Medical Education Content Generator
After=network.target

[Service]
Type=oneshot
User=$USER
WorkingDirectory=/opt/medical-edu-app
EnvironmentFile=/opt/medical-edu-app/.env
ExecStart=/usr/bin/python3 /opt/medical-edu-app/main.py

[Install]
WantedBy=multi-user.target
EOF

# Create timer file
sudo tee /etc/systemd/system/medical-edu.timer << 'EOF'
[Unit]
Description=Medical Education Daily Timer

[Timer]
OnCalendar=daily
OnCalendar=09:00:00
Persistent=true

[Install]
WantedBy=timers.target
EOF

# Enable and start timer
sudo systemctl daemon-reload
sudo systemctl enable medical-edu.timer
sudo systemctl start medical-edu.timer

# Check timer status
sudo systemctl status medical-edu.timer
```

#### Option C: macOS (launchd)

```bash
# Create plist file
cat > ~/Library/LaunchAgents/com.medicaledu.daily.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.medicaledu.daily</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3</string>
        <string>/opt/medical-edu-app/main.py</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>9</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>/tmp/medical-edu.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/medical-edu-error.log</string>
</dict>
</plist>
EOF

# Load the job
launchctl load ~/Library/LaunchAgents/com.medicaledu.daily.plist
```

## Verification

### Check Everything is Working

```bash
# 1. Check statistics
python3 main.py stats

# 2. Check logs
tail -f /var/log/medical-edu.log

# 3. Check videos directory
ls -lh videos/

# 4. Check database
sqlite3 medical_education.db "SELECT COUNT(*) FROM cases;"
```

### Test YouTube Upload

```bash
# Check latest upload
# Visit your YouTube channel and verify the video appears
```

### Test Telegram Post

```bash
# Check your Telegram channel
# Verify the post appears with correct formatting
```

## Troubleshooting

### Issue: "ModuleNotFoundError"

```bash
pip3 install -r requirements.txt
```

### Issue: "FFmpeg not found"

```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg
```

### Issue: "YouTube authentication failed"

```bash
# Verify credentials are set correctly
echo $YOUTUBE_CLIENT_ID
echo $YOUTUBE_CLIENT_SECRET
echo $YOUTUBE_REFRESH_TOKEN

# Re-export if needed
source .env
```

### Issue: "Telegram bot cannot send messages"

```bash
# Verify bot is admin in channel
# Check channel ID format:
# - Public: @channelname
# - Private: -1001234567890

# Test connection
python3 telegram_poster.py
```

### Issue: "Database is locked"

```bash
# Check for running instances
ps aux | grep main.py

# Kill if needed
pkill -f main.py

# Try again
python3 main.py
```

## Next Steps

Once everything is working:

1. **Monitor Daily Execution**
   - Check logs daily for first week
   - Verify content quality
   - Monitor API usage

2. **Set Up Backups**
   ```bash
   # Create backup script
   cat > backup.sh << 'EOF'
   #!/bin/bash
   DATE=$(date +%Y%m%d)
   cp medical_education.db backups/medical_education_$DATE.db
   tar -czf backups/videos_$DATE.tar.gz videos/
   EOF
   
   chmod +x backup.sh
   
   # Add to crontab (weekly backup)
   0 0 * * 0 /opt/medical-edu-app/backup.sh
   ```

3. **Set Up Monitoring**
   - Use UptimeRobot or similar for uptime monitoring
   - Set up email alerts for failures
   - Monitor disk space

4. **Review and Optimize**
   - Review content quality after first week
   - Adjust AI prompts if needed
   - Optimize video generation if slow

## Getting Help

If you encounter issues:

1. Check `README.md` for detailed documentation
2. Review `TESTING.md` for troubleshooting procedures
3. Check `cloudflare_deployment.md` for deployment options
4. Review error logs: `tail -100 /var/log/medical-edu.log`

## Success Checklist

- [ ] All dependencies installed
- [ ] Environment variables configured
- [ ] Topics imported (1,076 topics)
- [ ] Test workflow completed successfully
- [ ] Video created and uploaded to YouTube
- [ ] Post appeared on Telegram
- [ ] Daily automation configured
- [ ] Backups set up
- [ ] Monitoring in place

## You're Done! 🎉

Your Medical Education App is now running automatically!

It will:
- Generate new content every day
- Create professional videos
- Upload to YouTube
- Post to Telegram
- Track everything in the database

**No manual work required!**

---

**Need more details?** See the full documentation in `README.md`

**Want to customize?** Check the code comments and modify as needed

**Ready to scale?** Review `cloudflare_deployment.md` for advanced options
