"""
Medical Education Content Generator
Uses Mistral AI to generate daily medical content
"""
import os
import json
from openai import OpenAI

class MedicalContentGenerator:
    def __init__(self, model: str = "mistral-small-latest"):
        # Use environment variable or fallback to hardcoded key
        api_key = os.getenv("MISTRAL_API_KEY", "l3pdbDohuqIBhQCPJWw7BkZ9QUtFRsWJ")
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.mistral.ai/v1"
        )
        self.model = model
    
    def generate_educational_content(self, topic: str, subtopic: str) -> dict:
        prompt = f"""Generate medical educational content for:
**Topic**: {topic}
**Subtopic**: {subtopic}

Create the following in JSON format:
1. **Clinical Case** (1-2 sentences): Brief realistic clinical scenario
2. **Case-Based MCQs** (3 questions): Related to the clinical case
3. **Independent MCQs** (2 questions): Core concepts on same topic
4. **Answers**: {{'1': 'B', '2': 'A', '3': 'D', '4': 'C', '5': 'A'}}
5. **Mnemonic** (1 short mnemonic): Memorable concept aid

**Output Format (JSON)**:
{{
  "case_text": "Brief clinical case here",
  "case_based_mcqs": [
    {{
      "question": "Question 1?",
      "options": {{
        "A": "Option A",
        "B": "Option B", 
        "C": "Option C",
        "D": "Option D"
      }}
    }}
  ],
  "independent_mcqs": [
    {{
      "question": "Question 4?",
      "options": {{
        "A": "Option A",
        "B": "Option B",
        "C": "Option C", 
        "D": "Option D"
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
  "mnemonic": "Short mnemonic here"
}}

Return ONLY the JSON object."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert medical educator creating high-yield exam content. Always return valid JSON only, no markdown formatting."
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
            
            # Clean up response - remove markdown code blocks if present
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            elif content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            return json.loads(content)
            
        except Exception as e:
            print(f"Error: {e}")
            raise

# Test function
if __name__ == "__main__":
    generator = MedicalContentGenerator()
    content = generator.generate_educational_content("Cardiology", "Acute Coronary Syndrome")
    print(json.dumps(content, indent=2))