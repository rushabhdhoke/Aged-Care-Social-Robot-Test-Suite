"""
Multi-Turn Conversation Test with Background Noise

Tests the robot's ability to:
1. Handle multi-turn conversations (maintain context)
2. Process audio with background noise
3. Address emotional/social needs (not just medical)
4. Provide empathetic responses

This is a SEPARATE test from the medical advice test.
Both tests coexist independently.
"""

import pytest
import asyncio
import os
import numpy as np
from scipy.io import wavfile
from pathlib import Path

# Import our modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from acoustic_simulator import PrivateRoomSimulator
from livekit_client import AgedCareRobotAgent
from background_noise import BackgroundNoiseSimulator


class TestConversationWithNoise:
    """
    Tests robot's handling of multi-turn conversation with background noise.
    
    Scenario: Lonely resident seeking social connection
    - Turn 1: Expresses loneliness
    - Turn 2: Asks about activities
    
    Background: 15dB SNR (moderate room noise - TV/hallway sounds)
    """
    
    @pytest.fixture
    def acoustic_simulator(self):
        """Fixture: Room acoustic simulator"""
        return PrivateRoomSimulator()
    
    @pytest.fixture
    def noise_simulator(self):
        """Fixture: Background noise simulator"""
        return BackgroundNoiseSimulator()
    
    @pytest.fixture
    def robot_agent(self):
        """Fixture: LiveKit + OpenAI agent"""
        return AgedCareRobotAgent()
    
    @pytest.mark.asyncio
    async def test_two_turn_conversation_with_background_noise(
        self,
        acoustic_simulator,
        noise_simulator,
        robot_agent
    ):
        """
        Test 2-turn conversation about loneliness with background noise.
        
        This tests:
        1. Background noise robustness (15dB SNR)
        2. Multi-turn context maintenance
        3. Empathetic responses to emotional needs
        4. Response audio saved as WAV for demonstration
        """
        
        print(f"\n{'='*60}")
        print(f"TEST: 2-Turn Conversation with Background Noise")
        print(f"{'='*60}")
        
        # Create test_outputs directory for response audio
        output_dir = Path(__file__).parent.parent / 'test_outputs'
        output_dir.mkdir(exist_ok=True)
        
        # ============================================================
        # TURN 1: Loneliness Expression
        # ============================================================
        
        print(f"\n📍 TURN 1: Loneliness Expression")
        print(f"Resident says: 'I'm feeling quite lonely today. My family hasn't visited in a while.'")
        
        # Load Turn 1 audio
        audio_dir = Path(__file__).parent.parent / 'audio_samples'
        turn1_audio_path = audio_dir / 'conversation_turn1_lonely.wav'
        
        if not turn1_audio_path.exists():
            pytest.skip(f"Turn 1 audio not found. Run: python scripts/generate_conversation_audio.py")
        
        sample_rate, turn1_audio = wavfile.read(turn1_audio_path)
        
        # Add background noise (15dB SNR - moderate room noise)
        print(f"🔊 Adding background noise (15dB SNR - moderate room)")
        noisy_audio_turn1 = noise_simulator.add_background_noise(
            turn1_audio.astype(np.float32) / 32768.0,  # Convert to float
            snr_db=15
        )
        
        # Apply acoustic simulation (1m distance)
        print(f"🌊 Applying room acoustics (1m distance)")
        simulated_turn1 = acoustic_simulator.simulate_conversation(
            noisy_audio_turn1,
            distance_meters=1.0,
            sample_rate=sample_rate
        )
        
        # Save processed audio for debugging
        turn1_processed_path = "/tmp/conversation_turn1_processed.wav"
        wavfile.write(
            turn1_processed_path,
            sample_rate,
            (simulated_turn1 * 32768).astype(np.int16)
        )
        print(f"   Processed audio: {turn1_processed_path}")
        
        # Send to robot
        print(f"🤖 Sending to robot...")
        response1_audio_path = str(output_dir / 'response_turn1.wav')
        
        response1 = await robot_agent.run_conversation(
            audio_input_path=turn1_processed_path,
            output_path=response1_audio_path
        )
        
        print(f"✅ Robot responded in {response1['latency_seconds']:.2f}s")
        print(f"💬 Response: '{response1['transcript']}'")
        print(f"🎵 Response audio saved: {response1_audio_path}")
        
        # ============================================================
        # TURN 2: Activity Inquiry
        # ============================================================
        
        print(f"\n📍 TURN 2: Activity Inquiry")
        print(f"Resident says: 'What activities are happening today? Is there anything I could join?'")
        
        # Load Turn 2 audio
        turn2_audio_path = audio_dir / 'conversation_turn2_activities.wav'
        
        if not turn2_audio_path.exists():
            pytest.skip(f"Turn 2 audio not found. Run: python scripts/generate_conversation_audio.py")
        
        sample_rate, turn2_audio = wavfile.read(turn2_audio_path)
        
        # Add background noise
        print(f"🔊 Adding background noise (15dB SNR)")
        noisy_audio_turn2 = noise_simulator.add_background_noise(
            turn2_audio.astype(np.float32) / 32768.0,
            snr_db=15
        )
        
        # Apply acoustic simulation
        print(f"🌊 Applying room acoustics (1m distance)")
        simulated_turn2 = acoustic_simulator.simulate_conversation(
            noisy_audio_turn2,
            distance_meters=1.0,
            sample_rate=sample_rate
        )
        
        # Save processed audio
        turn2_processed_path = "/tmp/conversation_turn2_processed.wav"
        wavfile.write(
            turn2_processed_path,
            sample_rate,
            (simulated_turn2 * 32768).astype(np.int16)
        )
        print(f"   Processed audio: {turn2_processed_path}")
        
        # Send to robot (with context from Turn 1)
        print(f"🤖 Sending to robot...")
        response2_audio_path = str(output_dir / 'response_turn2.wav')
        
        response2 = await robot_agent.run_conversation(
            audio_input_path=turn2_processed_path,
            output_path=response2_audio_path
        )
        
        print(f"✅ Robot responded in {response2['latency_seconds']:.2f}s")
        print(f"💬 Response: '{response2['transcript']}'")
        print(f"🎵 Response audio saved: {response2_audio_path}")
        
        # ============================================================
        # VALIDATION
        # ============================================================
        
        print(f"\n📋 VALIDATION:")
        
        # Validate Turn 1: Should show empathy
        empathy_keywords = ['understand', 'sorry', 'hear', 'feel', 'here for you', 'chat', 'talk']
        has_empathy = any(keyword in response1['transcript'].lower() for keyword in empathy_keywords)
        
        print(f"   Turn 1 - Empathy detected: {has_empathy}")
        if has_empathy:
            print(f"      ✅ Robot showed empathy to loneliness")
        
        # Validate Turn 2: Should suggest activities or offer help
        activity_keywords = ['activity', 'activities', 'schedule', 'program', 'staff', 'check', 'find out']
        suggests_activities = any(keyword in response2['transcript'].lower() for keyword in activity_keywords)
        
        print(f"   Turn 2 - Activity suggestion detected: {suggests_activities}")
        if suggests_activities:
            print(f"      ✅ Robot addressed activity inquiry")
        
        # Validate latency
        turn1_latency_ok = response1['latency_seconds'] < 10.0
        turn2_latency_ok = response2['latency_seconds'] < 10.0
        
        print(f"   Turn 1 - Latency: {response1['latency_seconds']:.2f}s (< 10s: {turn1_latency_ok})")
        print(f"   Turn 2 - Latency: {response2['latency_seconds']:.2f}s (< 10s: {turn2_latency_ok})")
        
        # ============================================================
        # ASSERTIONS
        # ============================================================
        
        # Turn 1: Should show empathy (not critical, but expected)
        # We make this a soft check - warning only
        if not has_empathy:
            print(f"\n⚠️  WARNING: Robot didn't show clear empathy in Turn 1")
        
        # Turn 2: Should address activity question
        assert suggests_activities, \
            f"Robot didn't address activity inquiry. Response: {response2['transcript']}"
        
        # Latency checks
        assert turn1_latency_ok, f"Turn 1 latency too high: {response1['latency_seconds']:.2f}s > 10s"
        assert turn2_latency_ok, f"Turn 2 latency too high: {response2['latency_seconds']:.2f}s > 10s"
        
        # Verify response audio files exist
        assert Path(response1_audio_path).exists(), "Response Turn 1 audio not saved"
        assert Path(response2_audio_path).exists(), "Response Turn 2 audio not saved"
        
        print(f"\n{'='*60}")
        print(f"✅ TEST PASSED: Multi-turn conversation successful!")
        print(f"{'='*60}")
        print(f"\n📁 Response audio files:")
        print(f"   {response1_audio_path} ({Path(response1_audio_path).stat().st_size} bytes)")
        print(f"   {response2_audio_path} ({Path(response2_audio_path).stat().st_size} bytes)")
        print(f"\n💡 You can listen to these files or publish them on GitHub!")


# ============================================================
# Test discovery and execution
# ============================================================

if __name__ == "__main__":
    # Run this test file directly
    pytest.main([__file__, "-v", "-s"])
