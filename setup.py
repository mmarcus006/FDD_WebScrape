from setuptools import setup, find_packages

setup(
    name="fdd_webscrape",
    version="0.1.0",
    description="Web scraping tool for franchise disclosure documents",
    author="FDD WebScrape Team",
    packages=find_packages(),
    install_requires=[
        "playwright>=1.41.2",
        "beautifulsoup4>=4.12.2",
        "requests>=2.31.0",
        "pyppeteer>=1.0.2",
        "pandas>=2.1.4",
        "sqlalchemy>=2.0.25",
        "pypdf2>=3.0.1",
        "python-dateutil>=2.8.2",
    ],
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "fdd-webscrape=src.main:main_entry",
        ],
    },
) 