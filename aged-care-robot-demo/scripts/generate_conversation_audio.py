"""
Generate conversational test audio for aged care scenarios.

Creates a 2-turn conversation:
- Turn 1: Resident asks about feeling lonely
- Turn 2: Follow-up question about activities

This tests multi-turn context handling with background noise.
"""

from openai import OpenAI
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def generate_conversation_audio(force_regenerate=False):
    """
    Generate 2-turn conversation audio with lonely resident scenario.
    
    This scenario tests:
    - Multi-turn conversation context
    - Emotional/social needs (not medical)
    - Background noise robustness
    """
    
    output_dir = Path(__file__).parent.parent / "audio_samples"
    output_dir.mkdir(exist_ok=True)
    
    # Check if files already exist
    turn1_file = output_dir / "conversation_turn1_lonely.wav"
    turn2_file = output_dir / "conversation_turn2_activities.wav"
    
    if turn1_file.exists() and turn2_file.exists() and not force_regenerate:
        print(f"✅ Conversation audio already exists")
        print(f"   Turn 1: {turn1_file}")
        print(f"   Turn 2: {turn2_file}")
        print(f"\n💡 To regenerate, delete files or use --force flag")
        return turn1_file, turn2_file
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Conversation turns
    conversations = [
        {
            'text': "I'm feeling quite lonely today. My family hasn't visited in a while.",
            'filename': 'conversation_turn1_lonely.wav',
            'desc': 'Turn 1: Loneliness expression'
        },
        {
            'text': "What activities are happening today? Is there anything I could join?",
            'filename': 'conversation_turn2_activities.wav',
            'desc': 'Turn 2: Activity inquiry'
        }
    ]
    
    print("🎙️  Generating 2-turn conversation audio...")
    
    for conv in conversations:
        print(f"\n📝 {conv['desc']}")
        print(f"   Text: {conv['text']}")
        
        output_file = output_dir / conv['filename']
        
        # Generate speech
        response = client.audio.speech.create(
            model="tts-1",
            voice="nova",  # Female elderly voice
            input=conv['text'],
            speed=0.9  # Slightly slower for elderly speech
        )
        
        # Get audio bytes
        audio_bytes = response.content
        
        # Save as temp MP3
        temp_mp3 = output_dir / f"temp_{conv['filename']}.mp3"
        with open(temp_mp3, 'wb') as f:
            f.write(audio_bytes)
        
        # Convert to WAV using pydub
        try:
            from pydub import AudioSegment
            
            audio = AudioSegment.from_mp3(str(temp_mp3))
            audio = audio.set_frame_rate(16000).set_channels(1)
            audio.export(str(output_file), format="wav")
            temp_mp3.unlink()
            
            print(f"   ✅ Saved: {output_file}")
            print(f"   📊 Size: {output_file.stat().st_size} bytes")
            
        except ImportError:
            print("❌ pydub not installed")
            temp_mp3.rename(output_file)
    
    print(f"\n✅ Conversation audio generation complete!")
    return turn1_file, turn2_file


if __name__ == "__main__":
    try:
        generate_conversation_audio()
        print("\nReady for multi-turn conversation testing!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        exit(1)
