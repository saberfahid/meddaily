#!/bin/bash

# Medical Education App - Setup Script
# This script automates the installation and setup process

set -e  # Exit on error

echo "=========================================="
echo "Medical Education App - Setup"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
   echo "⚠️  Please do not run as root"
   exit 1
fi

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
else
    echo "❌ Unsupported operating system: $OSTYPE"
    exit 1
fi

echo "Detected OS: $OS"
echo ""

# Check Python version
echo "[1/6] Checking Python installation..."
if command -v python3.11 &> /dev/null; then
    PYTHON_CMD="python3.11"
    echo "✅ Python 3.11 found"
elif command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    if (( $(echo "$PYTHON_VERSION >= 3.11" | bc -l) )); then
        PYTHON_CMD="python3"
        echo "✅ Python $PYTHON_VERSION found"
    else
        echo "❌ Python 3.11+ required, found $PYTHON_VERSION"
        exit 1
    fi
else
    echo "❌ Python 3.11+ not found"
    echo "Please install Python 3.11 or higher"
    exit 1
fi

# Check FFmpeg
echo ""
echo "[2/6] Checking FFmpeg installation..."
if command -v ffmpeg &> /dev/null; then
    echo "✅ FFmpeg found"
else
    echo "❌ FFmpeg not found"
    echo ""
    if [ "$OS" == "linux" ]; then
        echo "Install with: sudo apt install ffmpeg"
    elif [ "$OS" == "macos" ]; then
        echo "Install with: brew install ffmpeg"
    fi
    exit 1
fi

# Install Python dependencies
echo ""
echo "[3/6] Installing Python dependencies..."
$PYTHON_CMD -m pip install --upgrade pip
$PYTHON_CMD -m pip install -r requirements.txt
echo "✅ Dependencies installed"

# Create directories
echo ""
echo "[4/6] Creating directories..."
mkdir -p videos
mkdir -p backups
mkdir -p logs
echo "✅ Directories created"

# Check for topics file
echo ""
echo "[5/6] Checking for topics file..."
if [ -f "medicaltopics.txt" ] || [ -f "medicaltopics.txt.txt" ]; then
    echo "✅ Topics file found"
    
    # Import topics if database doesn't exist
    if [ ! -f "medical_education.db" ]; then
        echo ""
        echo "Importing topics to database..."
        if [ -f "medicaltopics.txt" ]; then
            $PYTHON_CMD topic_ingestion.py medicaltopics.txt
        else
            $PYTHON_CMD topic_ingestion.py medicaltopics.txt.txt
        fi
        echo "✅ Topics imported"
    else
        echo "Database already exists, skipping import"
    fi
else
    echo "⚠️  Topics file not found"
    echo "Please add medicaltopics.txt to the directory"
fi

# Check environment variables
echo ""
echo "[6/6] Checking environment variables..."

MISSING_VARS=()

if [ -z "$OPENAI_API_KEY" ]; then
    MISSING_VARS+=("OPENAI_API_KEY")
fi

if [ -z "$YOUTUBE_CLIENT_ID" ]; then
    MISSING_VARS+=("YOUTUBE_CLIENT_ID")
fi

if [ -z "$YOUTUBE_CLIENT_SECRET" ]; then
    MISSING_VARS+=("YOUTUBE_CLIENT_SECRET")
fi

if [ -z "$YOUTUBE_REFRESH_TOKEN" ]; then
    MISSING_VARS+=("YOUTUBE_REFRESH_TOKEN")
fi

if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    MISSING_VARS+=("TELEGRAM_BOT_TOKEN")
fi

if [ -z "$TELEGRAM_CHANNEL_ID" ]; then
    MISSING_VARS+=("TELEGRAM_CHANNEL_ID")
fi

if [ ${#MISSING_VARS[@]} -eq 0 ]; then
    echo "✅ All environment variables set"
else
    echo "⚠️  Missing environment variables:"
    for var in "${MISSING_VARS[@]}"; do
        echo "   - $var"
    done
    echo ""
    echo "Create a .env file or export them:"
    echo ""
    echo "export OPENAI_API_KEY=\"your_key\""
    echo "export YOUTUBE_CLIENT_ID=\"your_client_id\""
    echo "export YOUTUBE_CLIENT_SECRET=\"your_client_secret\""
    echo "export YOUTUBE_REFRESH_TOKEN=\"your_refresh_token\""
    echo "export TELEGRAM_BOT_TOKEN=\"your_bot_token\""
    echo "export TELEGRAM_CHANNEL_ID=\"@your_channel\""
fi

# Summary
echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Set environment variables (if not done)"
echo "2. Test the workflow: $PYTHON_CMD main.py"
echo "3. View statistics: $PYTHON_CMD main.py stats"
echo "4. Set up cron job for daily execution"
echo ""
echo "For detailed instructions, see README.md"
echo ""
echo "=========================================="
