"""
Video Generation Module
Creates vertical educational videos (1080x1920) with text-to-speech narration
"""

import os
import textwrap
from typing import Dict, Any, List
from PIL import Image, ImageDraw, ImageFont
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip
from gtts import gTTS
import tempfile


class VideoGenerator:
    """Generates vertical educational videos for YouTube Shorts"""
    
    def __init__(self, output_dir: str = "videos"):
        self.width = 1080
        self.height = 1920
        self.output_dir = output_dir
        self.fps = 30
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Color scheme
        self.bg_color = (15, 23, 42)  # Dark blue
        self.text_color = (255, 255, 255)  # White
        self.accent_color = (59, 130, 246)  # Blue accent
        self.highlight_color = (34, 197, 94)  # Green
    
    def create_video(self, content: Dict[str, Any], topic: str, subtopic: str, 
                     output_filename: str = None) -> str:
        """
        Create a complete educational video
        
        Returns: path to the generated video file
        """
        
        if not output_filename:
            # Create safe filename
            safe_topic = "".join(c for c in topic if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_subtopic = "".join(c for c in subtopic if c.isalnum() or c in (' ', '-', '_')).strip()
            output_filename = f"{safe_topic}_{safe_subtopic}.mp4"
        
        output_path = os.path.join(self.output_dir, output_filename)
        
        # Create slides
        print("Creating video slides...")
        slides = []
        
        # Slide 1: Title + Case
        slide1_clip, audio1_path = self._create_case_slide(topic, subtopic, content['case_text'])
        slides.append((slide1_clip, audio1_path))
        
        # Slide 2: MCQs
        slide2_clip, audio2_path = self._create_mcq_slide(content)
        slides.append((slide2_clip, audio2_path))
        
        # Slide 3: Thinking pause
        slide3_clip, audio3_path = self._create_thinking_slide()
        slides.append((slide3_clip, audio3_path))
        
        # Slide 4: Answers + Mnemonic
        slide4_clip, audio4_path = self._create_answer_slide(content)
        slides.append((slide4_clip, audio4_path))
        
        # Combine slides with audio
        print("Combining slides with audio...")
        final_clips = []
        
        for img_clip, audio_path in slides:
            if audio_path and os.path.exists(audio_path):
                audio_clip = AudioFileClip(audio_path)
                duration = audio_clip.duration
                video_clip = img_clip.with_duration(duration).with_audio(audio_clip)
            else:
                video_clip = img_clip.with_duration(3)  # Default 3 seconds if no audio
            
            final_clips.append(video_clip)
        
        # Concatenate all clips
        print("Rendering final video...")
        final_video = concatenate_videoclips(final_clips, method="compose")
        
        # Ensure video is under 60 seconds
        if final_video.duration > 59:
            final_video = final_video.subclipped(0, 59)
        
        # Write video file
        final_video.write_videofile(
            output_path,
            fps=self.fps,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True,
            logger=None
        )
        
        # Clean up temporary audio files
        for _, audio_path in slides:
            if audio_path and os.path.exists(audio_path):
                try:
                    os.remove(audio_path)
                except:
                    pass
        
        print(f"Video created: {output_path}")
        return output_path
    
    def _create_case_slide(self, topic: str, subtopic: str, case_text: str):
        """Create the case/hook slide"""
        
        # Create image
        img = Image.new('RGB', (self.width, self.height), color=self.bg_color)
        draw = ImageDraw.Draw(img)
        
        # Try to load fonts, fallback to default if not available
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
            subtitle_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 45)
            text_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 38)
        except:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
        
        y_position = 150
        
        # Draw emoji and title
        title_text = f"🩺 {topic}"
        self._draw_centered_text(draw, title_text, y_position, title_font, self.text_color)
        y_position += 100
        
        # Draw subtopic
        self._draw_centered_text(draw, subtopic, y_position, subtitle_font, self.accent_color)
        y_position += 200
        
        # Draw "Case:" label
        self._draw_centered_text(draw, "📌 Clinical Case", y_position, subtitle_font, self.highlight_color)
        y_position += 100
        
        # Draw case text (wrapped)
        wrapped_case = self._wrap_text(case_text, 30)
        for line in wrapped_case:
            self._draw_centered_text(draw, line, y_position, text_font, self.text_color)
            y_position += 60
        
        # Save image
        temp_img = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        img.save(temp_img.name)
        
        # Create audio
        narration = f"{topic}. {subtopic}. Case: {case_text}"
        audio_path = self._create_audio(narration)
        
        # Create clip
        clip = ImageClip(temp_img.name)
        
        return clip, audio_path
    
    def _create_mcq_slide(self, content: Dict[str, Any]):
        """Create the MCQ slide"""
        
        img = Image.new('RGB', (self.width, self.height), color=self.bg_color)
        draw = ImageDraw.Draw(img)
        
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 55)
            question_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
            option_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
        except:
            title_font = ImageFont.load_default()
            question_font = ImageFont.load_default()
            option_font = ImageFont.load_default()
        
        y_position = 100
        
        # Title
        self._draw_centered_text(draw, "❓ Questions", y_position, title_font, self.highlight_color)
        y_position += 120
        
        # Combine all MCQs
        all_mcqs = content['case_based_mcqs'] + content['independent_mcqs']
        
        # Show first 3 questions (to fit on screen)
        narration_parts = ["Here are the questions."]
        
        for i, mcq in enumerate(all_mcqs[:3], 1):
            # Question number and text
            question_text = f"{i}. {mcq['question']}"
            wrapped_q = self._wrap_text(question_text, 35)
            
            for line in wrapped_q:
                if y_position > 1800:  # Stop if too close to bottom
                    break
                self._draw_text(draw, line, 60, y_position, question_font, self.text_color)
                y_position += 50
            
            y_position += 20
            
            # Options (abbreviated to fit)
            for opt_key in ['A', 'B', 'C', 'D']:
                if y_position > 1850:
                    break
                opt_text = mcq['options'][opt_key]
                if len(opt_text) > 40:
                    opt_text = opt_text[:37] + "..."
                self._draw_text(draw, f"  {opt_key}) {opt_text}", 80, y_position, option_font, self.accent_color)
                y_position += 45
            
            y_position += 30
            
            narration_parts.append(f"Question {i}: {mcq['question']}")
        
        # Save image
        temp_img = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        img.save(temp_img.name)
        
        # Create audio
        narration = " ".join(narration_parts)
        audio_path = self._create_audio(narration)
        
        clip = ImageClip(temp_img.name)
        
        return clip, audio_path
    
    def _create_thinking_slide(self):
        """Create thinking pause slide"""
        
        img = Image.new('RGB', (self.width, self.height), color=self.bg_color)
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
        except:
            font = ImageFont.load_default()
        
        # Draw thinking emoji and text
        self._draw_centered_text(draw, "🤔", 700, font, self.text_color)
        self._draw_centered_text(draw, "Think about it...", 900, font, self.highlight_color)
        
        # Save image
        temp_img = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        img.save(temp_img.name)
        
        # Create audio
        audio_path = self._create_audio("Take a moment to think about your answers.")
        
        clip = ImageClip(temp_img.name)
        
        return clip, audio_path
    
    def _create_answer_slide(self, content: Dict[str, Any]):
        """Create answers and mnemonic slide"""
        
        img = Image.new('RGB', (self.width, self.height), color=self.bg_color)
        draw = ImageDraw.Draw(img)
        
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
            answer_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 70)
            mnemonic_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 38)
        except:
            title_font = ImageFont.load_default()
            answer_font = ImageFont.load_default()
            mnemonic_font = ImageFont.load_default()
        
        y_position = 200
        
        # Answers title
        self._draw_centered_text(draw, "✅ Answers", y_position, title_font, self.highlight_color)
        y_position += 150
        
        # Answers
        answers_str = " ".join([f"{k}-{v}" for k, v in sorted(content['answers'].items())])
        self._draw_centered_text(draw, answers_str, y_position, answer_font, self.text_color)
        y_position += 250
        
        # Mnemonic title
        self._draw_centered_text(draw, "🧠 Mnemonic", y_position, title_font, self.accent_color)
        y_position += 120
        
        # Mnemonic text
        wrapped_mnemonic = self._wrap_text(content['mnemonic'], 30)
        for line in wrapped_mnemonic:
            self._draw_centered_text(draw, line, y_position, mnemonic_font, self.text_color)
            y_position += 60
        
        # Save image
        temp_img = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        img.save(temp_img.name)
        
        # Create audio
        narration = f"The answers are: {answers_str}. Here's a mnemonic to remember: {content['mnemonic']}"
        audio_path = self._create_audio(narration)
        
        clip = ImageClip(temp_img.name)
        
        return clip, audio_path
    
    def _create_audio(self, text: str) -> str:
        """Create audio file from text using gTTS"""
        
        temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        
        try:
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(temp_audio.name)
            return temp_audio.name
        except Exception as e:
            print(f"Error creating audio: {e}")
            return None
    
    def _draw_centered_text(self, draw, text, y, font, color):
        """Draw centered text"""
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        x = (self.width - text_width) // 2
        draw.text((x, y), text, font=font, fill=color)
    
    def _draw_text(self, draw, text, x, y, font, color):
        """Draw text at specific position"""
        draw.text((x, y), text, font=font, fill=color)
    
    def _wrap_text(self, text: str, width: int) -> List[str]:
        """Wrap text to specified width"""
        return textwrap.wrap(text, width=width)


# Test function
def test_video_generator():
    """Test the video generator"""
    from ai_generator import MedicalContentGenerator
    
    # Generate content
    print("Generating content...")
    generator = MedicalContentGenerator()
    content = generator.generate_educational_content(
        topic="Heart Failure",
        subtopic="Acute Heart Failure"
    )
    
    # Create video
    print("\nCreating video...")
    video_gen = VideoGenerator()
    video_path = video_gen.create_video(content, "Heart Failure", "Acute Heart Failure")
    
    print(f"\n✅ Video created successfully: {video_path}")


if __name__ == "__main__":
    test_video_generator()
