
import asyncio
import edge_tts

async def list_voices():
    voices = await edge_tts.VoicesManager.create()
    male_voices = voices.find(Gender="Male", Language="en")
    for v in male_voices:
        print(f"Name: {v['ShortName']}, Gender: {v['Gender']}, FriendlyName: {v['FriendlyName']}")

async def test_voice(voice_name, text, output_file):
    communicate = edge_tts.Communicate(text, voice_name)
    await communicate.save(output_file)
    print(f"Saved {output_file} using {voice_name}")

if __name__ == "__main__":
    print("Listing English Male Voices:")
    asyncio.run(list_voices())
    
    text = "Hello, this is a professional medical educator voice. We are using high-quality neural text-to-speech for our educational videos."
    # Testing a common high-quality male voice
    asyncio.run(test_voice("en-US-GuyNeural", text, "test_edge_guy.mp3"))
    asyncio.run(test_voice("en-GB-RyanNeural", text, "test_edge_ryan.mp3"))
