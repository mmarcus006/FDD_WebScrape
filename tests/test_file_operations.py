import os
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
import datetime
import shutil

from src.utils.file_operations import (
    download_file,
    save_html_to_file,
    generate_fdd_filename,
    create_fdd_filepath,
    get_file_size,
    get_current_date_string
)
from tests.utils import temp_file, temp_directory


class TestFileOperations(unittest.TestCase):
    """Test cases for file operation utility functions."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for test files
        self.temp_dir = tempfile.TemporaryDirectory()
        
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, dir=self.temp_dir.name)
        self.temp_file.write(b"Test content")
        self.temp_file.close()

    def tearDown(self):
        """Clean up test environment."""
        # Remove temporary files
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
        self.temp_dir.cleanup()

    @patch('src.utils.file_operations.requests.get')
    def test_download_file_success(self, mock_get):
        """Test downloading a file successfully."""
        # Mock response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.__enter__.return_value = mock_response
        mock_response.iter_content.return_value = [b"Test", b" ", b"content"]
        mock_get.return_value = mock_response
        
        # Download a file
        url = "https://example.com/file.pdf"
        output_path = os.path.join(self.temp_dir.name, "downloaded_file.pdf")
        headers = {"User-Agent": "Test User Agent"}
        
        result = download_file(url, output_path, headers)
        
        # Check if the download was successful
        self.assertTrue(result)
        
        # Check if the file was created
        self.assertTrue(os.path.exists(output_path))
        
        # Check if the file has the correct content
        with open(output_path, 'rb') as file:
            content = file.read()
            self.assertEqual(content, b"Test content")
        
        # Check if requests.get was called with the correct arguments
        mock_get.assert_called_once_with(url, headers=headers, stream=True)

    @patch('src.utils.file_operations.requests.get')
    def test_download_file_failure(self, mock_get):
        """Test downloading a file with an error."""
        # Mock response with error
        mock_get.side_effect = Exception("Test error")
        
        # Download a file
        url = "https://example.com/file.pdf"
        output_path = os.path.join(self.temp_dir.name, "downloaded_file.pdf")
        
        result = download_file(url, output_path)
        
        # Check if the download failed
        self.assertFalse(result)
        
        # Check if the file was not created
        self.assertFalse(os.path.exists(output_path))

    @patch('src.utils.file_operations.requests.get')
    def test_download_file_response_error(self, mock_get):
        """Test downloading a file with a response error."""
        # Mock response with error during raise_for_status
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("Response error")
        mock_response.__enter__.return_value = mock_response
        mock_get.return_value = mock_response
        
        # Download a file
        url = "https://example.com/file.pdf"
        output_path = os.path.join(self.temp_dir.name, "downloaded_file.pdf")
        
        result = download_file(url, output_path)
        
        # Check if the download failed
        self.assertFalse(result)

    def test_save_html_to_file_real(self):
        """Test saving HTML content to a real file."""
        # Use a real file in the temp directory
        filename = os.path.join(self.temp_dir.name, "test.html")
        html_content = "<html><body>Test</body></html>"
        
        # Save the HTML content
        output_path = save_html_to_file(html_content, filename)
        
        # Check if the file exists
        self.assertTrue(os.path.exists(filename))
        
        # Check if the file contains the correct content
        with open(filename, 'r', encoding='utf-8') as file:
            content = file.read()
            self.assertEqual(content, html_content)

    def test_save_html_to_file_mock(self):
        """Test saving HTML content to a file with mocking."""
        # Save HTML content
        html_content = "<html><body>Test</body></html>"
        filename = "test.html"
        
        with patch('src.utils.file_operations.open', mock_open()) as mock_file:
            with patch('src.utils.file_operations.os.makedirs') as mock_makedirs:
                output_path = save_html_to_file(html_content, filename)
                
                # Check if the directory was created
                mock_makedirs.assert_called_once()
                
                # Check if the file was written to
                mock_file.assert_called_once()
                mock_file().write.assert_called_once_with(html_content)
                
                # Check if the output path is correct
                self.assertIn(filename, output_path)

    def test_generate_fdd_filename_simple(self):
        """Test generating a filename with simple input."""
        # Generate a filename
        file_id = "123456"
        franchise_name = "Test Franchise"
        effective_year = "2022"
        
        filename = generate_fdd_filename(file_id, franchise_name, effective_year)
        
        # Check if the filename has the correct format
        self.assertEqual(filename, "123456_Test_Franchise_2022.pdf")

    def test_generate_fdd_filename_special_chars(self):
        """Test generating a filename with special characters."""
        # Test with special characters
        file_id = "123456"
        franchise_name = "Test & Franchise, Inc."
        effective_year = "2022"
        
        filename = generate_fdd_filename(file_id, franchise_name, effective_year)
        
        # Check if special characters are properly handled
        self.assertEqual(filename, "123456_Test___Franchise__Inc__2022.pdf")

    def test_generate_fdd_filename_whitespace(self):
        """Test generating a filename with extra whitespace."""
        # Test with extra whitespace
        file_id = "123456"
        franchise_name = "  Test   Franchise  "
        effective_year = "2022"
        
        filename = generate_fdd_filename(file_id, franchise_name, effective_year)
        
        # Check if whitespace is properly handled
        self.assertEqual(filename, "123456_Test___Franchise_2022.pdf")

    @patch('src.utils.file_operations.FDD_DIR', Path('/test/fdds'))
    def test_create_fdd_filepath(self):
        """Test creating the full path for an FDD file."""
        # Create a filepath
        filename = "123456_Test_Franchise_2022.pdf"
        
        filepath = create_fdd_filepath(filename)
        
        # Check if the filepath is correct
        self.assertEqual(filepath, "/test/fdds/123456_Test_Franchise_2022.pdf")

    def test_get_file_size_existing(self):
        """Test getting the size of an existing file."""
        # Get the size of the test file
        file_size = get_file_size(self.temp_file.name)
        
        # Check if the file size is correct
        self.assertEqual(file_size, 12)  # "Test content" is 12 bytes

    def test_get_file_size_nonexistent(self):
        """Test getting the size of a non-existent file."""
        # Test with a non-existent file
        file_size = get_file_size("/non/existent/file")
        
        # Check if None is returned for a non-existent file
        self.assertIsNone(file_size)

    @patch('src.utils.file_operations.datetime')
    def test_get_current_date_string(self, mock_datetime):
        """Test getting the current date as a string."""
        # Mock datetime.now()
        mock_datetime.now.return_value = datetime.datetime(2022, 1, 1)
        
        # Get the current date string
        date_string = get_current_date_string()
        
        # Check if the date string is correct
        self.assertEqual(date_string, "2022-01-01")


if __name__ == '__main__':
    unittest.main() 