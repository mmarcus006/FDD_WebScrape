"""Utilities for testing the FDD WebScrape application."""

import tempfile
import os
import sys
from pathlib import Path
from contextlib import contextmanager


@contextmanager
def temp_file(content=None, suffix=None):
    """Create a temporary file with the given content.
    
    Args:
        content (bytes, optional): Content to write to the file
        suffix (str, optional): File suffix (e.g., '.pdf')
        
    Yields:
        str: Path to the temporary file
    """
    fd, path = tempfile.mkstemp(suffix=suffix)
    try:
        if content:
            with os.fdopen(fd, 'wb') as f:
                f.write(content)
        else:
            os.close(fd)
        yield path
    finally:
        try:
            os.unlink(path)
        except (OSError, IOError):
            pass


@contextmanager
def temp_directory():
    """Create a temporary directory.
    
    Yields:
        str: Path to the temporary directory
    """
    temp_dir = tempfile.mkdtemp()
    try:
        yield temp_dir
    finally:
        try:
            import shutil
            shutil.rmtree(temp_dir)
        except (OSError, IOError):
            pass


def get_project_root():
    """Get the project root directory.
    
    Returns:
        Path: Path to the project root directory
    """
    return Path(__file__).parent.parent 