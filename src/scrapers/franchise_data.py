import asyncio
from typing import List, Dict, Any, Optional, Tuple
import re
from pyppeteer import launch
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time

from src.config import (
    FRANCHISE_SEARCH_URL, 
    FRANCHISE_DETAILS_BASE_URL,
    HEADLESS, 
    TIMEOUT, 
    DEFAULT_NAVIGATION_TIMEOUT
)
from src.utils.file_operations import save_html_to_file


class FranchiseDataScraper:
    """Scraper for detailed franchise metadata."""

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

    async def search_franchise(self, franchise_name: str) -> Optional[List[Dict[str, Any]]]:
        """Search for a franchise by name.
        
        Args:
            franchise_name (str): Name of the franchise to search for
            
        Returns:
            list: List of search results or None if an error occurs
        """
        try:
            if not self.page:
                await self.initialize()

            # Navigate to the search page
            await self.page.goto(FRANCHISE_SEARCH_URL, {'timeout': TIMEOUT, 'waitUntil': 'networkidle0'})

            # Type the franchise name in the search box
            await self.page.type('input#txtName', franchise_name)
            
            # Wait for 1 second
            await asyncio.sleep(1)
            
            # Click on the input element again
            await self.page.click('input#txtName')
            
            # Send tab and enter keys
            await self.page.keyboard.press('Tab')
            await self.page.keyboard.press('Enter')
            
            # Wait for the results page to load
            await self.page.waitForNavigation({'timeout': TIMEOUT, 'waitUntil': 'networkidle0'})
            
            # Get the page content
            content = await self.page.content()
            
            # Save the search results to a file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            save_html_to_file(content, f"search_results_{franchise_name.replace(' ', '_')}_{timestamp}.html")
            
            # Parse the search results
            soup = BeautifulSoup(content, 'html.parser')
            
            # Find the results table
            results_table = soup.find('table', {'id': 'grdSearchResults'})
            
            if not results_table:
                print(f"No results found for franchise: {franchise_name}")
                return None
            
            # Convert table to DataFrame
            results_df = pd.read_html(str(results_table))[0]
            
            # Get the "Details" links for registered franchises
            links = []
            for row in results_table.find_all('tr'):
                tds = row.find_all('td')
                if len(tds) > 6 and tds[5].text.strip() == 'Registered':
                    link = tds[6].find('a')
                    if link and 'href' in link.attrs:
                        href = link['href']
                        # Extract ID and hash from the href
                        match = re.search(r'id=(\d+)&hash=(\d+)', href)
                        if match:
                            file_id = match.group(1)
                            hash_value = match.group(2)
                            links.append({
                                'details_url': f"{FRANCHISE_DETAILS_BASE_URL}?id={file_id}&hash={hash_value}&search=external&type=GENERAL",
                                'file_id': file_id,
                                'hash': hash_value
                            })
            
            # Combine DataFrame and links
            results = []
            for i, row in results_df.iterrows():
                if row['Status'] == 'Registered':
                    # Find the corresponding link
                    for link in links:
                        if str(row['File Number']) == link['file_id']:
                            # Create a single result dictionary
                            result = {
                                'file_number': str(row['File Number']),
                                'legal_name': row['Legal Name'],
                                'trade_name': row['Trade Name'],
                                'effective_date': row['Effective Date'],
                                'expiration_date': row['Expiration Date'],
                                'status': row['Status'],
                                'details_url': link['details_url'],
                                'file_id': link['file_id'],
                                'hash': link['hash']
                            }
                            results.append(result)
            
            return results
        
        except Exception as e:
            print(f"Error searching for franchise {franchise_name}: {e}")
            return None

    async def get_franchise_details(self, details_url: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a franchise.
        
        Args:
            details_url (str): URL of the franchise details page
            
        Returns:
            dict: Franchise details or None if an error occurs
        """
        try:
            if not self.page:
                await self.initialize()
            
            # Navigate to the details page
            await self.page.goto(details_url, {'timeout': TIMEOUT, 'waitUntil': 'networkidle0'})
            
            # Get the page content
            content = await self.page.content()
            
            # Save the details page to a file
            file_id = re.search(r'id=(\d+)', details_url).group(1)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            save_html_to_file(content, f"franchise_details_{file_id}_{timestamp}.html")
            
            # Parse the details page
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extract address information
            address = {}
            try:
                address['address_line1'] = soup.find('span', {'id': 'lblFranchiseAddressLine1'}).text.strip()
                
                address_line2_element = soup.find('span', {'id': 'lblFranchiseAddressLine2'})
                if address_line2_element and address_line2_element.text.strip():
                    address['address_line2'] = address_line2_element.text.strip()
                else:
                    address['address_line2'] = None
                
                address['city'] = soup.find('span', {'id': 'lblFranchiseCity'}).text.strip()
                address['state'] = soup.find('span', {'id': 'lblFranchiseState'}).text.strip()
                address['zip'] = soup.find('span', {'id': 'lblFranchiseZip'}).text.strip()
            except (AttributeError, ValueError) as e:
                print(f"Error extracting address information: {e}")
            
            # The URL for the FDD download is the current details URL
            fdd_url = details_url
            
            return {
                'address': address,
                'wi_webpage_url': details_url,
                'fdd_url': fdd_url
            }
        
        except Exception as e:
            print(f"Error getting franchise details: {e}")
            return None

    async def scrape_franchise(self, franchise_name: str) -> Optional[List[Dict[str, Any]]]:
        """Scrape data for a specific franchise.
        
        Args:
            franchise_name (str): Name of the franchise to scrape
            
        Returns:
            list: List of franchise data or None if an error occurs
        """
        try:
            # Search for the franchise
            search_results = await self.search_franchise(franchise_name)
            
            if not search_results:
                print(f"No registered results found for franchise: {franchise_name}")
                return None
            
            # Get details for each registered franchise
            full_results = []
            for result in search_results:
                details = await self.get_franchise_details(result['details_url'])
                if details:
                    # Combine search results and details
                    combined = {**result}
                    
                    if 'address' in details:
                        combined['address_line1'] = details['address'].get('address_line1')
                        combined['address_line2'] = details['address'].get('address_line2')
                        combined['city'] = details['address'].get('city')
                        combined['state'] = details['address'].get('state')
                        combined['zip'] = details['address'].get('zip')
                    
                    combined['wi_webpage_url'] = details.get('wi_webpage_url')
                    combined['fdd_url'] = details.get('fdd_url')
                    
                    full_results.append(combined)
            
            return full_results
        
        except Exception as e:
            print(f"Error scraping franchise {franchise_name}: {e}")
            return None
        
    async def scrape(self, franchise_name: str) -> Optional[List[Dict[str, Any]]]:
        """Main scrape method.
        
        Args:
            franchise_name (str): Name of the franchise to scrape
            
        Returns:
            list: List of franchise data or None if an error occurs
        """
        try:
            return await self.scrape_franchise(franchise_name)
        finally:
            await self.close()


# Function to run the scraper
async def scrape_franchise_data(franchise_name: str) -> Optional[List[Dict[str, Any]]]:
    """Scrape data for a specific franchise.
    
    Args:
        franchise_name (str): Name of the franchise to scrape
        
    Returns:
        list: List of franchise data or None if an error occurs
    """
    scraper = FranchiseDataScraper()
    return await scraper.scrape(franchise_name) 