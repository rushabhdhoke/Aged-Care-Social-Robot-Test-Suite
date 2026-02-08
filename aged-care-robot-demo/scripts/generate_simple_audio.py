"""
Simple Audio Generator (Fallback if ffmpeg not available)

Creates a simple beep/tone WAV file for testing when OpenAI TTS
or ffmpeg is not available.
"""

import numpy as np
from scipy.io import wavfile
from pathlib import Path


def generate_simple_test_audio():
    """Generate a simple beep audio file for testing"""
    
    sample_rate = 16000  # 16 kHz
    duration = 5  # 5 seconds (approximate length of the medication question)
    
    # Create a simple tone (440 Hz - A note)
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # Generate a simple tone pattern (simulating speech rhythm)
    audio = np.zeros_like(t)
    
    # Add multiple frequency components to make it more speech-like
    audio += 0.3 * np.sin(2 * np.pi * 200 * t)  # Low frequency
    audio += 0.2 * np.sin(2 * np.pi * 400 * t)  # Mid frequency
    audio += 0.1 * np.sin(2 * np.pi * 800 * t)  # High frequency
    
    # Add amplitude modulation to simulate speech rhythm
    envelope = np.abs(np.sin(2 * np.pi * 2 * t))  # 2 Hz modulation
    audio = audio * envelope
    
    # Normalize
    audio = audio / np.max(np.abs(audio)) * 0.8
    
    # Convert to int16
    audio_int16 = (audio * 32767).astype(np.int16)
    
    # Save
    output_dir = Path(__file__).parent.parent / "audio_samples"
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "margaret_medication_question.wav"
    
    wavfile.write(output_file, sample_rate, audio_int16)
    
    print(f"✅ Generated simple test audio (beep tone)")
    print(f"📁 Saved to: {output_file}")
    print(f"📊 File size: {output_file.stat().st_size} bytes")
    print("\n⚠️  NOTE: This is a simple tone, not actual speech.")
    print("For real testing, install ffmpeg: sudo apt-get install ffmpeg")
    
    return output_file


if __name__ == "__main__":
    generate_simple_test_audio()
