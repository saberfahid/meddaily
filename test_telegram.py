"""
Test Telegram credentials and connection
"""
import os
import sys
from telegram_poster import TelegramPoster

def test_telegram():
    # Get credentials from command line or environment
    if len(sys.argv) >= 3:
        bot_token = sys.argv[1]
        channel_id = sys.argv[2]
        os.environ['TELEGRAM_BOT_TOKEN'] = bot_token
        os.environ['TELEGRAM_CHANNEL_ID'] = channel_id
        print("✅ Using credentials from command line")
    else:
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        channel_id = os.getenv('TELEGRAM_CHANNEL_ID')
        
        if not bot_token or not channel_id:
            print("❌ Please provide Telegram credentials")
            print("Usage: python test_telegram.py <BOT_TOKEN> <CHANNEL_ID>")
            return False
    
    try:
        # Initialize poster
        poster = TelegramPoster()
        print("✅ Telegram poster initialized")
        
        # Test connection
        print("Testing connection...")
        success = poster.test_connection()
        
        if success:
            print("✅ Telegram integration ready!")
            return True
        else:
            print("❌ Telegram connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_telegram()