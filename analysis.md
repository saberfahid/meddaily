# Medical Education App - Requirements Analysis

## Project Overview
Build a fully automated medical education app that generates and publishes daily medical learning content across multiple platforms (YouTube, Telegram) with no manual intervention after setup.

## Key Requirements

### 1. Data Input & Storage
- **Source**: Word (.docx) files containing medical topics
- **Subjects**: 4 main categories
  - Internal Medicine (~191 topics)
  - Surgery (~185+ topics)
  - Pediatrics (~275+ topics)
  - Gynecology (~282+ topics)
- **Total**: ~933+ medical topics across all subjects
- **Format**: Topics organized as: Day | Topic | Subtopic | Status

### 2. Database Schema (SQLite)
```sql
subjects(id, name)
topics(id, subject_id, topic_name, cycle_number, used)
cases(id, topic_id, case_text, mcqs, answers, mnemonic, video_url, created_at)
```

### 3. Daily Workflow Logic
1. **Subject Rotation**: Rotate through subjects daily (one subject per day)
2. **Topic Selection**: Select next unused topic from current subject
3. **AI Generation**: Use Mistral AI to generate:
   - 1 short clinical case
   - 3 case-based MCQs
   - 2 independent MCQs (same objective, not case-linked)
   - Correct answers
   - 1 short mnemonic
4. **Database Update**: Save all content to SQLite, mark topic as used
5. **Video Creation**: Generate vertical video (1080×1920) under 60 seconds
6. **Publishing**: Upload to YouTube + Post to Telegram
7. **Cycle Management**: When all topics used, increment cycle_number and reuse with NEW content

### 4. AI Topic Generator
- Autonomous agent to create new topics/subtopics using Mistral AI
- Adds topics to SQLite when count is low
- Ensures continuous content pipeline

### 5. Video Generation Requirements
- **Format**: Vertical 1080×1920 (YouTube Shorts)
- **Duration**: Under 60 seconds
- **Slides**:
  1. Case (hook)
  2. MCQs
  3. Thinking pause
  4. Answers + mnemonic
- **Audio**: Text-to-speech narration
- **Output**: MP4 file

### 6. YouTube Upload
- Automatic upload with metadata
- **Title**: 🩺 {Topic Name}
- **Description**: Formatted with case, MCQs, answers, mnemonic, hashtags
- **Hashtags**: #Medical #USMLE #PLAB #Shorts

### 7. Telegram Posting
- Text-only post (no video upload)
- Short, clean format with YouTube link
- Mobile-friendly

### 8. Deployment
- **Platform**: Cloudflare Workers
- **Scheduling**: Cron Triggers (once per day)
- **Secrets**: Environment variables
- **Persistence**: Database must persist across runs

## Technical Stack
- **Language**: Python
- **Database**: SQLite
- **AI**: Mistral AI (via OpenAI-compatible API)
- **Video**: Python libraries (moviepy, PIL, gTTS/pyttsx3)
- **APIs**: YouTube Data API v3, Telegram Bot API
- **Deployment**: Cloudflare Workers with Python support

## Content Rules
- No duplicated content across cycles
- No manual intervention required
- Content must be concise and mobile-friendly
- Fully autonomous operation

## Topic Structure from File
The provided file contains topics in a structured format:
- Organized by medical specialty/system
- Each topic has: Day number, Topic category, Subtopic name, Status
- Topics are comprehensive and cover major medical education areas
- Suitable for USMLE, PLAB, and general medical education

## Next Steps
1. Design and implement database schema
2. Build topic ingestion parser for the provided format
3. Develop AI content generation module
4. Create video generation pipeline
5. Implement YouTube and Telegram integrations
6. Build orchestration script with daily workflow
7. Configure Cloudflare deployment with cron triggers
8. Test complete system end-to-end
