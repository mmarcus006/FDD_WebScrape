"""Main entry point for FDD WebScrape when used as a module."""

import sys
import asyncio
from src.main import main

if __name__ == "__main__":
    # Create event loop
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    finally:
        loop.close() 