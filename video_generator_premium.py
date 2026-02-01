"""
Premium Video Generation Module
Creates modern, high-retention vertical videos for YouTube Shorts
Design: Dark gradient, cyan/orange/green accents, clean typography
"""

import os
import subprocess
import asyncio
import edge_tts
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from typing import Dict, Any

class PremiumVideoGenerator:
    def __init__(self, output_dir: str = "videos"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.width = 1080
        self.height = 1920
        # Colors from design prompt
        self.colors = {
            'bg_start': (15, 23, 42),   # #0F172A
            'bg_end': (2, 6, 23),       # #020617
            'text': (255, 255, 255),
            'accent_case': (255, 165, 0), # Orange
            'accent_q': (0, 255, 255),    # Cyan
            'accent_a': (0, 255, 0)       # Green
        }
        
        # High-quality neural male voice
        self.voice = "en-US-GuyNeural"

    def _create_gradient_bg(self):
        base = Image.new('RGB', (self.width, self.height), self.colors['bg_start'])
        top = self.colors['bg_start']
        bottom = self.colors['bg_end']
        
        draw = ImageDraw.Draw(base)
        for y in range(self.height):
            r = int(top[0] + (bottom[0] - top[0]) * (y / self.height))
            g = int(top[1] + (bottom[1] - top[1]) * (y / self.height))
            b = int(top[2] + (bottom[2] - top[2]) * (y / self.height))
            draw.line([(0, y), (self.width, y)], fill=(r, g, b))
        return base

    def create_video(self, content: Dict[str, Any], topic: str, subtopic: str, filename: str = None) -> str:
        if not filename:
            filename = f"{topic}_{subtopic}".replace(" ", "_")[:50] + ".mp4"
        
        output_path = os.path.join(self.output_dir, filename)
        temp_dir = "temp_slides"
        os.makedirs(temp_dir, exist_ok=True)
        
        slides = []
        
        # Slide 1: Hook (5s)
        slides.append(self._gen_slide(temp_dir, "slide1.png", [
            {"text": "🩺 DAILY MEDICAL CASE", "size": 72, "color": self.colors['text'], "y": 600},
            {"text": "Can you diagnose this?", "size": 85, "color": self.colors['accent_q'], "y": 850, "bold": True},
            {"text": "Think before the answer", "size": 58, "color": self.colors['text'], "y": 1050}
        ], duration=5, audio_text="Daily medical case. Can you diagnose this? Think before the answer."))

        # Slide 2: Case (10s) - Shortened
        case_lines = content['case_text'].split('.')[:2]
        case_display = ". ".join(case_lines) + "."
        slides.append(self._gen_slide(temp_dir, "slide2.png", [
            {"text": "📌 Clinical Case", "size": 80, "color": self.colors['accent_case'], "y": 350},
            {"text": case_display, "size": 58, "color": self.colors['text'], "y": 600, "wrap": True}
        ], duration=10, audio_text=f"Clinical case. {case_display}"))

        # Slide 3: MCQs (10s)
        mcq = content['case_based_mcqs'][0]
        mcq_lines = [f"{k}) {v}" for k, v in mcq['options'].items()]
        mcq_data = [{"text": "❓ Most Likely Diagnosis?", "size": 72, "color": self.colors['accent_q'], "y": 300}]
        for i, line in enumerate(mcq_lines):
            mcq_data.append({"text": line, "size": 54, "color": self.colors['text'], "y": 550 + (i * 180), "wrap": True})
        
        slides.append(self._gen_slide(temp_dir, "slide3.png", mcq_data, duration=10, 
                                     audio_text=f"What is the most likely diagnosis? A, {mcq['options']['A']}. B, {mcq['options']['B']}. C, {mcq['options']['C']}. or D, {mcq['options']['D']}."))

        # Slide 4: Think Pause (5s)
        slides.append(self._gen_slide(temp_dir, "slide4.png", [
            {"text": "⏳ Think for 5 seconds", "size": 80, "color": self.colors['text'], "y": 900}
        ], duration=5, audio_text="")) # No voice

        # Slide 5: Answer + Mnemonic (10s)
        ans_key = content['answers']['1']
        ans_text = content['case_based_mcqs'][0]['options'][ans_key]
        slides.append(self._gen_slide(temp_dir, "slide5.png", [
            {"text": f"✅ Correct Answer: {ans_key}", "size": 90, "color": self.colors['accent_a'], "y": 350},
            {"text": ans_text, "size": 62, "color": self.colors['text'], "y": 520, "wrap": True},
            {"text": "🧠 Mnemonic", "size": 72, "color": self.colors['accent_case'], "y": 950},
            {"text": content['mnemonic'], "size": 52, "color": self.colors['text'], "y": 1100, "wrap": True}
        ], duration=10, audio_text=f"The correct answer is {ans_key}, {ans_text}. Here is a mnemonic: {content['mnemonic']}"))

        # Slide 6: CTA (5s)
        slides.append(self._gen_slide(temp_dir, "slide6.png", [
            {"text": "Daily medical cases", "size": 75, "color": self.colors['text'], "y": 800},
            {"text": "Follow for more!", "size": 90, "color": self.colors['accent_q'], "y": 1000, "bold": True}
        ], duration=5, audio_text="Follow for more daily medical cases."))

        # Combine into video
        self._assemble_video(slides, output_path)
        return output_path

    def _gen_slide(self, temp_dir, name, elements, duration, audio_text):
        img = self._create_gradient_bg()
        draw = ImageDraw.Draw(img)
        
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        ]
        font_path = next((p for p in font_paths if os.path.exists(p)), None)
        
        if not font_path:
            print("WARNING: No font found, text may be small!")
            
        for el in elements:
            size = el['size']
            color = el['color']
            y = el['y']
            text = el['text']
            f = ImageFont.truetype(font_path, size) if font_path else ImageFont.load_default()
            
            if el.get('wrap'):
                lines = self._wrap_text(text, f, self.width - 160)
                current_y = y
                for line in lines:
                    w = draw.textlength(line, font=f)
                    draw.text(((self.width - w) / 2, current_y), line, font=f, fill=color)
                    current_y += int(size * 1.4)  # Better line spacing
            else:
                w = draw.textlength(text, font=f)
                draw.text(((self.width - w) / 2, y), text, font=f, fill=color)
        
        img_path = os.path.join(temp_dir, name)
        img.save(img_path)
        
        audio_path = os.path.join(temp_dir, name.replace(".png", ".mp3"))
        actual_duration = duration
        
        if audio_text:
            try:
                # Use edge-tts for high quality neural voice
                asyncio.run(self._generate_edge_audio(audio_text, audio_path))
                
                # Use ffprobe to get the actual duration
                result = subprocess.run([
                    "ffprobe", "-v", "error", "-show_entries", "format=duration", 
                    "-of", "default=noprint_wrappers=1:nokey=1", audio_path
                ], capture_output=True, text=True)
                if result.stdout.strip():
                    actual_duration = float(result.stdout.strip()) + 1.0 
            except Exception as e:
                print(f"Error generating voice: {e}")
        elif not audio_text:
            subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t", str(duration), audio_path], capture_output=True)
            
        return {"img": img_path, "audio": audio_path, "duration": actual_duration}

    async def _generate_edge_audio(self, text, output_path):
        communicate = edge_tts.Communicate(text, self.voice)
        await communicate.save(output_path)

    def _wrap_text(self, text, font, max_width):
        lines = []
        words = text.split()
        current_line = []
        for word in words:
            test_line = " ".join(current_line + [word])
            w = font.getlength(test_line)
            if w <= max_width:
                current_line.append(word)
            else:
                lines.append(" ".join(current_line))
                current_line = [word]
        lines.append(" ".join(current_line))
        return lines

    def _assemble_video(self, slides, output_path):
        slide_videos = []
        for i, s in enumerate(slides):
            v_part = os.path.join("temp_slides", f"part_{i}.mp4")
            subprocess.run([
                "ffmpeg", "-y", "-loop", "1", "-i", s['img'], "-i", s['audio'],
                "-c:v", "libx264", "-t", str(s['duration']), "-pix_fmt", "yuv420p",
                "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2",
                "-c:a", "aac", "-b:a", "192k", v_part
            ], capture_output=True)
            slide_videos.append(v_part)
            
        parts_file = os.path.join("temp_slides", "parts.txt")
        with open(parts_file, "w") as f:
            for v in slide_videos:
                f.write(f"file '{os.path.abspath(v)}'\n")
        
        subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", parts_file,
            "-c", "copy", output_path
        ], capture_output=True)
        
        # Cleanup
        for v in slide_videos: 
            if os.path.exists(v): os.remove(v)
        if os.path.exists(parts_file): os.remove(parts_file)
