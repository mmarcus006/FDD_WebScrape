"""
Configure pytest for the FDD WebScrape project.

This file sets up sys.path to allow tests to import from the src directory.
"""
import os
import sys
from pathlib import Path

# Add the parent directory to sys.path to make src importable
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root)) 