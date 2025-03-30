import os
import unittest
import tempfile
from unittest.mock import patch, MagicMock
import io

from src.utils.pdf_utils import get_pdf_page_count
from tests.utils import temp_file


class TestPdfUtils(unittest.TestCase):
    """Test cases for PDF utility functions."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for test files
        self.temp_dir = tempfile.TemporaryDirectory()
        
        # Path for a test PDF file
        self.test_pdf_path = os.path.join(self.temp_dir.name, "test.pdf")
        
        # Create a dummy PDF file
        with open(self.test_pdf_path, 'wb') as f:
            f.write(b"%PDF-1.4\n%Test PDF file")

    def tearDown(self):
        """Clean up test environment."""
        self.temp_dir.cleanup()

    @patch('src.utils.pdf_utils.PyPDF2.PdfReader')
    def test_get_pdf_page_count(self, mock_pdf_reader):
        """Test getting the number of pages in a PDF file."""
        # Create a mock PDF reader
        mock_reader = MagicMock()
        mock_reader.pages = [1, 2, 3]  # 3 pages
        mock_pdf_reader.return_value = mock_reader
        
        # Get the page count
        page_count = get_pdf_page_count(self.test_pdf_path)
        
        # Check if the page count is correct
        self.assertEqual(page_count, 3)
        
        # Check if PyPDF2.PdfReader was called with the correct arguments
        mock_pdf_reader.assert_called_once()
        
        # Verify file was opened in binary mode
        args, kwargs = mock_pdf_reader.call_args
        self.assertIsNotNone(args[0])

    @patch('src.utils.pdf_utils.PyPDF2.PdfReader')
    def test_get_pdf_page_count_error(self, mock_pdf_reader):
        """Test error handling when getting the page count."""
        # Make PyPDF2.PdfReader raise an exception
        mock_pdf_reader.side_effect = Exception("Test error")
        
        # Get the page count
        page_count = get_pdf_page_count(self.test_pdf_path)
        
        # Check if None is returned on error
        self.assertIsNone(page_count)

    def test_get_pdf_page_count_file_not_found(self):
        """Test getting the page count for a file that doesn't exist."""
        # Get the page count for a non-existent file
        page_count = get_pdf_page_count("/non/existent/file.pdf")
        
        # Check if None is returned when the file doesn't exist
        self.assertIsNone(page_count)

    @patch('src.utils.pdf_utils.open')
    def test_get_pdf_page_count_io_error(self, mock_open):
        """Test handling of I/O errors when reading a PDF file."""
        # Make open raise an I/O error
        mock_open.side_effect = IOError("Test I/O error")
        
        # Get the page count
        page_count = get_pdf_page_count(self.test_pdf_path)
        
        # Check if None is returned on I/O error
        self.assertIsNone(page_count)


if __name__ == '__main__':
    unittest.main() 