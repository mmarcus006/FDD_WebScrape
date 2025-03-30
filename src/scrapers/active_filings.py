import asyncio
from typing import List, Dict, Any, Optional
from pyppeteer import launch
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

from src.config import ACTIVE_FILINGS_URL, HEADLESS, TIMEOUT, DEFAULT_NAVIGATION_TIMEOUT
from src.utils.file_operations import save_html_to_file


class ActiveFilingsScraper:
    """Scraper for active franchise filings."""

    def __init__(self, headless: bool = HEADLESS):
        """Initialize the scraper.
        
        Args:
            headless (bool): Whether to run the browser in headless mode
        """
        self.headless = headless
        self.browser = None
        self.page = None

    async def initialize(self):
        """Initialize the browser and page."""
        self.browser = await launch(headless=self.headless)
        self.page = await self.browser.newPage()
        await self.page.setDefaultNavigationTimeout(DEFAULT_NAVIGATION_TIMEOUT)

    async def close(self):
        """Close the browser."""
        if self.browser:
            await self.browser.close()
            self.browser = None
            self.page = None

    async def get_active_filings(self) -> tuple[List[Dict[str, Any]], Optional[str]]:
        """Scrape active filings from the website.
        
        Returns:
            tuple: List of active filings and the path to the saved HTML file
        """
        if not self.page:
            await self.initialize()

        # Navigate to the active filings page
        await self.page.goto(ACTIVE_FILINGS_URL, {'timeout': TIMEOUT, 'waitUntil': 'networkidle0'})

        # Get the page content
        content = await self.page.content()

        # Save the HTML content to a file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        html_path = save_html_to_file(content, f"active_filings_{timestamp}.html")

        # Parse the HTML content to extract active filings
        soup = BeautifulSoup(content, 'html.parser')
        
        # Find the table containing active filings
        filings_table = soup.find('table', {'id': 'dgActiveFilings'})
        
        if not filings_table:
            print("Could not find active filings table")
            return [], html_path

        # Convert HTML table to a DataFrame
        filings_df = pd.read_html(str(filings_table))[0]
        
        # Convert DataFrame to list of dictionaries
        filings = filings_df.to_dict('records')
        
        # Rename columns to match our database schema
        for filing in filings:
            filing['franchise_name'] = filing.pop('Franchise Name')
            filing['expiration_date'] = filing.pop('Expiration Date')
            filing['active_state'] = 'wisconsin'
        
        return filings, html_path

    async def scrape(self) -> tuple[List[Dict[str, Any]], Optional[str]]:
        """Main scrape method.
        
        Returns:
            tuple: List of active filings and the path to the saved HTML file
        """
        try:
            filings, html_path = await self.get_active_filings()
            return filings, html_path
        finally:
            await self.close()


# Function to run the scraper
async def scrape_active_filings() -> tuple[List[Dict[str, Any]], Optional[str]]:
    """Scrape active filings from the website.
    
    Returns:
        tuple: List of active filings and the path to the saved HTML file
    """
    scraper = ActiveFilingsScraper()
    return await scraper.scrape() 