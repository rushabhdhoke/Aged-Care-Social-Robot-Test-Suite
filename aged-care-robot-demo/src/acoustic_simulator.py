"""
Acoustic Simulator for Aged Care Robot Testing

Simulates realistic room acoustics using pyroomacoustics to test
robot performance at different distances from residents.
"""

import numpy as np
import pyroomacoustics as pra
from scipy.io import wavfile


class PrivateRoomSimulator:
    """
    Simulates acoustic environment of an aged care private room.
    
    Room dimensions: 4m × 5m × 3m (typical private room)
    Materials: Drywall walls, carpet floor, acoustic ceiling tiles
    
    This gives us realistic reverberation and distance attenuation
    for testing robot performance at different positions.
    """
    
    def __init__(self):
        # Room dimensions (meters)
        self.room_dim = [4.0, 5.0, 3.0]  # width, length, height
        
        # Material absorption coefficients (frequency-dependent)
        # Higher = more absorption, less echo
        # pyroom acoustics requires: east, west, north, south, floor, ceiling
        wall_material = pra.Material(0.05)  # Drywall (reflective)
        self.materials = {
            'east': wall_material,
            'west': wall_material,
            'north': wall_material,
            'south': wall_material,
            'floor': pra.Material(0.30),      # Carpet (absorptive)
            'ceiling': pra.Material(0.70)     # Acoustic tiles (very absorptive)
        }
        
    def simulate_conversation(self, clean_audio, distance_meters, sample_rate=16000):
        """
        Simulate audio as heard by robot at given distance from resident.
        
        Args:
            clean_audio: Clean speech signal (numpy array)
            distance_meters: Distance between robot and resident (1m or 3m)
            sample_rate: Audio sample rate (16kHz default for LiveKit)
            
        Returns:
            Simulated audio with room acoustics applied
        """
        
        # Create room with absorption materials
        room = pra.ShoeBox(
            self.room_dim,
            fs=sample_rate,
            materials=self.materials,
            max_order=3  # Number of reflections (realistic for small room)
        )
        
        # Resident position: seated, center of room
        resident_position = [2.0, 2.5, 0.5]  # x, y, z (0.5m = seated height)
        
        # Robot microphone position depends on test case
        # 1m test: Close conversation (private session)
        # 3m test: Far conversation (robot at room entrance)
        if distance_meters == 1.0:
            robot_position = [2.0, 1.5, 1.2]  # 1m away, standing height
        elif distance_meters == 3.0:
            robot_position = [2.0, 5.5, 1.2]  # Near doorway
        else:
            raise ValueError("Only 1m and 3m distances supported in demo")
        
        # Add sound source (resident speaking)
        room.add_source(resident_position, signal=clean_audio)
        
        # Add microphone (robot's mic)
        room.add_microphone(robot_position)
        
        # Simulate acoustic propagation
        room.simulate()
        
        # Get received audio at robot microphone
        simulated_audio = room.mic_array.signals[0, :]
        
        # Normalize to prevent clipping
        max_val = np.max(np.abs(simulated_audio))
        if max_val > 0:
            simulated_audio = simulated_audio / max_val * 0.8
        
        return simulated_audio


# Design Decisions:
# - Room dimensions (4×5×3m): Typical aged care private room size
# - Materials: Carpet floor (common), acoustic ceiling (standard in care facilities)
# - Max order=3: Balances realism vs computation (3 reflections captures main echoes)
# - 1m vs 3m: 1m = optimal private conversation, 3m = robot at room entrance
