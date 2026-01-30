"""
Lightweight Video Generation Module
Optimized for fast rendering in production environment
Uses ffmpeg directly for better performance
"""

import os
import subprocess
import textwrap
import asyncio
import edge_tts
from typing import Dict, Any, List
from PIL import Image, ImageDraw, ImageFont
import tempfile


class LightweightVideoGenerator:
    """Fast video generator using direct ffmpeg commands"""
    
    def __init__(self, output_dir: str = "videos"):
        self.width = 1080
        self.height = 1920
        self.output_dir = output_dir
        self.fps = 30
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Color scheme
        self.bg_color = (15, 23, 42)
        self.text_color = (255, 255, 255)
        self.accent_color = (59, 130, 246)
        self.highlight_color = (34, 197, 94)
        
        # High-quality neural male voice
        self.voice = "en-US-GuyNeural"
    
    def create_video(self, content: Dict[str, Any], topic: str, subtopic: str, 
                     output_filename: str = None) -> str:
        """Create educational video using ffmpeg"""
        
        if not output_filename:
            safe_topic = "".join(c for c in topic if c.isalnum() or c in (' ', '-', '_')).strip()[:30]
            safe_subtopic = "".join(c for c in subtopic if c.isalnum() or c in (' ', '-', '_')).strip()[:30]
            output_filename = f"{safe_topic}_{safe_subtopic}.mp4"
        
        output_path = os.path.join(self.output_dir, output_filename)
        
        print("Creating video slides...")
        
        # Create slides and audio
        slides_with_audio = []
        
        # Slide 1: Title + Case
        img1, audio1 = self._create_case_slide(topic, subtopic, content['case_text'])
        slides_with_audio.append((img1, audio1))
        
        # Slide 2: MCQs
        img2, audio2 = self._create_mcq_slide(content)
        slides_with_audio.append((img2, audio2))
        
        # Slide 3: Thinking pause
        img3, audio3 = self._create_thinking_slide()
        slides_with_audio.append((img3, audio3))
        
        # Slide 4: Answers + Mnemonic
        img4, audio4 = self._create_answer_slide(content)
        slides_with_audio.append((img4, audio4))
        
        # Combine using ffmpeg
        print("Rendering video with ffmpeg...")
        self._combine_slides_ffmpeg(slides_with_audio, output_path)
        
        # Cleanup temp files
        for img_path, audio_path in slides_with_audio:
            try:
                if os.path.exists(img_path):
                    os.remove(img_path)
                if audio_path and os.path.exists(audio_path):
                    os.remove(audio_path)
            except:
                pass
        
        print(f"Video created: {output_path}")
        return output_path
    
    def _combine_slides_ffmpeg(self, slides_with_audio: List[tuple], output_path: str):
        """Combine slides using ffmpeg for fast rendering"""
        
        # Create concat file for ffmpeg
        concat_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
        video_segments = []
        
        for i, (img_path, audio_path) in enumerate(slides_with_audio):
            segment_path = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name
            
            if audio_path and os.path.exists(audio_path):
                # Get audio duration
                probe_cmd = [
                    'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                    '-of', 'default=noprint_wrappers=1:nokey=1', audio_path
                ]
                try:
                    duration = float(subprocess.check_output(probe_cmd).decode().strip())
                except:
                    duration = 3.0
                
                # Create video segment with audio
                cmd = [
                    'ffmpeg', '-y', '-loop', '1', '-i', img_path,
                    '-i', audio_path,
                    '-c:v', 'libx264', '-tune', 'stillimage',
                    '-c:a', 'aac', '-b:a', '192k',
                    '-pix_fmt', 'yuv420p',
                    '-shortest', '-t', str(duration),
                    '-vf', f'fps={self.fps}',
                    segment_path
                ]
            else:
                # Create video segment without audio (3 seconds)
                cmd = [
                    'ffmpeg', '-y', '-loop', '1', '-i', img_path,
                    '-c:v', 'libx264', '-tune', 'stillimage',
                    '-pix_fmt', 'yuv420p',
                    '-t', '3',
                    '-vf', f'fps={self.fps}',
                    segment_path
                ]
            
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            video_segments.append(segment_path)
            concat_file.write(f"file '{segment_path}'\n")
        
        concat_file.close()
        
        # Concatenate all segments
        concat_cmd = [
            'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
            '-i', concat_file.name,
            '-c', 'copy',
            output_path
        ]
        subprocess.run(concat_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        
        # Cleanup
        os.remove(concat_file.name)
        for segment in video_segments:
            try:
                os.remove(segment)
            except:
                pass
    
    def _create_case_slide(self, topic: str, subtopic: str, case_text: str):
        """Create case slide"""
        
        img = Image.new('RGB', (self.width, self.height), color=self.bg_color)
        draw = ImageDraw.Draw(img)
        
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
            subtitle_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 45)
            text_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 38)
        except:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
        
        y = 150
        
        # Title
        self._draw_centered_text(draw, f"🩺 {topic}", y, title_font, self.text_color)
        y += 100
        
        # Subtopic
        self._draw_centered_text(draw, subtopic, y, subtitle_font, self.accent_color)
        y += 200
        
        # Case label
        self._draw_centered_text(draw, "📌 Clinical Case", y, subtitle_font, self.highlight_color)
        y += 100
        
        # Case text
        for line in self._wrap_text(case_text, 30):
            self._draw_centered_text(draw, line, y, text_font, self.text_color)
            y += 60
        
        # Save image
        temp_img = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        img.save(temp_img.name)
        
        # Create audio
        narration = f"{topic}. {subtopic}. Case: {case_text}"
        audio_path = self._create_audio(narration)
        
        return temp_img.name, audio_path
    
    def _create_mcq_slide(self, content: Dict[str, Any]):
        """Create MCQ slide"""
        
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
        
        y = 100
        
        self._draw_centered_text(draw, "❓ Questions", y, title_font, self.highlight_color)
        y += 120
        
        all_mcqs = content['case_based_mcqs'] + content['independent_mcqs']
        narration_parts = ["Here are the questions."]
        
        for i, mcq in enumerate(all_mcqs[:3], 1):
            question_text = f"{i}. {mcq['question']}"
            for line in self._wrap_text(question_text, 35):
                if y > 1800:
                    break
                self._draw_text(draw, line, 60, y, question_font, self.text_color)
                y += 50
            
            y += 20
            
            for opt_key in ['A', 'B', 'C', 'D']:
                if y > 1850:
                    break
                opt_text = mcq['options'][opt_key]
                if len(opt_text) > 40:
                    opt_text = opt_text[:37] + "..."
                self._draw_text(draw, f"  {opt_key}) {opt_text}", 80, y, option_font, self.accent_color)
                y += 45
            
            y += 30
            narration_parts.append(f"Question {i}: {mcq['question']}")
        
        temp_img = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        img.save(temp_img.name)
        
        narration = " ".join(narration_parts)
        audio_path = self._create_audio(narration)
        
        return temp_img.name, audio_path
    
    def _create_thinking_slide(self):
        """Create thinking pause slide"""
        
        img = Image.new('RGB', (self.width, self.height), color=self.bg_color)
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
        except:
            font = ImageFont.load_default()
        
        self._draw_centered_text(draw, "🤔", 700, font, self.text_color)
        self._draw_centered_text(draw, "Think about it...", 900, font, self.highlight_color)
        
        temp_img = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        img.save(temp_img.name)
        
        audio_path = self._create_audio("Take a moment to think about your answers.")
        
        return temp_img.name, audio_path
    
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
        
        y = 200
        
        self._draw_centered_text(draw, "✅ Answers", y, title_font, self.highlight_color)
        y += 150
        
        answers_str = " ".join([f"{k}-{v}" for k, v in sorted(content['answers'].items())])
        self._draw_centered_text(draw, answers_str, y, answer_font, self.text_color)
        y += 250
        
        self._draw_centered_text(draw, "🧠 Mnemonic", y, title_font, self.accent_color)
        y += 120
        
        for line in self._wrap_text(content['mnemonic'], 30):
            self._draw_centered_text(draw, line, y, mnemonic_font, self.text_color)
            y += 60
        
        temp_img = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        img.save(temp_img.name)
        
        narration = f"The answers are: {answers_str}. Here's a mnemonic to remember: {content['mnemonic']}"
        audio_path = self._create_audio(narration)
        
        return temp_img.name, audio_path
    
    def _create_audio(self, text: str) -> str:
        """Create audio file from text using edge-tts for high quality male voice"""
        
        temp_audio_mp3 = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3').name
        
        try:
            asyncio.run(self._generate_edge_audio(text, temp_audio_mp3))
            return temp_audio_mp3
        except Exception as e:
            print(f"Error creating audio: {e}")
            return None

    async def _generate_edge_audio(self, text, output_path):
        communicate = edge_tts.Communicate(text, self.voice)
        await communicate.save(output_path)
    
    def _draw_centered_text(self, draw, text, y, font, color):
        """Draw centered text"""
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        x = (self.width - text_width) // 2
        draw.text((x, y), text, font=font, fill=color)
    
    def _draw_text(self, draw, text, x, y, font, color):
        """Draw text at position"""
        draw.text((x, y), text, font=font, fill=color)
    
    def _wrap_text(self, text: str, width: int) -> List[str]:
        """Wrap text to width"""
        return textwrap.wrap(text, width=width)
