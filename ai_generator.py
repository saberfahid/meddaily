"""
AI Content Generation Module
Uses Mistral AI to generate medical educational content
"""

import os
import json
import re
from typing import Dict, Any, Optional
from openai import OpenAI


class MedicalContentGenerator:
    """Generates medical educational content using Mistral AI"""
    
    def __init__(self, model: str = "mistral-small-latest"):
        """
        Initialize the AI content generator
        Uses Mistral AI API
        """
        self.client = OpenAI(
            api_key="l3pdbDohuqIBhQCPJWw7BkZ9QUtFRsWJ",
            base_url="https://api.mistral.ai/v1"
        )
        self.model = model
    
    def generate_educational_content(self, topic: str, subtopic: str) -> Dict[str, Any]:
        """
        Generate complete educational content for a medical topic
        
        Returns:
        {
            'case_text': str,
            'case_based_mcqs': [{'question': str, 'options': {'A': str, 'B': str, 'C': str, 'D': str}}, ...],
            'independent_mcqs': [{'question': str, 'options': {...}}, ...],
            'answers': {'1': 'A', '2': 'B', '3': 'C', '4': 'D', '5': 'A'},
            'mnemonic': str
        }
        """
        
        prompt = self._create_content_prompt(topic, subtopic)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert medical educator creating high-yield, exam-focused content for medical students preparing for USMLE, PLAB, and similar exams. 

Your content must be:
- Clinically accurate and evidence-based
- Concise and focused on high-yield information
- Exam-oriented with realistic clinical scenarios
- Memorable with effective mnemonics

Format your response as valid JSON with the exact structure requested."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.8,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            
            # Parse JSON response
            parsed_content = self._parse_ai_response(content)
            
            return parsed_content
            
        except Exception as e:
            print(f"Error generating content: {e}")
            raise
    
    def _create_content_prompt(self, topic: str, subtopic: str) -> str:
        """Create the prompt for content generation"""
        
        prompt = f"""Generate medical educational content for:
**Topic**: {topic}
**Subtopic**: {subtopic}

Create the following in JSON format:

1. **Clinical Case** (1-2 sentences): A brief, realistic clinical scenario that hooks the learner. Include key presenting symptoms, relevant history, and physical exam findings.

2. **Case-Based MCQs** (3 questions): Create 3 multiple-choice questions directly related to the clinical case. Each should test different aspects (diagnosis, management, complications, etc.). Each question must have 4 options (A, B, C, D).

3. **Independent MCQs** (2 questions): Create 2 additional MCQs on the same topic/subtopic but NOT directly related to the case. These should test core concepts, mechanisms, or clinical pearls. Each must have 4 options (A, B, C, D).

4. **Answers**: Provide correct answers for all 5 questions (format: {{"1": "B", "2": "A", "3": "D", "4": "C", "5": "A"}})

5. **Mnemonic** (1 short mnemonic): Create a memorable, easy-to-recall mnemonic for a key concept related to this topic. Keep it under 10 words.

**Output Format (JSON)**:
{{
  "case_text": "Brief 1-2 sentence clinical case here",
  "case_based_mcqs": [
    {{
      "question": "Question 1 text?",
      "options": {{
        "A": "Option A text",
        "B": "Option B text",
        "C": "Option C text",
        "D": "Option D text"
      }}
    }},
    {{
      "question": "Question 2 text?",
      "options": {{
        "A": "Option A text",
        "B": "Option B text",
        "C": "Option C text",
        "D": "Option D text"
      }}
    }},
    {{
      "question": "Question 3 text?",
      "options": {{
        "A": "Option A text",
        "B": "Option B text",
        "C": "Option C text",
        "D": "Option D text"
      }}
    }}
  ],
  "independent_mcqs": [
    {{
      "question": "Question 4 text?",
      "options": {{
        "A": "Option A text",
        "B": "Option B text",
        "C": "Option C text",
        "D": "Option D text"
      }}
    }},
    {{
      "question": "Question 5 text?",
      "options": {{
        "A": "Option A text",
        "B": "Option B text",
        "C": "Option C text",
        "D": "Option D text"
      }}
    }}
  ],
  "answers": {{
    "1": "B",
    "2": "A",
    "3": "D",
    "4": "C",
    "5": "A"
  }},
  "mnemonic": "Short memorable mnemonic here"
}}

Return ONLY the JSON object, no additional text."""
        
        return prompt
    
    def _parse_ai_response(self, content: str) -> Dict[str, Any]:
        """Parse and validate AI response"""
        
        # Try to extract JSON from response
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
        else:
            json_str = content
        
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {e}")
            print(f"Content: {content}")
            raise
        
        # Validate structure
        required_keys = ['case_text', 'case_based_mcqs', 'independent_mcqs', 'answers', 'mnemonic']
        for key in required_keys:
            if key not in data:
                raise ValueError(f"Missing required key: {key}")
        
        # Validate MCQs structure
        if len(data['case_based_mcqs']) != 3:
            raise ValueError("Expected 3 case-based MCQs")
        if len(data['independent_mcqs']) != 2:
            raise ValueError("Expected 2 independent MCQs")
        
        return data
    
    def format_for_display(self, content: Dict[str, Any], topic: str, subtopic: str) -> str:
        """Format content for display/video"""
        
        formatted = f"🩺 {topic}: {subtopic}\n\n"
        formatted += f"📌 Case:\n{content['case_text']}\n\n"
        formatted += "❓ MCQs:\n"
        
        # Combine all MCQs
        all_mcqs = content['case_based_mcqs'] + content['independent_mcqs']
        for i, mcq in enumerate(all_mcqs, 1):
            formatted += f"{i}) {mcq['question']}\n"
            for option, text in mcq['options'].items():
                formatted += f"   {option}) {text}\n"
            formatted += "\n"
        
        formatted += "✅ Answers:\n"
        answers_str = " ".join([f"{k}-{v}" for k, v in sorted(content['answers'].items())])
        formatted += answers_str + "\n\n"
        
        formatted += f"🧠 Mnemonic:\n{content['mnemonic']}\n"
        
        return formatted
    
    def format_for_youtube_description(self, content: Dict[str, Any], topic: str, subtopic: str) -> str:
        """Format content for YouTube description"""
        
        description = f"🩺 {topic}: {subtopic}\n\n"
        description += f"📌 Case:\n{content['case_text']}\n\n"
        description += "❓ MCQs:\n"
        
        all_mcqs = content['case_based_mcqs'] + content['independent_mcqs']
        for i, mcq in enumerate(all_mcqs, 1):
            description += f"{i}) {mcq['question']}\n"
        
        description += "\n✅ Answers:\n"
        answers_str = " ".join([f"{k}-{v}" for k, v in sorted(content['answers'].items())])
        description += answers_str + "\n\n"
        
        description += f"🧠 Mnemonic:\n{content['mnemonic']}\n\n"
        description += "#Medical #USMLE #PLAB #Shorts #MedicalEducation #MedicalStudent"
        
        return description
    
    def format_for_telegram(self, content: Dict[str, Any], topic: str, subtopic: str, 
                           youtube_url: str = None) -> str:
        """Format content for Telegram post"""
        
        message = f"🩺 {topic}: {subtopic}\n\n"
        message += f"📌 Case:\n{content['case_text']}\n\n"
        message += "❓ MCQs:\n"
        
        all_mcqs = content['case_based_mcqs'] + content['independent_mcqs']
        for i, mcq in enumerate(all_mcqs, 1):
            # Shortened version for Telegram
            question = mcq['question']
            if len(question) > 100:
                question = question[:97] + "..."
            message += f"{i}) {question}\n"
        
        message += f"\n🧠 Mnemonic:\n{content['mnemonic']}\n"
        
        if youtube_url:
            message += f"\n▶ Watch: {youtube_url}"
        
        return message
    
    def generate_new_topics(self, subject: str, count: int = 10) -> list:
        """
        Generate new medical topics/subtopics using AI
        Used when topic count is low
        """
        
        prompt = f"""Generate {count} new medical education topics for the subject: {subject}

Each topic should include:
1. A main topic category
2. A specific subtopic

The topics should be:
- Clinically relevant and high-yield for medical exams
- Not too basic, not too advanced (appropriate for medical students)
- Diverse and covering different aspects of {subject}
- Exam-focused (USMLE, PLAB style)

Return as JSON array:
[
  {{"topic": "Main Topic", "subtopic": "Specific Subtopic"}},
  ...
]

Return ONLY the JSON array, no additional text."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert medical educator creating curriculum content."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.9,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content
            
            # Extract JSON
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                json_str = content
            
            topics = json.loads(json_str)
            return topics
            
        except Exception as e:
            print(f"Error generating new topics: {e}")
            return []


# Test function
def test_generator():
    """Test the content generator"""
    generator = MedicalContentGenerator()
    
    # Test content generation
    print("Testing content generation...")
    content = generator.generate_educational_content(
        topic="Heart Failure",
        subtopic="Acute Heart Failure"
    )
    
    print("\n=== Generated Content ===")
    print(json.dumps(content, indent=2))
    
    print("\n=== Formatted for Display ===")
    formatted = generator.format_for_display(content, "Heart Failure", "Acute Heart Failure")
    print(formatted)
    
    print("\n=== YouTube Description ===")
    yt_desc = generator.format_for_youtube_description(content, "Heart Failure", "Acute Heart Failure")
    print(yt_desc)
    
    print("\n=== Telegram Message ===")
    tg_msg = generator.format_for_telegram(
        content, "Heart Failure", "Acute Heart Failure", 
        youtube_url="https://youtube.com/shorts/example"
    )
    print(tg_msg)


if __name__ == "__main__":
    test_generator()
