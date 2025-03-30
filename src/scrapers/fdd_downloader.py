import os
import asyncio
import re
import requests
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
import time
from urllib.parse import urljoin

from src.config import USER_AGENT, FDD_DIR
from src.utils.file_operations import (
    generate_fdd_filename,
    create_fdd_filepath,
    get_file_size,
    get_current_date_string
)
from src.utils.pdf_utils import get_pdf_page_count


class FDDDownloader:
    """Downloader for Franchise Disclosure Documents."""

    def __init__(self):
        """Initialize the downloader."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'max-age=0',
            'DNT': '1',
            'Upgrade-Insecure-Requests': '1',
            'Content-Type': 'application/x-www-form-urlencoded'
        })

    def download_fdd(self, fdd_url: str, franchise_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Download an FDD document.
        
        Args:
            fdd_url (str): URL of the FDD document
            franchise_data (dict): Franchise data
            
        Returns:
            dict: Metadata about the downloaded FDD or None if an error occurs
        """
        try:
            # Extract information for the filename
            file_id = franchise_data['file_id']
            franchise_name = franchise_data['trade_name']
            effective_date = franchise_data['effective_date']
            effective_year = effective_date.split('/')[-1]  # Extract year from MM/DD/YYYY
            
            # Generate filename and filepath
            filename = generate_fdd_filename(file_id, franchise_name, effective_year)
            filepath = create_fdd_filepath(filename)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Get necessary request parameters
            # The download form requires the VIEWSTATE parameters which are dynamically generated
            # We need to make an initial request to get these values
            response = self.session.get(fdd_url)
            response.raise_for_status()
            
            # Extract VIEWSTATE fields
            viewstate = re.search(r'id="__VIEWSTATE" value="([^"]*)"', response.text)
            viewstate_generator = re.search(r'id="__VIEWSTATEGENERATOR" value="([^"]*)"', response.text)
            
            # Also look for additional viewstate fields
            viewstate_fields = {}
            viewstate_count_match = re.search(r'id="__VIEWSTATEFIELDCOUNT" value="([^"]*)"', response.text)
            if viewstate_count_match:
                viewstate_count = int(viewstate_count_match.group(1))
                # Extract each viewstate field
                for i in range(1, viewstate_count):
                    field_match = re.search(rf'id="__VIEWSTATE{i}" value="([^"]*)"', response.text)
                    if field_match:
                        viewstate_fields[f'__VIEWSTATE{i}'] = field_match.group(1)
            
            # Build the form data for the POST request
            form_data = {
                '__VIEWSTATEFIELDCOUNT': str(len(viewstate_fields) + 1) if viewstate_fields else '1',
                '__VIEWSTATE': viewstate.group(1) if viewstate else '',
                '__VIEWSTATEGENERATOR': viewstate_generator.group(1) if viewstate_generator else '',
                '__VIEWSTATEENCRYPTED': '',
                'upload_downloadFile': 'Download'
            }
            
            # Add additional viewstate fields
            form_data.update(viewstate_fields)
            
            # Make the download request
            download_response = self.session.post(fdd_url, data=form_data, stream=True)
            download_response.raise_for_status()
            
            # Check if the response is a PDF
            if 'application/pdf' not in download_response.headers.get('Content-Type', ''):
                print(f"Warning: Response is not a PDF for {franchise_name}")
                
            # Save the file
            with open(filepath, 'wb') as file:
                for chunk in download_response.iter_content(chunk_size=8192):
                    file.write(chunk)
            
            # Get file metadata
            file_size = get_file_size(filepath)
            download_date = get_current_date_string()
            num_pages = get_pdf_page_count(filepath)
            
            # Return metadata
            return {
                'fdd_url': fdd_url,
                'fdd_file_name': filename,
                'fdd_file_path': filepath,
                'fdd_file_size': file_size,
                'fdd_file_download_date': download_date,
                'num_pages': num_pages
            }
        
        except Exception as e:
            print(f"Error downloading FDD for {franchise_data.get('trade_name', 'unknown')}: {e}")
            return None

    def close(self):
        """Close the session."""
        if self.session:
            self.session.close()


# Function to download an FDD
def download_fdd(fdd_url: str, franchise_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Download an FDD document.
    
    Args:
        fdd_url (str): URL of the FDD document
        franchise_data (dict): Franchise data
        
    Returns:
        dict: Metadata about the downloaded FDD or None if an error occurs
    """
    downloader = FDDDownloader()
    try:
        return downloader.download_fdd(fdd_url, franchise_data)
    finally:
        downloader.close() 