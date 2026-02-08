"""
Generate Test Audio for Aged Care Robot Testing

Uses OpenAI TTS to create Margaret's medication question audio sample.
"""

from openai import OpenAI
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def generate_test_audio(force_regenerate=False):
    """Generate Margaret's medication question using OpenAI TTS
    
    Args:
        force_regenerate: If True, regenerate even if file exists
    """
    
    # Check if file already exists
    output_dir = Path(__file__).parent.parent / "audio_samples"
    output_file = output_dir / "margaret_medication_question.wav"
    
    if output_file.exists() and not force_regenerate:
        print(f"✅ Test audio already exists: {output_file}")
        print(f"📊 File size: {output_file.stat().st_size} bytes")
        print(f"\n💡 To regenerate, delete the file or run with --force flag")
        return output_file
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # The critical medication question from Margaret persona
    text = "Should I take my blood pressure pill now? I can't remember if I already took it today."
    
    print("🎙️  Generating test audio with OpenAI TTS...")
    print(f"📝 Text: {text}")
    
    # Generate speech with elderly-appropriate voice
    # OpenAI TTS returns various formats - we'll get raw PCM and convert to WAV
    response = client.audio.speech.create(
        model="tts-1",
        voice="nova",  # Female voice
        input=text,
        speed=0.9  # Slightly slower for elderly speech pattern
    )
    
   # Create output directory
    output_dir = Path(__file__).parent.parent / "audio_samples"
    output_dir.mkdir(exist_ok=True)
    
    # Save audio file
    output_file = output_dir / "margaret_medication_question.wav"
    
    # Get the raw audio bytes
    audio_bytes = response.content
    
    # OpenAI returns MP3, we need to convert to WAV
    # Save as temp MP3 first
    temp_mp3 = output_dir / "temp.mp3"
    with open(temp_mp3, 'wb') as f:
        f.write(audio_bytes)
    
    # Use pydub to convert MP3 to WAV
    try:
        from pydub import AudioSegment
        
        # Load MP3
        audio = AudioSegment.from_mp3(str(temp_mp3))
        
        # Convert to 16kHz mono WAV (required for acoustic simulation)
        audio = audio.set_frame_rate(16000).set_channels(1)
        
        # Export as WAV
        audio.export(str(output_file), format="wav")
        
        # Clean up temp file
        temp_mp3.unlink()
        
    except ImportError:
        print("⚠️  pydub not installed, attempting direct save...")
        # Fallback: save MP3 with .wav extension (will fail in tests)
        temp_mp3.rename(output_file)
        print("❌ WARNING: Audio is MP3 format, not WAV. Install pydub: pip install pydub")
    
    print(f"✅ Test audio generated successfully!")
    print(f"📁 Saved to: {output_file}")
    print(f"📊 File size: {output_file.stat().st_size} bytes")
    
    return output_file


if __name__ == "__main__":
    try:
        output = generate_test_audio()
        print("\n✅ Audio generation complete!")
        print("You can now run the tests with: pytest tests/ -v -s")
    except Exception as e:
        print(f"\n❌ Error generating audio: {e}")
        print("\nMake sure you have:")
        print("1. Set OPENAI_API_KEY in .env file")
        print("2. Installed all dependencies: pip install -r requirements.txt")
        exit(1)
