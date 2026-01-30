from youtube_uploader import YouTubeUploader
import os

def authenticate():
    print("Starting YouTube authentication flow...")
    try:
        uploader = YouTubeUploader(
            credentials_file='youtube_credentials.json',
            token_file='youtube_token.pickle'
        )
        print("✅ Authentication successful!")
        print(f"Token saved to: {os.path.abspath('youtube_token.pickle')}")
    except Exception as e:
        print(f"❌ Authentication failed: {e}")

if __name__ == "__main__":
    authenticate()
