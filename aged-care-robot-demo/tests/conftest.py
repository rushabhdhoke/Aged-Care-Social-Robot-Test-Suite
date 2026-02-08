"""
Pytest configuration and fixtures for aged care robot tests.
"""

import pytest
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
