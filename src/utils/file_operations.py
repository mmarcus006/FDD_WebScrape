import os
import shutil
from datetime import datetime
from pathlib import Path
import requests
from typing import Optional, Dict, Any

from src.config import FDD_DIR


def download_file(url: str, output_path: str, headers: Optional[Dict[str, str]] = None) -> bool:
    """Download a file from a URL to the specified path.
    
    Args:
        url (str): URL of the file to download
        output_path (str): Path where the file will be saved
        headers (dict, optional): HTTP headers to use for the request
        
    Returns:
        bool: True if download was successful, False otherwise
    """
    try:
        with requests.get(url, headers=headers, stream=True) as response:
            response.raise_for_status()
            with open(output_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
        return True
    except Exception as e:
        print(f"Error downloading file: {e}")
        return False


def save_html_to_file(html_content: str, filename: str) -> str:
    """Save HTML content to a file.
    
    Args:
        html_content (str): HTML content to save
        filename (str): Name of the file
        
    Returns:
        str: Path of the saved file
    """
    output_path = Path(f"data/{filename}")
    os.makedirs(output_path.parent, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(html_content)
    
    return str(output_path)


def generate_fdd_filename(file_id: str, franchise_name: str, effective_year: str) -> str:
    """Generate a standardized filename for an FDD document.
    
    Args:
        file_id (str): File ID
        franchise_name (str): Name of the franchise
        effective_year (str): Year when the filing became effective
        
    Returns:
        str: Standardized filename
    """
    # Clean franchise name for use in filename
    clean_name = franchise_name.strip()
    clean_name = ''.join(c if c.isalnum() or c.isspace() else '_' for c in clean_name)
    clean_name = clean_name.replace(' ', '_')
    
    return f"{file_id}_{clean_name}_{effective_year}.pdf"


def create_fdd_filepath(filename: str) -> str:
    """Create the full path for an FDD file.
    
    Args:
        filename (str): Name of the FDD file
        
    Returns:
        str: Full path to the FDD file
    """
    return str(FDD_DIR / filename)


def get_file_size(file_path: str) -> Optional[int]:
    """Get the size of a file in bytes.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        int: Size of the file in bytes or None if the file doesn't exist
    """
    try:
        return os.path.getsize(file_path)
    except (FileNotFoundError, OSError):
        return None


def get_current_date_string() -> str:
    """Get the current date as a string in ISO format.
    
    Returns:
        str: Current date in YYYY-MM-DD format
    """
    return datetime.now().strftime('%Y-%m-%d') 