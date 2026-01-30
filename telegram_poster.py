"""
Telegram Posting Automation Module
Handles automatic posting of educational content to Telegram
"""

import os
import requests
from typing import Optional, Dict, Any


class TelegramPoster:
    """Handles posting messages to Telegram channels/groups"""
    
    def __init__(self, bot_token: str = None, channel_id: str = None):
        """
        Initialize Telegram poster
        
        Args:
            bot_token: Telegram Bot API token (or from TELEGRAM_BOT_TOKEN env var)
            channel_id: Telegram channel/group ID (or from TELEGRAM_CHANNEL_ID env var)
        """
        self.bot_token = bot_token or os.getenv('TELEGRAM_BOT_TOKEN')
        self.channel_id = channel_id or os.getenv('TELEGRAM_CHANNEL_ID')
        
        if not self.bot_token:
            raise ValueError("Telegram bot token not provided")
        if not self.channel_id:
            raise ValueError("Telegram channel ID not provided")
        
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"
    
    def send_message(self, text: str, parse_mode: str = "HTML",
                     disable_web_page_preview: bool = False) -> Optional[Dict[str, Any]]:
        """
        Send a text message to Telegram channel
        
        Args:
            text: Message text (max 4096 characters)
            parse_mode: Message formatting (HTML, Markdown, or None)
            disable_web_page_preview: Disable link previews
        
        Returns:
            Response dict if successful, None otherwise
        """
        
        url = f"{self.api_url}/sendMessage"
        
        payload = {
            'chat_id': self.channel_id,
            'text': text[:4096],  # Telegram limit
            'parse_mode': parse_mode,
            'disable_web_page_preview': disable_web_page_preview
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('ok'):
                message_id = result['result']['message_id']
                print(f"✅ Message sent to Telegram (ID: {message_id})")
                return result['result']
            else:
                print(f"❌ Telegram API error: {result.get('description')}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error sending message to Telegram: {e}")
            return None
    
    def post_educational_content(self, topic: str, subtopic: str, case_text: str,
                                 mcqs: list, mnemonic: str, 
                                 youtube_url: str = None) -> Optional[str]:
        """
        Post formatted educational content to Telegram
        
        Args:
            topic: Medical topic
            subtopic: Medical subtopic
            case_text: Clinical case text
            mcqs: List of MCQ dicts with 'question' key
            mnemonic: Mnemonic text
            youtube_url: YouTube video URL
        
        Returns:
            Message ID if successful, None otherwise
        """
        
        # Format message
        message = self._format_educational_message(
            topic, subtopic, case_text, mcqs, mnemonic, youtube_url
        )
        
        # Send message
        result = self.send_message(message, parse_mode="HTML", disable_web_page_preview=False)
        
        if result:
            return str(result['message_id'])
        return None
    
    def _format_educational_message(self, topic: str, subtopic: str, case_text: str,
                                    mcqs: list, mnemonic: str, 
                                    youtube_url: str = None) -> str:
        """Format educational content for Telegram"""
        
        # Use HTML formatting for better appearance
        message = f"🩺 <b>{topic}: {subtopic}</b>\n\n"
        
        message += f"📌 <b>Case:</b>\n{case_text}\n\n"
        
        message += "❓ <b>MCQs:</b>\n"
        for i, mcq in enumerate(mcqs[:5], 1):  # Limit to 5 questions
            question = mcq['question']
            if len(question) > 100:
                question = question[:97] + "..."
            message += f"{i}) {question}\n"
        
        message += f"\n🧠 <b>Mnemonic:</b>\n{mnemonic}\n"
        
        if youtube_url:
            message += f"\n▶ <a href='{youtube_url}'>Watch Video</a>"
        
        return message
    
    def test_connection(self) -> bool:
        """Test bot connection and channel access"""
        
        url = f"{self.api_url}/getMe"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('ok'):
                bot_info = result['result']
                print(f"✅ Bot connected: @{bot_info['username']}")
                
                # Test channel access
                test_message = "🤖 Bot connection test"
                test_result = self.send_message(test_message)
                
                if test_result:
                    print(f"✅ Channel access confirmed: {self.channel_id}")
                    return True
                else:
                    print(f"❌ Cannot send messages to channel: {self.channel_id}")
                    return False
            else:
                print(f"❌ Bot authentication failed")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection error: {e}")
            return False


def setup_instructions():
    """Print setup instructions for Telegram Bot"""
    
    print("""
    ========================================
    Telegram Bot Setup Instructions
    ========================================
    
    1. Create a Telegram Bot:
       - Open Telegram and search for @BotFather
       - Send /newbot command
       - Follow instructions to create your bot
       - Copy the bot token (looks like: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz)
    
    2. Create a Telegram Channel:
       - Create a new channel in Telegram
       - Make it public or private
       - Add your bot as an administrator with post permissions
    
    3. Get Channel ID:
       - For public channels: Use @channelname (e.g., @medicaledudaily)
       - For private channels/groups:
         a) Add @userinfobot to your channel
         b) Forward a message from the channel to @userinfobot
         c) It will show the channel ID (e.g., -1001234567890)
    
    4. Set Environment Variables:
       - TELEGRAM_BOT_TOKEN: Your bot token from BotFather
       - TELEGRAM_CHANNEL_ID: Your channel ID or @username
    
    5. Test the bot:
       - Run this script to test connection
       - Bot should send a test message to your channel
    
    ========================================
    Example Usage:
    ========================================
    
    export TELEGRAM_BOT_TOKEN="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
    export TELEGRAM_CHANNEL_ID="@medicaledudaily"
    
    python telegram_poster.py
    
    ========================================
    """)


def test_telegram():
    """Test Telegram posting"""
    
    # Check if credentials are available
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    channel_id = os.getenv('TELEGRAM_CHANNEL_ID')
    
    if not bot_token or not channel_id:
        print("⚠️  Telegram credentials not found in environment variables")
        setup_instructions()
        return
    
    # Create poster
    poster = TelegramPoster(bot_token, channel_id)
    
    # Test connection
    print("Testing Telegram connection...")
    if poster.test_connection():
        print("\n✅ Telegram setup successful!")
        
        # Test educational content post
        print("\nTesting educational content post...")
        
        sample_mcqs = [
            {'question': 'What is the most common cause of acute heart failure?'},
            {'question': 'Which medication is first-line for acute decompensation?'},
            {'question': 'What is the most sensitive sign on physical exam?'}
        ]
        
        message_id = poster.post_educational_content(
            topic="Heart Failure",
            subtopic="Acute Heart Failure",
            case_text="A 68-year-old man presents with sudden onset dyspnea and orthopnea.",
            mcqs=sample_mcqs,
            mnemonic="NO LIP: Nitrates, Oxygen, Loop diuretics, Inotropes, Position",
            youtube_url="https://youtube.com/shorts/example123"
        )
        
        if message_id:
            print(f"✅ Test post successful! Message ID: {message_id}")
        else:
            print("❌ Test post failed")
    else:
        print("\n❌ Telegram setup failed")
        print("Please check your credentials and try again")


if __name__ == "__main__":
    test_telegram()
