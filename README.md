# FDD WebScrape

A web scraping tool that extracts franchise disclosure documents (FDDs) and related metadata from the Wisconsin Department of Financial Institutions website.

## Overview

This tool automatically:
1. Extracts active franchise filings
2. Retrieves detailed metadata for each franchise
3. Downloads franchise disclosure documents (FDDs)
4. Stores all data in a structured SQLite database

## Requirements

- Python 3.9+
- Dependencies listed in requirements.txt

## Installation

```bash
# Clone the repository
git clone [repository-url]
cd FDD_WebScrape

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
python -m src.main
```

## Project Structure

```
FDD_WebScrape/
├── data/                  # Data directory
│   └── fdds/              # FDD files directory
├── src/                   # Source code
├── tests/                 # Test files
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

## License

See the LICENSE file for details.