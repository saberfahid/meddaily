"""
Run the medical education app with Telegram integration
"""
import os
import sys

def main():
    # Check if credentials are provided as arguments
    if len(sys.argv) >= 3:
        telegram_token = sys.argv[1]
        telegram_channel = sys.argv[2]
        
        # Set environment variables
        os.environ['TELEGRAM_BOT_TOKEN'] = telegram_token
        os.environ['TELEGRAM_CHANNEL_ID'] = telegram_channel
        print(f"✅ Using Telegram credentials from command line")
    else:
        # Check if environment variables are set
        telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        telegram_channel = os.getenv('TELEGRAM_CHANNEL_ID')
        
        if not telegram_token or not telegram_channel:
            print("❌ Telegram credentials not found!")
            print("\nUsage:")
            print("  python run_with_telegram.py <BOT_TOKEN> <CHANNEL_ID>")
            print("  Or set TELEGRAM_BOT_TOKEN and TELEGRAM_CHANNEL_ID environment variables")
            print("\nExample:")
            print("  python run_with_telegram.py \"123456789:ABCdefGHIjklMNOpqrsTUVwxyz\" \"@medicaledudaily\"")
            return
    
    # Import and run main app
    try:
        from main import main as app_main
        app_main()
    except Exception as e:
        print(f"❌ Error running app: {e}")

if __name__ == "__main__":
    main()