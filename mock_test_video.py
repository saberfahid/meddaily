
import os
from video_generator_lite import LightweightVideoGenerator

def mock_test():
    content = {
        'case_text': "A 65-year-old male presents with shortness of breath and ankle swelling. He has a history of hypertension.",
        'case_based_mcqs': [
            {
                'question': "What is the most likely diagnosis?",
                'options': {
                    'A': "Acute Heart Failure",
                    'B': "Pneumonia",
                    'C': "Pulmonary Embolism",
                    'D': "Asthma"
                }
            }
        ],
        'independent_mcqs': [],
        'answers': {'1': 'A'},
        'mnemonic': "FAILURE: Fatigue, Activities limited, In chest congestion, Edema, Shortness of breath."
    }
    
    print("Creating mock video with male voice...")
    video_gen = LightweightVideoGenerator()
    video_path = video_gen.create_video(content, "Heart Failure", "Mock Test")
    print(f"✅ Mock video created: {video_path}")

if __name__ == "__main__":
    mock_test()
