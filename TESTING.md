# Testing Guide

This document provides comprehensive testing procedures for the Medical Education App.

## Pre-Deployment Testing

### 1. Database Testing

#### Test Database Initialization
```bash
python3 -c "from database import MedicalDatabase; db = MedicalDatabase('test.db'); print('✅ Database initialized')"
```

#### Test Topic Import
```bash
python3 topic_ingestion.py medicaltopics.txt.txt
python3 -c "from database import MedicalDatabase; db = MedicalDatabase(); stats = db.get_statistics(); print(f'Topics imported: {stats[\"total_topics\"]}')"
```

#### Test Subject Rotation
```bash
python3 -c "
from database import MedicalDatabase
db = MedicalDatabase()
for i in range(5):
    subject_id = db.get_next_subject_for_rotation()
    subjects = db.get_all_subjects()
    subject = next((s for s in subjects if s['id'] == subject_id), None)
    print(f'Rotation {i+1}: {subject[\"name\"]}')
    db.update_workflow_state(subject_id)
"
```

### 2. AI Content Generation Testing

#### Test Basic Content Generation
```bash
python3 -c "
from ai_generator import MedicalContentGenerator
gen = MedicalContentGenerator()
content = gen.generate_educational_content('Heart Failure', 'Acute Heart Failure')
print('✅ Content generated')
print(f'Case: {content[\"case_text\"][:50]}...')
print(f'MCQs: {len(content[\"case_based_mcqs\"])} + {len(content[\"independent_mcqs\"])}')
print(f'Mnemonic: {content[\"mnemonic\"][:50]}...')
"
```

#### Test Content Formatting
```bash
python3 -c "
from ai_generator import MedicalContentGenerator
gen = MedicalContentGenerator()
content = gen.generate_educational_content('Diabetes', 'Type 1 Diabetes')
yt_desc = gen.format_for_youtube_description(content, 'Diabetes', 'Type 1 Diabetes')
tg_msg = gen.format_for_telegram(content, 'Diabetes', 'Type 1 Diabetes', 'https://youtube.com/shorts/test')
print('✅ Formatting successful')
print(f'YouTube description length: {len(yt_desc)}')
print(f'Telegram message length: {len(tg_msg)}')
"
```

### 3. Video Generation Testing

#### Test Video Creation (Lightweight)
```bash
python3 -c "
from ai_generator import MedicalContentGenerator
from video_generator_lite import LightweightVideoGenerator
import os

print('Generating content...')
gen = MedicalContentGenerator()
content = gen.generate_educational_content('Hypertension', 'Essential Hypertension')

print('Creating video...')
video_gen = LightweightVideoGenerator('test_videos')
video_path = video_gen.create_video(content, 'Hypertension', 'Essential Hypertension', 'test_video.mp4')

if os.path.exists(video_path):
    size = os.path.getsize(video_path) / (1024*1024)
    print(f'✅ Video created: {video_path} ({size:.2f} MB)')
else:
    print('❌ Video creation failed')
"
```

### 4. YouTube Upload Testing

**Note**: This requires valid YouTube API credentials.

#### Test YouTube Connection
```bash
python3 -c "
import os
os.environ['YOUTUBE_CLIENT_ID'] = 'your_client_id'
os.environ['YOUTUBE_CLIENT_SECRET'] = 'your_client_secret'
os.environ['YOUTUBE_REFRESH_TOKEN'] = 'your_refresh_token'

from youtube_uploader import YouTubeUploaderEnv
try:
    uploader = YouTubeUploaderEnv()
    print('✅ YouTube authentication successful')
except Exception as e:
    print(f'❌ YouTube authentication failed: {e}')
"
```

#### Test Video Upload (Dry Run)
```bash
# Create a test video first
python3 -c "
from ai_generator import MedicalContentGenerator
from video_generator_lite import LightweightVideoGenerator

gen = MedicalContentGenerator()
content = gen.generate_educational_content('Test Topic', 'Test Subtopic')
video_gen = LightweightVideoGenerator('test_videos')
video_path = video_gen.create_video(content, 'Test Topic', 'Test Subtopic', 'upload_test.mp4')
print(f'Test video ready: {video_path}')
"

# Note: Actual upload will count against YouTube quota
# Only run when ready to upload
```

### 5. Telegram Testing

#### Test Telegram Connection
```bash
python3 telegram_poster.py
```

This will:
- Verify bot token
- Check channel access
- Send a test message
- Post sample educational content

#### Test Message Formatting
```bash
python3 -c "
from telegram_poster import TelegramPoster
import os

# Set test credentials
os.environ['TELEGRAM_BOT_TOKEN'] = 'your_bot_token'
os.environ['TELEGRAM_CHANNEL_ID'] = '@your_channel'

poster = TelegramPoster()
sample_mcqs = [
    {'question': 'Test question 1?'},
    {'question': 'Test question 2?'},
    {'question': 'Test question 3?'}
]

message_id = poster.post_educational_content(
    topic='Test Topic',
    subtopic='Test Subtopic',
    case_text='This is a test case.',
    mcqs=sample_mcqs,
    mnemonic='TEST: This is a test mnemonic',
    youtube_url='https://youtube.com/shorts/test123'
)

if message_id:
    print(f'✅ Test message sent (ID: {message_id})')
else:
    print('❌ Message sending failed')
"
```

### 6. Integration Testing

#### Test Complete Workflow (Without Upload)
```bash
python3 -c "
from database import MedicalDatabase
from ai_generator import MedicalContentGenerator
from video_generator_lite import LightweightVideoGenerator

print('Testing complete workflow...')

# Initialize
db = MedicalDatabase()
ai_gen = MedicalContentGenerator()
video_gen = LightweightVideoGenerator('test_videos')

# Get subject and topic
subject_id = db.get_next_subject_for_rotation()
subjects = db.get_all_subjects()
subject = next((s for s in subjects if s['id'] == subject_id), None)
topic_data = db.get_next_unused_topic(subject_id)

print(f'Subject: {subject[\"name\"]}')
print(f'Topic: {topic_data[\"topic_name\"]} - {topic_data[\"subtopic_name\"]}')

# Generate content
content = ai_gen.generate_educational_content(
    topic_data['topic_name'],
    topic_data['subtopic_name']
)
print('✅ Content generated')

# Create video
video_path = video_gen.create_video(
    content,
    topic_data['topic_name'],
    topic_data['subtopic_name'],
    'integration_test.mp4'
)
print(f'✅ Video created: {video_path}')

print('✅ Integration test successful')
"
```

## Production Testing

### 1. Dry Run Test

Run the complete workflow without uploading:

```bash
# Comment out upload functions in main.py temporarily
# Or set environment variables to test mode
python3 main.py
```

### 2. Single Execution Test

Run one complete workflow:

```bash
python3 main.py
```

Monitor output for:
- ✅ All steps completed
- ✅ No errors or warnings
- ✅ Database updated
- ✅ Video created
- ✅ YouTube upload successful
- ✅ Telegram post successful

### 3. Statistics Verification

```bash
python3 main.py stats
```

Verify:
- Topic counts are correct
- Cases are being recorded
- Workflow state is updating

### 4. Multi-Day Simulation

Run workflow multiple times to test rotation:

```bash
for i in {1..5}; do
    echo "=== Day $i ==="
    python3 main.py
    sleep 2
done
```

Check that:
- Different subjects are selected each day
- Topics are not repeated
- Database state is consistent

## Performance Testing

### 1. Execution Time

```bash
time python3 main.py
```

Expected times:
- AI generation: 10-20 seconds
- Video creation: 30-60 seconds
- YouTube upload: 20-40 seconds
- Total: 2-3 minutes

### 2. Resource Usage

```bash
# Monitor during execution
top -p $(pgrep -f main.py)

# Or use htop
htop -p $(pgrep -f main.py)
```

Expected usage:
- RAM: ~500MB peak
- CPU: 50-100% during video encoding
- Disk I/O: Moderate during video write

### 3. Database Performance

```bash
python3 -c "
import time
from database import MedicalDatabase

db = MedicalDatabase()

# Test query performance
start = time.time()
for i in range(100):
    subject_id = db.get_next_subject_for_rotation()
    topic = db.get_next_unused_topic(subject_id)
end = time.time()

print(f'100 queries completed in {end-start:.2f} seconds')
print(f'Average: {(end-start)/100*1000:.2f} ms per query')
"
```

## Error Handling Testing

### 1. Test Missing API Keys

```bash
# Temporarily unset API keys
unset OPENAI_API_KEY
python3 main.py
# Should fail gracefully with error message
```

### 2. Test Network Failure

```bash
# Simulate network issues
# Use network simulation tools or disconnect temporarily
python3 main.py
# Should handle errors and log appropriately
```

### 3. Test Database Lock

```bash
# Start two instances simultaneously
python3 main.py &
python3 main.py &
# Should handle database locking gracefully
```

### 4. Test Disk Space

```bash
# Check available space
df -h

# Test with limited space (use a test partition)
# Should fail gracefully if disk is full
```

## Validation Checklist

Before production deployment:

- [ ] Database initialized with all topics
- [ ] All environment variables set correctly
- [ ] API credentials tested and working
- [ ] Video generation produces valid MP4 files
- [ ] YouTube uploads successfully
- [ ] Telegram posts successfully
- [ ] Subject rotation works correctly
- [ ] Topic cycle management works
- [ ] Database updates correctly
- [ ] Error handling works as expected
- [ ] Logging is comprehensive
- [ ] Performance is acceptable
- [ ] Resource usage is within limits
- [ ] Cron job configured correctly
- [ ] Backups configured
- [ ] Monitoring set up

## Continuous Monitoring

### Daily Checks

```bash
# Check if workflow ran today
python3 main.py stats

# Check logs for errors
tail -50 /var/log/medical-edu.log | grep -i error

# Verify latest video
ls -lht videos/ | head -5

# Check database size
du -h medical_education.db
```

### Weekly Checks

```bash
# Review statistics
python3 main.py stats

# Check disk usage
df -h

# Review API usage
# Check YouTube API quota in Google Cloud Console
# Check OpenAI API usage in OpenAI dashboard

# Verify backups
ls -lh backups/
```

### Monthly Checks

```bash
# Database integrity check
sqlite3 medical_education.db "PRAGMA integrity_check;"

# Clean up old videos (optional)
find videos/ -type f -mtime +30 -delete

# Review and rotate logs
logrotate /etc/logrotate.d/medical-edu
```

## Troubleshooting Tests

### Test 1: Database Recovery

```bash
# Backup current database
cp medical_education.db medical_education.db.backup

# Test recovery
rm medical_education.db
python3 topic_ingestion.py medicaltopics.txt.txt
python3 main.py stats
```

### Test 2: Video Generation Fallback

```bash
# Test with limited resources
# Reduce video quality or use alternative generator
python3 -c "
from video_generator_lite import LightweightVideoGenerator
# Test video generation with constraints
"
```

### Test 3: API Failure Recovery

```bash
# Test with invalid credentials
# Should log error and continue gracefully
```

## Load Testing

### Simulate Multiple Days

```bash
#!/bin/bash
# load_test.sh

for day in {1..30}; do
    echo "=== Simulating Day $day ==="
    python3 main.py
    if [ $? -ne 0 ]; then
        echo "❌ Failed on day $day"
        exit 1
    fi
    echo "✅ Day $day completed"
    sleep 5
done

echo "✅ 30-day simulation completed successfully"
```

## Automated Testing Script

```bash
#!/bin/bash
# run_tests.sh

echo "Running Medical Education App Tests"
echo "===================================="

# Test 1: Database
echo "Test 1: Database initialization"
python3 -c "from database import MedicalDatabase; MedicalDatabase('test.db')" && echo "✅ PASS" || echo "❌ FAIL"

# Test 2: AI Generation
echo "Test 2: AI content generation"
python3 -c "from ai_generator import MedicalContentGenerator; gen = MedicalContentGenerator(); gen.generate_educational_content('Test', 'Test')" && echo "✅ PASS" || echo "❌ FAIL"

# Test 3: Video Generation
echo "Test 3: Video generation"
python3 -c "from video_generator_lite import LightweightVideoGenerator; from ai_generator import MedicalContentGenerator; gen = MedicalContentGenerator(); content = gen.generate_educational_content('Test', 'Test'); video_gen = LightweightVideoGenerator('test_videos'); video_gen.create_video(content, 'Test', 'Test', 'test.mp4')" && echo "✅ PASS" || echo "❌ FAIL"

# Test 4: Statistics
echo "Test 4: Statistics retrieval"
python3 main.py stats && echo "✅ PASS" || echo "❌ FAIL"

echo "===================================="
echo "Tests completed"
```

Make executable:
```bash
chmod +x run_tests.sh
./run_tests.sh
```

## Success Criteria

The system is ready for production when:

1. ✅ All unit tests pass
2. ✅ Integration tests complete successfully
3. ✅ Performance meets requirements (< 5 minutes per workflow)
4. ✅ Error handling works correctly
5. ✅ All API integrations functional
6. ✅ Database operations are reliable
7. ✅ Video quality is acceptable
8. ✅ Content quality is high
9. ✅ Monitoring is in place
10. ✅ Backups are configured

---

**Remember**: Always test in a staging environment before deploying to production!
