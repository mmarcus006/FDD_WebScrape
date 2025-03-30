import os
import sqlite3
from pathlib import Path


class Database:
    """SQLite database connection manager for franchise data."""

    def __init__(self, db_path="franchise_data.db"):
        """Initialize database connection.

        Args:
            db_path (str): Path to the SQLite database file
        """
        self.db_path = db_path
        self.connection = None
        self.cursor = None

    def connect(self):
        """Create a connection to the database."""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()
        return self.connection

    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
            self.cursor = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            if exc_type:
                self.connection.rollback()
            else:
                self.connection.commit()
            self.close()

    def initialize_database(self):
        """Create database tables if they don't exist."""
        self.connect()
        
        # Create Active Filings table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS active_filings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            franchise_name TEXT NOT NULL,
            expiration_date TEXT NOT NULL,
            active_state TEXT NOT NULL DEFAULT 'wisconsin'
        )
        ''')
        
        # Create Franchise Metadata table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS franchise_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            active_filing_id INTEGER NOT NULL,
            file_number TEXT NOT NULL,
            legal_name TEXT NOT NULL,
            effective_date TEXT NOT NULL,
            expiration_date TEXT NOT NULL,
            status TEXT NOT NULL,
            address_line1 TEXT,
            address_line2 TEXT,
            city TEXT,
            state TEXT,
            zip TEXT,
            wi_webpage_url TEXT,
            FOREIGN KEY (active_filing_id) REFERENCES active_filings (id)
        )
        ''')
        
        # Create FDD Metadata table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS fdd_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            franchise_metadata_id INTEGER NOT NULL,
            fdd_url TEXT NOT NULL,
            fdd_file_name TEXT NOT NULL,
            fdd_file_path TEXT NOT NULL,
            fdd_file_size INTEGER,
            fdd_file_download_date TEXT,
            num_pages INTEGER,
            FOREIGN KEY (franchise_metadata_id) REFERENCES franchise_metadata (id)
        )
        ''')
        
        self.connection.commit()

    def insert_active_filing(self, franchise_name, expiration_date, active_state="wisconsin"):
        """Insert a new active filing record.
        
        Args:
            franchise_name (str): Name of the franchise
            expiration_date (str): Expiration date of the filing
            active_state (str): State where the filing is active
            
        Returns:
            int: The ID of the inserted record
        """
        query = '''
        INSERT INTO active_filings (franchise_name, expiration_date, active_state)
        VALUES (?, ?, ?)
        '''
        self.cursor.execute(query, (franchise_name, expiration_date, active_state))
        self.connection.commit()
        return self.cursor.lastrowid

    def insert_franchise_metadata(self, active_filing_id, file_number, legal_name, 
                                effective_date, expiration_date, status, 
                                address_line1=None, address_line2=None, 
                                city=None, state=None, zip_code=None, 
                                wi_webpage_url=None):
        """Insert franchise metadata.
        
        Args:
            active_filing_id (int): Foreign key to active_filings table
            file_number (str): File number of the franchise
            legal_name (str): Legal name of the franchise
            effective_date (str): Effective date of the filing
            expiration_date (str): Expiration date of the filing
            status (str): Status of the filing
            address_line1 (str, optional): Address line 1
            address_line2 (str, optional): Address line 2
            city (str, optional): City
            state (str, optional): State
            zip_code (str, optional): ZIP code
            wi_webpage_url (str, optional): Wisconsin webpage URL
            
        Returns:
            int: The ID of the inserted record
        """
        query = '''
        INSERT INTO franchise_metadata (
            active_filing_id, file_number, legal_name, effective_date, 
            expiration_date, status, address_line1, address_line2, 
            city, state, zip, wi_webpage_url
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        self.cursor.execute(query, (
            active_filing_id, file_number, legal_name, effective_date, 
            expiration_date, status, address_line1, address_line2, 
            city, state, zip_code, wi_webpage_url
        ))
        self.connection.commit()
        return self.cursor.lastrowid

    def insert_fdd_metadata(self, franchise_metadata_id, fdd_url, fdd_file_name,
                          fdd_file_path, fdd_file_size=None, 
                          fdd_file_download_date=None, num_pages=None):
        """Insert FDD metadata.
        
        Args:
            franchise_metadata_id (int): Foreign key to franchise_metadata table
            fdd_url (str): URL of the FDD document
            fdd_file_name (str): File name of the FDD document
            fdd_file_path (str): File path of the FDD document
            fdd_file_size (int, optional): File size of the FDD document
            fdd_file_download_date (str, optional): Download date of the FDD document
            num_pages (int, optional): Number of pages in the FDD document
            
        Returns:
            int: The ID of the inserted record
        """
        query = '''
        INSERT INTO fdd_metadata (
            franchise_metadata_id, fdd_url, fdd_file_name, fdd_file_path,
            fdd_file_size, fdd_file_download_date, num_pages
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        '''
        self.cursor.execute(query, (
            franchise_metadata_id, fdd_url, fdd_file_name, fdd_file_path,
            fdd_file_size, fdd_file_download_date, num_pages
        ))
        self.connection.commit()
        return self.cursor.lastrowid
    
    def get_all_active_filings(self):
        """Get all active filings from the database.
        
        Returns:
            list: List of active filings
        """
        query = "SELECT * FROM active_filings"
        self.cursor.execute(query)
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_franchise_by_name(self, franchise_name):
        """Get franchise by name.
        
        Args:
            franchise_name (str): Name of the franchise
            
        Returns:
            dict: Franchise data or None if not found
        """
        query = "SELECT * FROM active_filings WHERE franchise_name = ?"
        self.cursor.execute(query, (franchise_name,))
        row = self.cursor.fetchone()
        return dict(row) if row else None 