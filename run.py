#!/usr/bin/env python3
"""
Executable script to run the FDD WebScrape application.

This script sets up the asyncio event loop and runs the main application.
"""

import asyncio
import sys
from src.main import main

if __name__ == "__main__":
    # Create event loop
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    finally:
        loop.close()
        sys.exit(0) 