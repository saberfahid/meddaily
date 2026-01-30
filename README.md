# Medical Education Content Generator 🩺

Fully automated system for generating and publishing daily medical educational content across multiple platforms.

## Features

✅ **Automated Content Generation**
- AI-powered clinical cases, MCQs, and mnemonics using Mistral AI
- Covers 1,076+ medical topics across 4 major subjects
- Intelligent topic rotation and cycle management

✅ **Video Creation**
- Vertical videos (1080×1920) optimized for YouTube Shorts
- Text-to-speech narration
- Professional medical education styling
- Under 60 seconds duration

✅ **Multi-Platform Publishing**
- Automatic YouTube upload with metadata
- Telegram channel posting
- Synchronized content delivery

✅ **Database Management**
- SQLite database for topic and content tracking
- Cycle-based topic reuse with fresh content
- Complete workflow state management

✅ **Zero Manual Intervention**
- Fully autonomous after initial setup
- Daily scheduled execution
- Error handling and logging

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Daily Workflow                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Subject Rotation  →  Select next subject in cycle       │
│  2. Topic Selection   →  Get unused topic from database     │
│  3. AI Generation     →  Create case, MCQs, mnemonic        │
│  4. Video Creation    →  Generate vertical video (MP4)      │
│  5. YouTube Upload    →  Publish as YouTube Short           │
│  6. Telegram Post     →  Share to Telegram channel          │
│  7. Database Update   →  Mark topic as used, save results   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Project Structure

```
medical_edu_app/
├── database.py                 # Database management and operations
├── topic_ingestion.py          # Parse and import topics from files
├── ai_generator.py             # AI content generation with Mistral
├── video_generator_lite.py     # Lightweight video creation
├── youtube_uploader.py         # YouTube API integration
├── telegram_poster.py          # Telegram Bot API integration
├── main.py                     # Main orchestration script
├── requirements.txt            # Python dependencies
├── cloudflare_deployment.md    # Deployment guide
├── README.md                   # This file
└── medical_education.db        # SQLite database (created on first run)
```

## Quick Start

### Prerequisites

- Python 3.11+
- FFmpeg installed
- API credentials for:
  - OpenAI/Mistral AI
  - YouTube Data API v3
  - Telegram Bot API

### Installation

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd medical_edu_app
   ```

2. **Install system dependencies**
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install python3.11 python3-pip ffmpeg -y
   
   # macOS
   brew install python@3.11 ffmpeg
   ```

3. **Install Python dependencies**
   ```bash
   pip3 install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   export OPENAI_API_KEY="your_openai_api_key"
   export YOUTUBE_CLIENT_ID="your_youtube_client_id"
   export YOUTUBE_CLIENT_SECRET="your_youtube_client_secret"
   export YOUTUBE_REFRESH_TOKEN="your_youtube_refresh_token"
   export TELEGRAM_BOT_TOKEN="your_telegram_bot_token"
   export TELEGRAM_CHANNEL_ID="@your_channel"
   ```

5. **Initialize database with topics**
   ```bash
   python3 topic_ingestion.py medicaltopics.txt
   ```

6. **Run the workflow**
   ```bash
   python3 main.py
   ```

## Configuration

### API Setup Guides

#### 1. OpenAI/Mistral AI API

1. Sign up at [OpenAI Platform](https://platform.openai.com/)
2. Create an API key
3. Set environment variable: `OPENAI_API_KEY`

#### 2. YouTube Data API v3

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable "YouTube Data API v3"
4. Create OAuth 2.0 credentials (Desktop app)
5. Download credentials JSON
6. Run `python3 youtube_uploader.py` for first-time authentication
7. Extract and set environment variables:
   - `YOUTUBE_CLIENT_ID`
   - `YOUTUBE_CLIENT_SECRET`
   - `YOUTUBE_REFRESH_TOKEN`

#### 3. Telegram Bot API

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot` and follow instructions
3. Copy the bot token
4. Create a channel and add your bot as administrator
5. Get channel ID:
   - Public: `@channelname`
   - Private: Use [@userinfobot](https://t.me/userinfobot)
6. Set environment variables:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHANNEL_ID`

## Usage

### Run Daily Workflow

```bash
python3 main.py
```

This executes the complete workflow:
1. Selects next subject (rotation)
2. Gets next unused topic
3. Generates content with AI
4. Creates video
5. Uploads to YouTube
6. Posts to Telegram
7. Updates database

### View Statistics

```bash
python3 main.py stats
```

Output:
```
System Statistics
==================
Total Subjects: 4
Total Topics: 1076
Total Cases Generated: 15

Topics by Subject:
  Internal Medicine: 192
  Surgery: 225
  Pediatrics: 511
  Gynecology: 148

Last Run: 2024-01-30
Total Runs: 15
```

### Generate New Topics (AI)

```bash
python3 main.py generate-topics
```

Automatically generates new topics when count is low.

## Scheduling

### Linux (Cron)

```bash
# Edit crontab
crontab -e

# Add daily execution at 9 AM
0 9 * * * cd /path/to/medical_edu_app && /usr/bin/python3 main.py >> /var/log/medical-edu.log 2>&1
```

### Linux (Systemd Timer)

See `cloudflare_deployment.md` for detailed systemd setup.

### macOS (launchd)

Create `~/Library/LaunchAgents/com.medicaledu.daily.plist`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.medicaledu.daily</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3</string>
        <string>/path/to/medical_edu_app/main.py</string>
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
```

Load:
```bash
launchctl load ~/Library/LaunchAgents/com.medicaledu.daily.plist
```

### Windows (Task Scheduler)

1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily at 9:00 AM
4. Action: Start a program
   - Program: `python.exe`
   - Arguments: `C:\path\to\medical_edu_app\main.py`
   - Start in: `C:\path\to\medical_edu_app`

## Database Schema

### Tables

**subjects**
- `id`: Primary key
- `name`: Subject name (Internal Medicine, Surgery, etc.)

**topics**
- `id`: Primary key
- `subject_id`: Foreign key to subjects
- `topic_name`: Main topic
- `subtopic_name`: Specific subtopic
- `cycle_number`: Current cycle (for reuse)
- `used`: Boolean flag
- `last_used_at`: Timestamp

**cases**
- `id`: Primary key
- `topic_id`: Foreign key to topics
- `case_text`: Clinical case
- `mcqs`: JSON with questions
- `answers`: JSON with correct answers
- `mnemonic`: Memory aid
- `video_path`: Local video file path
- `video_url`: YouTube URL
- `youtube_id`: YouTube video ID
- `telegram_message_id`: Telegram message ID
- `created_at`: Timestamp

**workflow_state**
- `id`: Always 1 (singleton)
- `current_subject_id`: Last processed subject
- `last_run_date`: Last execution date
- `total_runs`: Total workflow executions

## Content Format

### YouTube Video Description

```
🩺 Heart Failure: Acute Heart Failure

📌 Case:
A 68-year-old man presents with sudden onset dyspnea...

❓ MCQs:
1) What is the most likely diagnosis?
2) Which initial therapy is most appropriate?
3) Which complication is most likely?
4) Which neurohormonal system is activated?
5) Which physical exam finding is classic?

✅ Answers:
1-B 2-A 3-D 4-A 5-A

🧠 Mnemonic:
NO LIP: Nitrates, Oxygen, Loop diuretics, Inotropes, Position

#Medical #USMLE #PLAB #Shorts #MedicalEducation
```

### Telegram Post

```
🩺 Heart Failure: Acute Heart Failure

📌 Case:
A 68-year-old man presents with sudden onset dyspnea...

❓ MCQs:
1) What is the most likely diagnosis?
2) Which initial therapy is most appropriate?
3) Which complication is most likely?

🧠 Mnemonic:
NO LIP: Nitrates, Oxygen, Loop diuretics, Inotropes, Position

▶ Watch: https://youtube.com/shorts/abc123
```

## Troubleshooting

### Common Issues

**1. ModuleNotFoundError**
```bash
pip3 install -r requirements.txt
```

**2. FFmpeg not found**
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg
```

**3. YouTube quota exceeded**
- YouTube API has daily quota limits (10,000 units/day)
- Each upload costs ~1,600 units
- Request quota increase in Google Cloud Console

**4. Database locked**
- Ensure only one instance is running
- Kill zombie processes: `pkill -f main.py`

**5. Video generation timeout**
- Increase system timeout limits
- Use lightweight video generator
- Reduce video quality if needed

### Debug Mode

Add debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Performance

### Typical Execution Time
- Content generation (AI): 10-20 seconds
- Video creation: 30-60 seconds
- YouTube upload: 20-40 seconds
- Telegram post: 1-2 seconds
- **Total: ~2-3 minutes per workflow**

### Resource Usage
- RAM: ~500MB during video generation
- Disk: ~10MB per video
- CPU: Moderate during video encoding
- Network: ~15MB upload per video

## Deployment

See [cloudflare_deployment.md](cloudflare_deployment.md) for detailed deployment options:
- VPS/Cloud Server (Recommended)
- Cloudflare Workers + External Server
- GitHub Actions
- Docker containers

## Maintenance

### Regular Tasks

**Weekly**
- Check logs for errors
- Verify content quality
- Monitor API usage

**Monthly**
- Review database statistics
- Clean up old videos (optional)
- Update dependencies

**Quarterly**
- Rotate API credentials
- Review and optimize content
- Update topic database

### Backups

```bash
# Backup database
cp medical_education.db backups/medical_education_$(date +%Y%m%d).db

# Backup videos (optional)
tar -czf videos_backup_$(date +%Y%m%d).tar.gz videos/
```

## Cost Estimation

### Monthly Costs (Approximate)

| Service | Cost | Notes |
|---------|------|-------|
| VPS (2GB RAM) | $10-20 | DigitalOcean, Linode |
| OpenAI API | $5-15 | ~30 requests/month |
| YouTube API | Free | Within quota |
| Telegram Bot | Free | Unlimited |
| Storage | $2-5 | Videos and backups |
| **Total** | **$17-40/month** | |

## Security

### Best Practices

1. **Never commit credentials**
   - Use environment variables
   - Add `.env` to `.gitignore`

2. **Secure server**
   - Enable firewall
   - Use SSH keys
   - Keep system updated

3. **API security**
   - Rotate keys regularly
   - Use least privilege access
   - Monitor API usage

4. **Database backups**
   - Automated daily backups
   - Store in separate location
   - Test restore procedures

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is provided as-is for educational purposes.

## Support

For issues, questions, or feature requests:
- Create an issue in the repository
- Check existing documentation
- Review troubleshooting section

## Acknowledgments

- Medical content powered by Mistral AI
- Video generation using FFmpeg and MoviePy
- Text-to-speech by Google TTS
- APIs: YouTube Data API v3, Telegram Bot API

---

**Made with ❤️ for medical education**

🩺 Helping medical students learn, one topic at a time.
