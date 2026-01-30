from gtts import gTTS
import os

def test_voices():
    text = "Hello, this is a test of the medical education application voice. Is this a male or female voice?"
    
    # Try different TLDs to find a more masculine sounding one
    tlds = {
        'us': 'en',
        'co.uk': 'en',
        'co.in': 'en',
        'ca': 'en'
    }
    
    for tld, lang in tlds.items():
        filename = f"test_voice_{tld.replace('.', '_')}.mp3"
        print(f"Generating {filename} with TLD {tld}...")
        tts = gTTS(text=text, lang=lang, tld=tld)
        tts.save(filename)
        print(f"Saved {filename}")

if __name__ == "__main__":
    test_voices()
