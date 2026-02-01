"""
YouTube Upload Automation Module
Handles automatic video uploads to YouTube with metadata
"""

import os
import pickle
from typing import Optional, Dict, Any
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError


class YouTubeUploader:
    """Handles YouTube video uploads with authentication"""
    
    # YouTube API scopes
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
    
    def __init__(self, credentials_file: str = 'youtube_credentials.json', 
                 token_file: str = 'youtube_token.pickle'):
        """
        Initialize YouTube uploader
        
        Args:
            credentials_file: Path to OAuth2 credentials JSON file
            token_file: Path to store/load authentication token
        """
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.youtube = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with YouTube API"""
        
        creds = None
        
        # Load existing token if available
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
        
        # If no valid credentials, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            elif os.path.exists(self.credentials_file):
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.SCOPES)
                # Use local server flow but specify host as 0.0.0.0 for sandbox access
                # In this environment, we'll try to use the browser tool
                creds = flow.run_local_server(
                    host='localhost',
                    port=8080,
                    authorization_prompt_message='Please visit this URL to authorize this application: {url}',
                    success_message='The authentication flow has completed; you may close this window.',
                    open_browser=False
                )
            else:
                raise FileNotFoundError(
                    f"Credentials file not found: {self.credentials_file}\n"
                    "Please download OAuth2 credentials from Google Cloud Console"
                )
            
            # Save credentials for future use
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)
        
        # Build YouTube service
        self.youtube = build('youtube', 'v3', credentials=creds)
    
    def upload_video(self, video_path: str, title: str, description: str,
                     tags: list = None, category_id: str = "27",  # Education category
                     privacy_status: str = "public") -> Optional[str]:
        """
        Upload video to YouTube
        
        Args:
            video_path: Path to video file
            title: Video title (max 100 characters)
            description: Video description (max 5000 characters)
            tags: List of tags (max 500 characters total)
            category_id: YouTube category ID (27 = Education)
            privacy_status: public, private, or unlisted
        
        Returns:
            Video ID if successful, None otherwise
        """
        
        if not os.path.exists(video_path):
            print(f"Error: Video file not found: {video_path}")
            return None
        
        # Prepare video metadata
        body = {
            'snippet': {
                'title': title[:100],  # YouTube limit
                'description': description[:5000],  # YouTube limit
                'tags': tags or [],
                'categoryId': category_id
            },
            'status': {
                'privacyStatus': privacy_status,
                'selfDeclaredMadeForKids': False
            }
        }
        
        # Create media upload
        media = MediaFileUpload(
            video_path,
            chunksize=1024*1024,  # 1MB chunks
            resumable=True,
            mimetype='video/mp4'
        )
        
        try:
            print(f"Uploading video: {title}")
            
            # Execute upload request
            request = self.youtube.videos().insert(
                part='snippet,status',
                body=body,
                media_body=media
            )
            
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    print(f"Upload progress: {progress}%")
            
            video_id = response['id']
            video_url = f"https://youtube.com/shorts/{video_id}"
            
            print(f"✅ Upload successful!")
            print(f"Video ID: {video_id}")
            print(f"URL: {video_url}")
            
            return video_id
            
        except HttpError as e:
            print(f"HTTP Error during upload: {e}")
            return None
        except Exception as e:
            print(f"Error during upload: {e}")
            return None
    
    def upload_short(self, video_path: str, topic: str, subtopic: str,
                     description: str) -> Optional[Dict[str, str]]:
        """
        Upload a YouTube Short with medical education content
        
        Args:
            video_path: Path to video file
            topic: Medical topic
            subtopic: Medical subtopic
            description: Full description with case, MCQs, etc.
        
        Returns:
            Dict with video_id and video_url if successful
        """
        
        # Create title
        title = f"🩺 {topic}: {subtopic}"
        
        # Add hashtags to description
        full_description = description + "\n\n#Medical #USMLE #PLAB #Shorts #MedicalEducation #MedicalStudent"
        
        # Tags for better discoverability
        tags = [
            'medical education', 'USMLE', 'PLAB', 'medical student',
            'medicine', 'clinical case', 'MCQ', 'medical exam',
            topic.lower(), subtopic.lower()
        ]
        
        # Upload video
        video_id = self.upload_video(
            video_path=video_path,
            title=title,
            description=full_description,
            tags=tags,
            category_id="27",  # Education
            privacy_status="public"
        )
        
        if video_id:
            return {
                'video_id': video_id,
                'video_url': f"https://youtube.com/shorts/{video_id}"
            }
        
        return None
    
    def get_video_info(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Get information about an uploaded video"""
        
        try:
            request = self.youtube.videos().list(
                part='snippet,status,statistics',
                id=video_id
            )
            response = request.execute()
            
            if response['items']:
                return response['items'][0]
            return None
            
        except HttpError as e:
            print(f"Error getting video info: {e}")
            return None


# Environment variable based uploader for production
class YouTubeUploaderEnv:
    """
    YouTube uploader using environment variables or pickle token
    """
    
    def __init__(self, token_file: str = 'youtube_token.pickle'):
        self.token_file = token_file
        self.youtube = None
        self._authenticate()
    
    def _authenticate(self):
        creds = None
        
        # Try loading from pickle first
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
        
        # Fallback to environment variables
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                client_id = os.getenv('YOUTUBE_CLIENT_ID')
                client_secret = os.getenv('YOUTUBE_CLIENT_SECRET')
                refresh_token = os.getenv('YOUTUBE_REFRESH_TOKEN')
                
                if all([client_id, client_secret, refresh_token]) and client_id != "your_youtube_client_id":
                    creds = Credentials(
                        token=None,
                        refresh_token=refresh_token,
                        token_uri='https://oauth2.googleapis.com/token',
                        client_id=client_id,
                        client_secret=client_secret
                    )
                    creds.refresh(Request())
                else:
                    print("⚠️  YouTube credentials not configured. Skipping YouTube initialization.")
                    self.youtube = None
                    return
        
        self.youtube = build('youtube', 'v3', credentials=creds)
    
    def upload_short(self, video_path: str, topic: str, subtopic: str,
                     description: str) -> Optional[Dict[str, str]]:
        """Upload YouTube Short (same interface as YouTubeUploader)"""
        if not self.youtube:
            print("⚠️  YouTube not configured. Cannot upload video.")
            return None
        
        title = f"🩺 {topic}: {subtopic}"
        full_description = description + "\n\n#Medical #USMLE #PLAB #Shorts #MedicalEducation #MedicalStudent"
        
        tags = [
            'medical education', 'USMLE', 'PLAB', 'medical student',
            'medicine', 'clinical case', 'MCQ', 'medical exam',
            topic.lower(), subtopic.lower()
        ]
        
        body = {
            'snippet': {
                'title': title[:100],
                'description': full_description[:5000],
                'tags': tags,
                'categoryId': "27"
            },
            'status': {
                'privacyStatus': 'public',
                'selfDeclaredMadeForKids': False
            }
        }
        
        media = MediaFileUpload(video_path, chunksize=1024*1024, resumable=True, mimetype='video/mp4')
        
        try:
            request = self.youtube.videos().insert(
                part='snippet,status',
                body=body,
                media_body=media
            )
            
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    print(f"Upload progress: {int(status.progress() * 100)}%")
            
            video_id = response['id']
            return {
                'video_id': video_id,
                'video_url': f"https://youtube.com/shorts/{video_id}"
            }
            
        except Exception as e:
            print(f"Upload error: {e}")
            return None


def setup_instructions():
    """Print setup instructions for YouTube API"""
    
    print("""
    ========================================
    YouTube API Setup Instructions
    ========================================
    
    1. Go to Google Cloud Console: https://console.cloud.google.com/
    
    2. Create a new project or select existing one
    
    3. Enable YouTube Data API v3:
       - Go to "APIs & Services" > "Library"
       - Search for "YouTube Data API v3"
       - Click "Enable"
    
    4. Create OAuth 2.0 Credentials:
       - Go to "APIs & Services" > "Credentials"
       - Click "Create Credentials" > "OAuth client ID"
       - Application type: "Desktop app"
       - Download the JSON file
       - Save as "youtube_credentials.json"
    
    5. For production (Cloudflare):
       - After first authentication, extract:
         * client_id
         * client_secret
         * refresh_token (from youtube_token.pickle)
       - Set as environment variables:
         * YOUTUBE_CLIENT_ID
         * YOUTUBE_CLIENT_SECRET
         * YOUTUBE_REFRESH_TOKEN
    
    6. First-time authentication:
       - Run this script locally
       - Browser will open for authorization
       - Grant permissions
       - Token will be saved for future use
    
    ========================================
    """)


if __name__ == "__main__":
    setup_instructions()
