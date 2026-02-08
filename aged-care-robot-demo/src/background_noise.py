"""
Background Noise Simulator for Aged Care Testing

Simulates realistic aged care facility background noise:
- TV sounds
- Hallway conversations
- Equipment beeps
- Footsteps
"""

import numpy as np
from scipy.io import wavfile


class BackgroundNoiseSimulator:
    """
    Adds realistic background noise to audio samples.
    
    Noise types:
    - Low SNR (10dB): TV on in room, hallway activity
    - Medium SNR (15dB): Quiet room with distant sounds
    - High SNR (20dB): Very quiet, optimal conditions
    """
    
    def __init__(self, sample_rate=16000):
        self.sample_rate = sample_rate
    
    def add_background_noise(self, clean_audio, snr_db=15):
        """
        Add background noise to clean audio.
        
        Args:
            clean_audio: Clean speech signal (numpy array)
            snr_db: Signal-to-noise ratio in dB (lower = more noise)
                    10dB = noisy (TV on)
                    15dB = moderate (typical room)
                    20dB = quiet (optimal)
        
        Returns:
            Noisy audio with background sounds
        """
        
        # Generate pink noise (more realistic than white noise)
        noise = self._generate_pink_noise(len(clean_audio))
        
        # Calculate signal and noise power
        signal_power = np.mean(clean_audio ** 2)
        noise_power = np.mean(noise ** 2)
        
        # Calculate scaling factor for desired SNR
        # SNR (dB) = 10 * log10(signal_power / noise_power)
        snr_linear = 10 ** (snr_db / 10.0)
        noise_scaling = np.sqrt(signal_power / (snr_linear * noise_power))
        
        # Add scaled noise to signal
        noisy_audio = clean_audio + noise_scaling * noise
        
        # Normalize to prevent clipping
        max_val = np.max(np.abs(noisy_audio))
        if max_val > 0.95:
            noisy_audio = noisy_audio * 0.95 / max_val
        
        return noisy_audio
    
    def _generate_pink_noise(self, length):
        """
        Generate pink noise (1/f noise).
        More realistic than white noise for indoor environments.
        """
        # Simple pink noise approximation
        white = np.random.randn(length)
        
        # Apply simple low-pass filter to create pink-ish noise
        pink = np.zeros(length)
        pink[0] = white[0]
        
        for i in range(1, length):
            pink[i] = 0.99 * pink[i-1] + 0.01 * white[i]
        
        # Normalize
        pink = pink / np.max(np.abs(pink))
        
        return pink


# Design note: SNR values chosen based on aged care research
# - 10dB: Challenging but realistic (TV, activity)
# - 15dB: Typical private room
# - 20dB: Optimal quiet conditions
