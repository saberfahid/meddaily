"""
Generate enhanced video with larger, more readable text
"""
import json
from video_generator_enhanced import EnhancedVideoGenerator

def create_enhanced_video():
    """Create a video with larger text for better readability"""
    
    # Use the content from the last run
    sample_content = {
        'case_text': 'A 45-year-old male presents with headache and dizziness. Blood pressure is 160/100 mmHg. No other significant findings on examination.',
        'case_based_mcqs': [
            {
                'question': 'What is the most likely diagnosis in this patient with elevated blood pressure and no secondary causes identified?',
                'options': {
                    'A': 'Essential (primary) hypertension',
                    'B': 'Secondary hypertension due to kidney disease',
                    'C': 'White coat hypertension',
                    'D': 'Malignant hypertension with end-organ damage'
                }
            },
            {
                'question': 'Which of the following is NOT typically associated with essential hypertension?',
                'options': {
                    'A': 'Gradual onset over months to years',
                    'B': 'Elevated aldosterone levels',
                    'C': 'No identifiable secondary cause',
                    'D': 'Positive family history'
                }
            },
            {
                'question': 'What is the initial management approach for a patient diagnosed with stage 1 essential hypertension?',
                'options': {
                    'A': 'Immediate pharmacologic therapy',
                    'B': 'Lifestyle modifications for 3-6 months',
                    'C': 'Emergency department referral',
                    'D': 'Specialist consultation within 24 hours'
                }
            }
        ],
        'independent_mcqs': [
            {
                'question': 'What is the target blood pressure for most adults with hypertension according to current guidelines?',
                'options': {
                    'A': '<130/80 mmHg',
                    'B': '<140/90 mmHg',
                    'C': '<150/90 mmHg',
                    'D': '<160/100 mmHg'
                }
            },
            {
                'question': 'Which lifestyle modification has the greatest impact on blood pressure reduction?',
                'options': {
                    'A': 'Reducing sodium intake',
                    'B': 'Regular aerobic exercise',
                    'C': 'Weight loss in overweight patients',
                    'D': 'Limiting alcohol consumption'
                }
            }
        ],
        'answers': {'1': 'A', '2': 'B', '3': 'B', '4': 'A', '5': 'C'},
        'mnemonic': 'HEART: Healthy Eating, Exercise, Avoid smoking, Reduce stress, Take medication'
    }
    
    print("Creating enhanced video with larger text...")
    generator = EnhancedVideoGenerator()
    
    video_path = generator.create_video(
        content=sample_content,
        topic="Internal Medicine",
        subtopic="Hypertension - Essential Hypertension"
    )
    
    print(f"✅ Enhanced video created: {video_path}")
    print("This video has:")
    print("- 60% larger text than previous versions")
    print("- Better spacing between lines")
    print("- Fewer questions per slide for clarity")
    print("- Optimized for screenshot readability")
    
    # Open the video
    import subprocess
    subprocess.run(['explorer.exe', video_path])
    
    return video_path

if __name__ == "__main__":
    create_enhanced_video()