# Cloudflare Deployment Guide

## Overview

This guide explains how to deploy the Medical Education App on Cloudflare Workers with scheduled cron triggers for daily automated content generation.

**Important Note**: Cloudflare Workers has limitations for this use case:
- Workers have a 50ms CPU time limit (not suitable for video generation)
- Workers don't support long-running processes
- Python support is limited

**Recommended Alternative**: Use **Cloudflare Workers + External Server** hybrid approach or deploy on a traditional VPS/cloud server with cron jobs.

## Deployment Options

### Option 1: VPS/Cloud Server (Recommended)

Deploy on a traditional server (AWS EC2, DigitalOcean, Linode, etc.) with cron scheduling.

#### Requirements
- Ubuntu 22.04 or similar Linux server
- Python 3.11+
- FFmpeg installed
- Persistent storage for database and videos
- Stable internet connection

#### Setup Steps

1. **Install Dependencies**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install Python and pip
   sudo apt install python3.11 python3-pip -y
   
   # Install FFmpeg
   sudo apt install ffmpeg -y
   
   # Install system dependencies
   sudo apt install libcairo2-dev pkg-config python3-dev -y
   ```

2. **Clone/Upload Application**
   ```bash
   # Create application directory
   mkdir -p /opt/medical-edu-app
   cd /opt/medical-edu-app
   
   # Upload all Python files
   # - database.py
   # - ai_generator.py
   # - video_generator_lite.py
   # - youtube_uploader.py
   # - telegram_poster.py
   # - main.py
   # - topic_ingestion.py
   
   # Upload database
   # - medical_education.db
   ```

3. **Install Python Dependencies**
   ```bash
   sudo pip3 install openai gtts Pillow requests google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
   ```

4. **Set Environment Variables**
   ```bash
   # Create environment file
   sudo nano /opt/medical-edu-app/.env
   ```
   
   Add the following:
   ```bash
   # OpenAI/Mistral API
   OPENAI_API_KEY=your_openai_api_key_here
   
   # YouTube API
   YOUTUBE_CLIENT_ID=your_youtube_client_id
   YOUTUBE_CLIENT_SECRET=your_youtube_client_secret
   YOUTUBE_REFRESH_TOKEN=your_youtube_refresh_token
   
   # Telegram Bot
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   TELEGRAM_CHANNEL_ID=@your_channel_or_chat_id
   ```

5. **Create Systemd Service (Optional)**
   ```bash
   sudo nano /etc/systemd/system/medical-edu.service
   ```
   
   ```ini
   [Unit]
   Description=Medical Education Content Generator
   After=network.target
   
   [Service]
   Type=oneshot
   User=root
   WorkingDirectory=/opt/medical-edu-app
   EnvironmentFile=/opt/medical-edu-app/.env
   ExecStart=/usr/bin/python3.11 /opt/medical-edu-app/main.py
   StandardOutput=journal
   StandardError=journal
   
   [Install]
   WantedBy=multi-user.target
   ```

6. **Setup Cron Job**
   ```bash
   sudo crontab -e
   ```
   
   Add daily execution at 9 AM:
   ```bash
   0 9 * * * cd /opt/medical-edu-app && /usr/bin/python3.11 main.py >> /var/log/medical-edu.log 2>&1
   ```
   
   Or use systemd timer:
   ```bash
   sudo nano /etc/systemd/system/medical-edu.timer
   ```
   
   ```ini
   [Unit]
   Description=Medical Education Daily Timer
   
   [Timer]
   OnCalendar=daily
   OnCalendar=09:00:00
   Persistent=true
   
   [Install]
   WantedBy=timers.target
   ```
   
   Enable timer:
   ```bash
   sudo systemctl enable medical-edu.timer
   sudo systemctl start medical-edu.timer
   ```

7. **Test Execution**
   ```bash
   cd /opt/medical-edu-app
   python3.11 main.py
   ```

### Option 2: Cloudflare Workers + External Trigger

Use Cloudflare Workers as a lightweight trigger that calls an external API endpoint on your server.

#### Architecture
1. Cloudflare Worker runs on schedule (cron trigger)
2. Worker makes HTTP request to your server's API endpoint
3. Server executes the main workflow
4. Server returns status to Worker

#### Cloudflare Worker Code

Create `worker.js`:
```javascript
export default {
  async scheduled(event, env, ctx) {
    // Trigger the external server
    try {
      const response = await fetch(env.SERVER_ENDPOINT, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${env.API_SECRET}`
        },
        body: JSON.stringify({
          trigger: 'daily_workflow',
          timestamp: new Date().toISOString()
        })
      });
      
      const result = await response.json();
      console.log('Workflow triggered:', result);
      
    } catch (error) {
      console.error('Error triggering workflow:', error);
    }
  }
}
```

Create `wrangler.toml`:
```toml
name = "medical-edu-trigger"
main = "worker.js"
compatibility_date = "2024-01-01"

[triggers]
crons = ["0 9 * * *"]  # Daily at 9 AM UTC

[vars]
SERVER_ENDPOINT = "https://your-server.com/api/trigger"

[[env.production.vars]]
API_SECRET = "your-secret-key-here"
```

Deploy:
```bash
npm install -g wrangler
wrangler login
wrangler deploy
```

#### Server API Endpoint

Create simple Flask API on your server:

```python
# api_server.py
from flask import Flask, request, jsonify
import subprocess
import os

app = Flask(__name__)

API_SECRET = os.getenv('API_SECRET', 'your-secret-key-here')

@app.route('/api/trigger', methods=['POST'])
def trigger_workflow():
    # Verify authorization
    auth_header = request.headers.get('Authorization')
    if not auth_header or auth_header != f'Bearer {API_SECRET}':
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Run workflow in background
    try:
        subprocess.Popen([
            'python3.11', '/opt/medical-edu-app/main.py'
        ], cwd='/opt/medical-edu-app')
        
        return jsonify({
            'status': 'triggered',
            'message': 'Workflow started successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

Run with gunicorn:
```bash
pip3 install flask gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 api_server:app
```

### Option 3: GitHub Actions (Alternative)

Use GitHub Actions as a free cron scheduler.

Create `.github/workflows/daily-content.yml`:
```yaml
name: Daily Medical Content Generation

on:
  schedule:
    - cron: '0 9 * * *'  # Daily at 9 AM UTC
  workflow_dispatch:  # Manual trigger

jobs:
  generate-content:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y ffmpeg
          pip install openai gtts Pillow requests google-auth google-auth-oauthlib google-api-python-client
      
      - name: Run workflow
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          YOUTUBE_CLIENT_ID: ${{ secrets.YOUTUBE_CLIENT_ID }}
          YOUTUBE_CLIENT_SECRET: ${{ secrets.YOUTUBE_CLIENT_SECRET }}
          YOUTUBE_REFRESH_TOKEN: ${{ secrets.YOUTUBE_REFRESH_TOKEN }}
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHANNEL_ID: ${{ secrets.TELEGRAM_CHANNEL_ID }}
        run: |
          python main.py
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: generated-content
          path: |
            videos/
            medical_education.db
```

## Environment Variables Reference

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `OPENAI_API_KEY` | OpenAI/Mistral API key | Yes | `sk-...` |
| `YOUTUBE_CLIENT_ID` | YouTube OAuth client ID | Yes | `123456789.apps.googleusercontent.com` |
| `YOUTUBE_CLIENT_SECRET` | YouTube OAuth client secret | Yes | `GOCSPX-...` |
| `YOUTUBE_REFRESH_TOKEN` | YouTube OAuth refresh token | Yes | `1//...` |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token | Yes | `123456789:ABC...` |
| `TELEGRAM_CHANNEL_ID` | Telegram channel/group ID | Yes | `@channelname` or `-1001234567890` |

## Database Persistence

### Local Storage
- Database file: `medical_education.db`
- Videos directory: `videos/`
- Ensure regular backups

### Cloud Storage (Optional)
- Upload database to S3/R2 after each run
- Download before execution
- Sync videos to cloud storage

Example backup script:
```bash
#!/bin/bash
# backup.sh

# Backup database
aws s3 cp medical_education.db s3://your-bucket/backups/medical_education_$(date +%Y%m%d).db

# Sync videos
aws s3 sync videos/ s3://your-bucket/videos/

# Keep only last 30 days of backups
aws s3 ls s3://your-bucket/backups/ | while read -r line; do
  createDate=$(echo $line|awk {'print $1" "$2'})
  createDate=$(date -d "$createDate" +%s)
  olderThan=$(date -d "30 days ago" +%s)
  if [[ $createDate -lt $olderThan ]]; then
    fileName=$(echo $line|awk {'print $4'})
    if [[ $fileName != "" ]]; then
      aws s3 rm s3://your-bucket/backups/$fileName
    fi
  fi
done
```

## Monitoring & Logging

### View Logs
```bash
# Cron logs
tail -f /var/log/medical-edu.log

# Systemd logs
journalctl -u medical-edu.service -f

# Check last execution
python3.11 main.py stats
```

### Set Up Alerts
- Use monitoring tools (UptimeRobot, Pingdom)
- Configure email notifications for failures
- Monitor disk space for videos directory

## Troubleshooting

### Common Issues

1. **FFmpeg not found**
   ```bash
   sudo apt install ffmpeg
   ```

2. **Permission denied**
   ```bash
   sudo chmod +x main.py
   sudo chown -R $USER:$USER /opt/medical-edu-app
   ```

3. **Database locked**
   - Ensure only one instance is running
   - Check for zombie processes: `ps aux | grep python`

4. **YouTube quota exceeded**
   - YouTube API has daily quota limits
   - Request quota increase in Google Cloud Console
   - Implement retry logic with exponential backoff

5. **Video generation timeout**
   - Increase timeout in cron/systemd
   - Optimize video generation settings
   - Use lightweight video generator

## Security Best Practices

1. **Protect credentials**
   - Never commit credentials to git
   - Use environment variables or secrets management
   - Rotate API keys regularly

2. **Secure server**
   - Enable firewall (ufw)
   - Keep system updated
   - Use SSH keys instead of passwords

3. **API endpoint security**
   - Use strong API secrets
   - Implement rate limiting
   - Use HTTPS only

4. **Database backups**
   - Automated daily backups
   - Store backups in separate location
   - Test restore procedures

## Cost Estimation

### Monthly Costs (Approximate)

| Service | Cost | Notes |
|---------|------|-------|
| VPS (2GB RAM) | $10-20 | DigitalOcean, Linode, Vultr |
| OpenAI API | $5-15 | ~30 requests/month |
| YouTube API | Free | Within quota limits |
| Telegram Bot | Free | Unlimited messages |
| Storage (50GB) | $2-5 | For videos and backups |
| **Total** | **$17-40/month** | Scales with usage |

### Free Tier Options
- GitHub Actions: 2,000 minutes/month free
- Oracle Cloud: Always free tier (ARM instances)
- Cloudflare Workers: 100,000 requests/day free

## Scaling Considerations

### Increase Frequency
- Modify cron schedule for multiple posts per day
- Implement queue system for parallel processing
- Use separate workers for video generation

### Multiple Channels
- Add multiple Telegram channels
- Create separate YouTube channels per subject
- Implement channel rotation logic

### Performance Optimization
- Pre-generate content in batches
- Use faster video generation libraries
- Implement caching for AI responses
- Optimize database queries

## Support & Maintenance

### Regular Maintenance Tasks
- Weekly: Check logs for errors
- Monthly: Review API usage and costs
- Quarterly: Update dependencies
- Yearly: Rotate API credentials

### Updates
```bash
cd /opt/medical-edu-app
git pull  # If using git
pip3 install --upgrade openai gtts Pillow
sudo apt update && sudo apt upgrade
```

## Conclusion

The recommended deployment approach is **Option 1 (VPS/Cloud Server)** for full control and reliability. This provides:
- Complete control over execution environment
- No time limits or restrictions
- Persistent storage
- Easy debugging and monitoring
- Cost-effective for daily automated tasks

For questions or issues, refer to the main documentation or create an issue in the repository.
