"""
This file contains shared fixtures and hooks for the test suite.
"""

import sys
from pathlib import Path

# Add the project root's 'src' directory to the Python path
# so that pytest can find the source modules.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
