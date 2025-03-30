import unittest
import asyncio
from unittest.mock import patch, MagicMock
import pandas as pd

from src.scrapers.active_filings import ActiveFilingsScraper, scrape_active_filings


class TestActiveFilingsScraper(unittest.TestCase):
    """Test cases for the ActiveFilingsScraper class."""

    def setUp(self):
        """Set up test environment."""
        # Sample HTML content with a table
        self.sample_html = '''
        <html>
            <body>
                <table id="dgActiveFilings">
                    <tr>
                        <th>Franchise Name</th>
                        <th>Expiration Date</th>
                    </tr>
                    <tr>
                        <td>Test Franchise 1</td>
                        <td>12/31/2023</td>
                    </tr>
                    <tr>
                        <td>Test Franchise 2</td>
                        <td>12/31/2023</td>
                    </tr>
                </table>
            </body>
        </html>
        '''

    @patch('src.scrapers.active_filings.launch')
    @patch('src.scrapers.active_filings.save_html_to_file')
    @patch('src.scrapers.active_filings.pd.read_html')
    def test_get_active_filings(self, mock_read_html, mock_save_html, mock_launch):
        """Test getting active filings."""
        # Set up mocks
        mock_browser = MagicMock()
        mock_page = MagicMock()
        mock_browser.newPage.return_value = asyncio.Future()
        mock_browser.newPage.return_value.set_result(mock_page)
        
        mock_page.goto = MagicMock(return_value=asyncio.Future())
        mock_page.goto.return_value.set_result(None)
        
        mock_page.content = MagicMock(return_value=asyncio.Future())
        mock_page.content.return_value.set_result(self.sample_html)
        
        mock_page.setDefaultNavigationTimeout = MagicMock(return_value=asyncio.Future())
        mock_page.setDefaultNavigationTimeout.return_value.set_result(None)
        
        mock_launch.return_value = asyncio.Future()
        mock_launch.return_value.set_result(mock_browser)
        
        mock_save_html.return_value = "/path/to/html"
        
        # Mock pandas.read_html
        mock_df = pd.DataFrame({
            'Franchise Name': ['Test Franchise 1', 'Test Franchise 2'],
            'Expiration Date': ['12/31/2023', '12/31/2023']
        })
        mock_read_html.return_value = [mock_df]
        
        # Create a scraper
        scraper = ActiveFilingsScraper()
        
        # Run the scraper
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        filings, html_path = loop.run_until_complete(scraper.get_active_filings())
        loop.close()
        
        # Check if the filings were extracted correctly
        self.assertEqual(len(filings), 2)
        self.assertEqual(filings[0]['franchise_name'], 'Test Franchise 1')
        self.assertEqual(filings[0]['expiration_date'], '12/31/2023')
        self.assertEqual(filings[0]['active_state'], 'wisconsin')
        self.assertEqual(filings[1]['franchise_name'], 'Test Franchise 2')
        self.assertEqual(filings[1]['expiration_date'], '12/31/2023')
        self.assertEqual(filings[1]['active_state'], 'wisconsin')
        
        # Check if the HTML was saved
        self.assertEqual(html_path, "/path/to/html")
        
        # Check if the browser was launched and closed
        mock_launch.assert_called_once()
        mock_browser.close.assert_not_called()  # We don't close in get_active_filings, only in scrape()

    @patch('src.scrapers.active_filings.launch')
    @patch('src.scrapers.active_filings.save_html_to_file')
    def test_get_active_filings_no_table(self, mock_save_html, mock_launch):
        """Test getting active filings when the table is not found."""
        # Set up mocks
        mock_browser = MagicMock()
        mock_page = MagicMock()
        mock_browser.newPage.return_value = asyncio.Future()
        mock_browser.newPage.return_value.set_result(mock_page)
        
        mock_page.goto = MagicMock(return_value=asyncio.Future())
        mock_page.goto.return_value.set_result(None)
        
        # HTML without the table
        html_without_table = '<html><body>No table here</body></html>'
        mock_page.content = MagicMock(return_value=asyncio.Future())
        mock_page.content.return_value.set_result(html_without_table)
        
        mock_page.setDefaultNavigationTimeout = MagicMock(return_value=asyncio.Future())
        mock_page.setDefaultNavigationTimeout.return_value.set_result(None)
        
        mock_launch.return_value = asyncio.Future()
        mock_launch.return_value.set_result(mock_browser)
        
        mock_save_html.return_value = "/path/to/html"
        
        # Create a scraper
        scraper = ActiveFilingsScraper()
        
        # Run the scraper
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        filings, html_path = loop.run_until_complete(scraper.get_active_filings())
        loop.close()
        
        # Check if an empty list was returned
        self.assertEqual(len(filings), 0)
        
        # Check if the HTML was saved
        self.assertEqual(html_path, "/path/to/html")

    @patch('src.scrapers.active_filings.ActiveFilingsScraper')
    def test_scrape_active_filings(self, mock_scraper_class):
        """Test the scrape_active_filings function."""
        # Set up mocks
        mock_scraper = MagicMock()
        mock_scraper.scrape = MagicMock(return_value=asyncio.Future())
        mock_scraper.scrape.return_value.set_result((['filing1', 'filing2'], '/path/to/html'))
        
        mock_scraper_class.return_value = mock_scraper
        
        # Run the function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        filings, html_path = loop.run_until_complete(scrape_active_filings())
        loop.close()
        
        # Check if the filings were returned correctly
        self.assertEqual(filings, ['filing1', 'filing2'])
        self.assertEqual(html_path, '/path/to/html')
        
        # Check if the scraper was created and used
        mock_scraper_class.assert_called_once()
        mock_scraper.scrape.assert_called_once()

    @patch('src.scrapers.active_filings.launch')
    def test_scraper_close(self, mock_launch):
        """Test that the scraper closes the browser."""
        # Set up mocks
        mock_browser = MagicMock()
        mock_browser.close = MagicMock(return_value=asyncio.Future())
        mock_browser.close.return_value.set_result(None)
        
        mock_launch.return_value = asyncio.Future()
        mock_launch.return_value.set_result(mock_browser)
        
        # Create a scraper
        scraper = ActiveFilingsScraper()
        scraper.browser = mock_browser
        
        # Run the close method
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(scraper.close())
        loop.close()
        
        # Check if the browser was closed
        mock_browser.close.assert_called_once()
        self.assertIsNone(scraper.browser)
        self.assertIsNone(scraper.page)


if __name__ == '__main__':
    unittest.main() 