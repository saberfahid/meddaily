import pyttsx3
import os

def test_male_voice():
    print("Initializing pyttsx3...")
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        print(f"Found {len(voices)} voices.")
        
        for i, voice in enumerate(voices):
            print(f"Voice {i}: {voice.name} (ID: {voice.id}, Gender: {getattr(voice, 'gender', 'unknown')})")
            
        # Select a voice that is likely male (often the first one in espeak is male)
        # Or specifically look for 'male' or 'm1', 'm2' etc.
        selected_voice = None
        for voice in voices:
            if 'male' in voice.name.lower() or 'm1' in voice.id.lower():
                selected_voice = voice.id
                print(f"Selected voice: {voice.name}")
                break
        
        if not selected_voice and voices:
            selected_voice = voices[0].id
            print(f"No explicitly male voice found, using first available: {voices[0].name}")
            
        if selected_voice:
            engine.setProperty('voice', selected_voice)
            engine.setProperty('rate', 150) # Slow down slightly for clarity
            
            output_file = "test_male_voice_output.mp3"
            text = "This is a test of the male medical educator voice. We are now using a professional masculine tone for all videos."
            
            print(f"Saving test audio to {output_file}...")
            engine.save_to_file(text, output_file)
            engine.runAndWait()
            print("Done.")
            return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    test_male_voice()
