#!/bin/bash
# Medical Education App Deployment Script

echo "🚀 Deploying Medical Education App..."

# Create directories
sudo mkdir -p /opt/medical-edu-app
sudo chown $USER:$USER /opt/medical-edu-app

# Copy files
echo "📋 Copying application files..."
cp *.py /opt/medical-edu-app/
cp medical_education.db /opt/medical-edu-app/
cp -r videos /opt/medical-edu-app/
cp youtube*.json /opt/medical-edu-app/ 2>/dev/null || true
cp youtube*.pickle /opt/medical-edu-app/ 2>/dev/null || true

# Create environment file
echo "🔑 Setting up environment variables..."
cat > /opt/medical-edu-app/.env << EOF
OPENAI_API_KEY=l3pdbDohuqIBhQCPJWw7BkZ9QUtFRsWJ
TELEGRAM_BOT_TOKEN=8574102270:AAF_Lyi4-oLbx6isrGEPmvBSuHTPNBI56NQ
TELEGRAM_CHANNEL_ID=@medianly_sb
EOF

# Install dependencies
echo "📦 Installing dependencies..."
sudo apt update
sudo apt install -y python3.11 python3-pip ffmpeg libcairo2-dev pkg-config python3-dev

pip3 install openai gtts Pillow requests google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client edge-tts

# Install as systemd service
echo "⚙️ Installing systemd service..."
sudo cp medical-edu.service /etc/systemd/system/
sudo cp medical-edu.timer /etc/systemd/system/

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable medical-edu.timer
sudo systemctl start medical-edu.timer

# Test run
echo "🧪 Testing deployment..."
cd /opt/medical-edu-app
python3.11 main.py

echo "✅ Deployment complete!"
echo "📅 Daily execution scheduled for 9:00 AM"
echo "📊 Check status with: systemctl status medical-edu.timer"
echo "📋 View logs with: journalctl -u medical-edu.service -f"