# Medical Education App - Cloud Deployment Guide

## 🚀 Deployment Steps

### 1. Server Setup
```bash
# Connect to your Linux server (Ubuntu 22.04 recommended)
ssh user@your-server-ip
```

### 2. Install Dependencies
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and required packages
sudo apt install python3.11 python3-pip ffmpeg libcairo2-dev pkg-config python3-dev -y

# Install Python libraries
pip3 install openai gtts Pillow requests google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client edge-tts
```

### 3. Deploy Application
```bash
# Create application directory
sudo mkdir -p /opt/medical-edu-app
sudo chown $USER:$USER /opt/medical-edu-app

# Upload all files to server
# - All .py files
# - medical_education.db
# - videos/ directory
# - youtube_credentials.json
# - youtube_token.pickle
```

### 4. Configure Environment
```bash
# Create environment file
cat > /opt/medical-edu-app/.env << EOF
OPENAI_API_KEY=l3pdbDohuqIBhQCPJWw7BkZ9QUtFRsWJ
TELEGRAM_BOT_TOKEN=8574102270:AAF_Lyi4-oLbx6isrGEPmvBSuHTPNBI56NQ
TELEGRAM_CHANNEL_ID=@medianly_sb
EOF
```

### 5. Setup Systemd Service
```bash
# Copy service files
sudo cp medical-edu.service /etc/systemd/system/
sudo cp medical-edu.timer /etc/systemd/system/

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable medical-edu.timer
sudo systemctl start medical-edu.timer
```

### 6. Test Deployment
```bash
# Run manually to test
cd /opt/medical-edu-app
python3.11 main.py

# Check service status
systemctl status medical-edu.timer

# View logs
journalctl -u medical-edu.service -f
```

## 📅 Daily Automation

The app will automatically run daily at 9:00 AM and:
- 🩺 Generate new medical content with Mistral AI
- 🎥 Create educational videos
- 📤 Post to Telegram channel (@medianly_sb)
- 📺 Upload to YouTube (when quota available)

## 📊 Monitoring

```bash
# Check next execution time
systemctl list-timers

# View recent logs
journalctl -u medical-edu.service --since "1 hour ago"

# Check database stats
cd /opt/medical-edu-app
python3.11 main.py stats
```

## 🔧 Troubleshooting

```bash
# If service fails to start
sudo systemctl status medical-edu.service
sudo journalctl -u medical-edu.service --no-pager

# Restart service
sudo systemctl restart medical-edu.timer

# Manual run for debugging
cd /opt/medical-edu-app
python3.11 main.py
```

## 💰 Cost Estimate

- **Server**: $10-20/month (2GB RAM VPS)
- **API Costs**: $5-15/month (Mistral API)
- **Storage**: $2-5/month (videos + backups)
- **Total**: ~$17-40/month

## 🛡️ Security Notes

- Keep API keys in .env file (never in code)
- Use firewall to restrict access
- Regular system updates
- Monitor logs for errors

## ✅ Success Indicators

When deployed successfully, you'll see:
- Daily posts in @medianly_sb Telegram channel
- New videos in your YouTube channel
- Database growing with new cases
- No error logs in journalctl