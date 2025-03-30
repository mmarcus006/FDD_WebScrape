import asyncio
import os
import sys
from typing import List, Dict, Any, Optional
import datetime

from src.config import DB_PATH
from src.db.database import Database
from src.scrapers.active_filings import scrape_active_filings
from src.scrapers.franchise_data import scrape_franchise_data
from src.scrapers.fdd_downloader import download_fdd


async def process_active_filings() -> List[Dict[str, Any]]:
    """Scrape and store active filings.
    
    Returns:
        list: List of active filings
    """
    print("Scraping active filings...")
    filings, html_path = await scrape_active_filings()
    print(f"Found {len(filings)} active filings. HTML saved to {html_path}")
    
    # Store active filings in the database
    with Database(DB_PATH) as db:
        db.initialize_database()
        
        # Insert each filing
        for filing in filings:
            db.insert_active_filing(
                franchise_name=filing['franchise_name'],
                expiration_date=filing['expiration_date'],
                active_state=filing['active_state']
            )
        
        # Return all active filings with IDs
        return db.get_all_active_filings()


async def process_franchise_data(active_filings: List[Dict[str, Any]]) -> Dict[int, List[Dict[str, Any]]]:
    """Process franchise data for each active filing.
    
    Args:
        active_filings (list): List of active filings
        
    Returns:
        dict: Dictionary mapping active filing IDs to franchise metadata
    """
    results = {}
    
    with Database(DB_PATH) as db:
        for filing in active_filings:
            franchise_name = filing['franchise_name']
            active_filing_id = filing['id']
            
            print(f"Processing franchise: {franchise_name}")
            franchise_data = await scrape_franchise_data(franchise_name)
            
            if not franchise_data:
                print(f"No data found for franchise: {franchise_name}")
                continue
            
            # Store franchise metadata in the database
            franchise_metadata_ids = []
            for data in franchise_data:
                # Insert franchise metadata
                metadata_id = db.insert_franchise_metadata(
                    active_filing_id=active_filing_id,
                    file_number=data['file_number'],
                    legal_name=data['legal_name'],
                    effective_date=data['effective_date'],
                    expiration_date=data['expiration_date'],
                    status=data['status'],
                    address_line1=data.get('address_line1'),
                    address_line2=data.get('address_line2'),
                    city=data.get('city'),
                    state=data.get('state'),
                    zip_code=data.get('zip'),
                    wi_webpage_url=data.get('wi_webpage_url')
                )
                data['metadata_id'] = metadata_id
                franchise_metadata_ids.append(metadata_id)
            
            # Store the results
            results[active_filing_id] = franchise_data
    
    return results


def process_fdd_downloads(franchise_data_by_filing: Dict[int, List[Dict[str, Any]]]):
    """Download and process FDD documents.
    
    Args:
        franchise_data_by_filing (dict): Dictionary mapping active filing IDs to franchise metadata
    """
    with Database(DB_PATH) as db:
        for active_filing_id, franchise_data_list in franchise_data_by_filing.items():
            for franchise_data in franchise_data_list:
                franchise_name = franchise_data.get('trade_name', 'Unknown')
                fdd_url = franchise_data.get('fdd_url')
                metadata_id = franchise_data.get('metadata_id')
                
                if not fdd_url or not metadata_id:
                    print(f"Missing URL or metadata ID for franchise: {franchise_name}")
                    continue
                
                print(f"Downloading FDD for franchise: {franchise_name}")
                fdd_metadata = download_fdd(fdd_url, franchise_data)
                
                if not fdd_metadata:
                    print(f"Failed to download FDD for franchise: {franchise_name}")
                    continue
                
                # Insert FDD metadata
                db.insert_fdd_metadata(
                    franchise_metadata_id=metadata_id,
                    fdd_url=fdd_metadata['fdd_url'],
                    fdd_file_name=fdd_metadata['fdd_file_name'],
                    fdd_file_path=fdd_metadata['fdd_file_path'],
                    fdd_file_size=fdd_metadata['fdd_file_size'],
                    fdd_file_download_date=fdd_metadata['fdd_file_download_date'],
                    num_pages=fdd_metadata['num_pages']
                )
                
                print(f"Successfully processed FDD for franchise: {franchise_name}")
                
                # Sleep to avoid overloading the server
                import time
                time.sleep(2)


async def main():
    """Main application entry point."""
    try:
        print("Starting FDD WebScrape...")
        
        # Step 1: Process active filings
        active_filings = await process_active_filings()
        
        # Step 2: Process franchise data
        franchise_data_by_filing = await process_franchise_data(active_filings)
        
        # Step 3: Download and process FDD documents
        process_fdd_downloads(franchise_data_by_filing)
        
        print("FDD WebScrape completed successfully!")
    
    except Exception as e:
        print(f"Error running the application: {e}")
        sys.exit(1)


def main_entry():
    """Entry point for console script."""
    # Create event loop
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    finally:
        loop.close()


if __name__ == "__main__":
    main_entry() 