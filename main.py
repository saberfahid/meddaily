"""
Main Orchestration Script
Coordinates the complete daily workflow for medical education content generation
"""

import os
import sys
import json

# Fix Windows console encoding for emoji/unicode characters
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not installed, try manual loading
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
from datetime import datetime
from typing import Dict, Any, Optional

from database import MedicalDatabase
from ai_generator import MedicalContentGenerator
from video_generator_premium import PremiumVideoGenerator
from youtube_uploader import YouTubeUploaderEnv
from telegram_poster import TelegramPoster


class MedicalEducationOrchestrator:
    """Main orchestrator for automated medical education content pipeline"""
    
    def __init__(self, db_path: str = "medical_education.db"):
        """Initialize orchestrator with all components"""
        
        print("=" * 60)
        print("Medical Education Content Generator")
        print("=" * 60)
        
        # Initialize database
        print("\n[1/6] Initializing database...")
        self.db = MedicalDatabase(db_path)
        
        # Initialize AI generator
        print("[2/6] Initializing AI content generator...")
        self.ai_generator = MedicalContentGenerator()
        
        # Initialize video generator
        print("[3/6] Initializing video generator...")
        self.video_generator = PremiumVideoGenerator()
        
        # Initialize YouTube uploader (will be initialized when needed)
        print("[4/6] YouTube uploader ready...")
        self.youtube_uploader = None
        
        # Initialize Telegram poster
        print("[5/6] Initializing Telegram poster...")
        try:
            self.telegram_poster = TelegramPoster()
            print("   ✅ Telegram configured")
        except Exception as e:
            print(f"   ⚠️  Telegram not configured: {e}")
            self.telegram_poster = None
        
        print("[6/6] Orchestrator initialized successfully!")
        print("=" * 60)
    
    def run_daily_workflow(self) -> Dict[str, Any]:
        """
        Execute the complete daily workflow:
        1. Select next subject (rotation)
        2. Get next unused topic
        3. Generate content with AI
        4. Create video
        5. Upload to YouTube
        6. Post to Telegram
        7. Update database
        
        Returns:
            Dict with workflow results
        """
        
        print("\n" + "=" * 60)
        print(f"Starting Daily Workflow - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        results = {
            'success': False,
            'timestamp': datetime.now().isoformat(),
            'subject': None,
            'topic': None,
            'subtopic': None,
            'video_path': None,
            'youtube_url': None,
            'telegram_message_id': None,
            'error': None
        }
        
        try:
            # Step 1: Get next subject for rotation
            print("\n[Step 1/7] Selecting subject...")
            subject_id = self.db.get_next_subject_for_rotation()
            
            if not subject_id:
                raise Exception("No subjects found in database")
            
            # Get subject name
            subjects = self.db.get_all_subjects()
            subject = next((s for s in subjects if s['id'] == subject_id), None)
            subject_name = subject['name'] if subject else f"Subject {subject_id}"
            
            print(f"   Selected: {subject_name}")
            results['subject'] = subject_name
            
            # Step 2: Get next unused topic
            print("\n[Step 2/7] Getting next topic...")
            topic_data = self.db.get_next_unused_topic(subject_id)
            
            if not topic_data:
                # All topics used, start new cycle
                print("   All topics used in current cycle, starting new cycle...")
                self.db.check_and_start_new_cycle(subject_id)
                topic_data = self.db.get_next_unused_topic(subject_id)
                
                if not topic_data:
                    raise Exception(f"No topics available for subject: {subject_name}")
            
            topic_name = topic_data['topic_name']
            subtopic_name = topic_data['subtopic_name']
            topic_id = topic_data['id']
            
            print(f"   Topic: {topic_name}")
            print(f"   Subtopic: {subtopic_name}")
            
            results['topic'] = topic_name
            results['subtopic'] = subtopic_name
            
            # Step 3: Generate content with AI
            print("\n[Step 3/7] Generating educational content with AI...")
            content = self.ai_generator.generate_educational_content(
                topic=topic_name,
                subtopic=subtopic_name
            )
            
            print("   ✅ Content generated successfully")
            print(f"   - Case: {content['case_text'][:50]}...")
            print(f"   - MCQs: {len(content['case_based_mcqs']) + len(content['independent_mcqs'])} questions")
            print(f"   - Mnemonic: {content['mnemonic'][:50]}...")
            
            # Step 4: Create video
            print("\n[Step 4/7] Creating educational video...")
            video_path = self.video_generator.create_video(
                content=content,
                topic=topic_name,
                subtopic=subtopic_name
            )
            
            print(f"   ✅ Video created: {video_path}")
            results['video_path'] = video_path
            
            # Step 5: Upload to YouTube
            print("\n[Step 5/7] Uploading to YouTube...")
            youtube_result = None
            
            try:
                if not self.youtube_uploader:
                    self.youtube_uploader = YouTubeUploaderEnv()
                
                # Format description
                description = self.ai_generator.format_for_youtube_description(
                    content, topic_name, subtopic_name
                )
                
                youtube_result = self.youtube_uploader.upload_short(
                    video_path=video_path,
                    topic=topic_name,
                    subtopic=subtopic_name,
                    description=description
                )
                
                if youtube_result:
                    print(f"   ✅ YouTube upload successful")
                    print(f"   Video ID: {youtube_result['video_id']}")
                    print(f"   URL: {youtube_result['video_url']}")
                    results['youtube_url'] = youtube_result['video_url']
                else:
                    print("   ⚠️  YouTube upload failed")
                    
            except Exception as e:
                print(f"   ⚠️  YouTube upload error: {e}")
            
            # Step 6: Post to Telegram
            print("\n[Step 6/7] Posting to Telegram...")
            telegram_message_id = None
            
            if self.telegram_poster:
                try:
                    # Combine all MCQs
                    all_mcqs = content['case_based_mcqs'] + content['independent_mcqs']
                    
                    # Ensure we use the correct YouTube URL if available
                    yt_url = youtube_result['video_url'] if youtube_result else None
                    
                    telegram_message_id = self.telegram_poster.post_educational_content(
                        topic=topic_name,
                        subtopic=subtopic_name,
                        case_text=content['case_text'],
                        mcqs=all_mcqs,
                        mnemonic=content['mnemonic'],
                        youtube_url=yt_url
                    )
                    
                    if telegram_message_id:
                        print(f"   ✅ Telegram post successful (Message ID: {telegram_message_id})")
                        results['telegram_message_id'] = telegram_message_id
                    else:
                        print("   ⚠️  Telegram post failed")
                        
                except Exception as e:
                    print(f"   ⚠️  Telegram post error: {e}")
            else:
                print("   ⚠️  Telegram not configured, skipping...")
            
            # Step 7: Update database
            print("\n[Step 7/7] Updating database...")
            
            # Format MCQs and answers for storage
            mcqs_json = json.dumps({
                'case_based': content['case_based_mcqs'],
                'independent': content['independent_mcqs']
            })
            answers_json = json.dumps(content['answers'])
            
            # Save case to database
            case_id = self.db.add_case(
                topic_id=topic_id,
                case_text=content['case_text'],
                mcqs=mcqs_json,
                answers=answers_json,
                mnemonic=content['mnemonic'],
                video_path=video_path,
                video_url=youtube_result['video_url'] if youtube_result else None,
                youtube_id=youtube_result['video_id'] if youtube_result else None,
                telegram_message_id=telegram_message_id
            )
            
            # Mark topic as used
            self.db.mark_topic_as_used(topic_id)
            
            # Update workflow state
            self.db.update_workflow_state(subject_id)
            
            print(f"   ✅ Database updated (Case ID: {case_id})")
            
            # Success!
            results['success'] = True
            
            # Delete video after successful upload to save space
            if youtube_result and os.path.exists(video_path):
                try:
                    os.remove(video_path)
                    print(f"\n   🗑️  Video deleted after upload (saving space)")
                except Exception as e:
                    print(f"\n   ⚠️  Could not delete video: {e}")
            
            print("\n" + "=" * 60)
            print("✅ Daily Workflow Completed Successfully!")
            print("=" * 60)
            print(f"Subject: {subject_name}")
            print(f"Topic: {topic_name} - {subtopic_name}")
            if youtube_result:
                print(f"YouTube: {youtube_result['video_url']}")
            else:
                print(f"Video: {video_path}")
            if telegram_message_id:
                print(f"Telegram: Message ID {telegram_message_id}")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n❌ Workflow failed: {e}")
            results['error'] = str(e)
            import traceback
            traceback.print_exc()
        
        return results
    
    def check_and_generate_topics(self, min_topics: int = 50):
        """
        Check if any subject has low topic count and generate new ones
        
        Args:
            min_topics: Minimum number of topics per subject
        """
        
        print("\n[AI Topic Generator] Checking topic counts...")
        
        subjects = self.db.get_all_subjects()
        
        for subject in subjects:
            count = self.db.get_topic_count_by_subject(subject['id'])
            print(f"   {subject['name']}: {count} topics")
            
            if count < min_topics:
                print(f"   ⚠️  Low topic count, generating new topics...")
                
                try:
                    # Generate new topics
                    new_topics = self.ai_generator.generate_new_topics(
                        subject=subject['name'],
                        count=min_topics - count
                    )
                    
                    # Add to database
                    for topic_data in new_topics:
                        self.db.add_topic(
                            subject_id=subject['id'],
                            topic_name=topic_data['topic'],
                            subtopic_name=topic_data['subtopic'],
                            cycle_number=1
                        )
                    
                    # Log generation
                    self.db.log_ai_topic_generation(subject['id'], new_topics)
                    
                    print(f"   ✅ Generated {len(new_topics)} new topics")
                    
                except Exception as e:
                    print(f"   ❌ Topic generation failed: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get system statistics"""
        return self.db.get_statistics()


def main():
    """Main entry point"""
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "stats":
            # Show statistics
            orchestrator = MedicalEducationOrchestrator()
            stats = orchestrator.get_statistics()
            
            print("\n" + "=" * 60)
            print("System Statistics")
            print("=" * 60)
            print(f"Total Subjects: {stats['total_subjects']}")
            print(f"Total Topics: {stats['total_topics']}")
            print(f"Total Cases Generated: {stats['total_cases']}")
            print("\nTopics by Subject:")
            for subject, count in stats['topics_by_subject'].items():
                print(f"  {subject}: {count}")
            
            if stats['workflow']:
                print(f"\nLast Run: {stats['workflow']['last_run_date']}")
                print(f"Total Runs: {stats['workflow']['total_runs']}")
            
            print("=" * 60)
            return
        
        elif command == "generate-topics":
            # Generate new topics
            orchestrator = MedicalEducationOrchestrator()
            orchestrator.check_and_generate_topics()
            return
    
    # Run daily workflow
    orchestrator = MedicalEducationOrchestrator()
    results = orchestrator.run_daily_workflow()
    
    # Exit with appropriate code
    sys.exit(0 if results['success'] else 1)


if __name__ == "__main__":
    main()
