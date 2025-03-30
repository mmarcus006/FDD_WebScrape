import os
from pathlib import Path

# Project root directory
ROOT_DIR = Path(__file__).parent.parent

# Data directories
DATA_DIR = ROOT_DIR / "data"
FDD_DIR = DATA_DIR / "fdds"

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(FDD_DIR, exist_ok=True)

# Database settings
DB_PATH = ROOT_DIR / "franchise_data.db"

# Website URLs
ACTIVE_FILINGS_URL = "https://apps.dfi.wi.gov/apps/FranchiseEFiling/activeFilings.aspx"
FRANCHISE_SEARCH_URL = "https://apps.dfi.wi.gov/apps/FranchiseSearch/MainSearch.aspx"
FRANCHISE_DETAILS_BASE_URL = "https://apps.dfi.wi.gov/apps/FranchiseSearch/details.aspx"

# Puppeteer/Scraping settings
HEADLESS = True  # Run browser in headless mode
TIMEOUT = 30000  # Timeout in milliseconds
DEFAULT_NAVIGATION_TIMEOUT = 60000  # Navigation timeout in milliseconds

# User agent string for HTTP requests
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36" 