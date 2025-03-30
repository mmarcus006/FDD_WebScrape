import os
import unittest
import sqlite3
import tempfile

from src.db.database import Database


class TestDatabase(unittest.TestCase):
    """Test cases for the Database class."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary file for the test database
        self.temp_db_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_db_file.close()
        self.db = Database(self.temp_db_file.name)
        self.db.connect()
        self.db.initialize_database()

    def tearDown(self):
        """Clean up test environment."""
        self.db.close()
        if os.path.exists(self.temp_db_file.name):
            os.unlink(self.temp_db_file.name)

    def test_connection(self):
        """Test database connection."""
        self.assertIsNotNone(self.db.connection)
        self.assertIsNotNone(self.db.cursor)

    def test_context_manager(self):
        """Test using the database as a context manager."""
        # Close the existing connection first
        self.db.close()
        
        # Use the database as a context manager
        with Database(self.temp_db_file.name) as db:
            self.assertIsNotNone(db.connection)
            self.assertIsNotNone(db.cursor)
            
            # Execute a query
            db.cursor.execute("SELECT 1")
            result = db.cursor.fetchone()
            self.assertEqual(result[0], 1)
        
        # Check if the connection was closed
        self.assertIsNone(self.db.connection)
        self.assertIsNone(self.db.cursor)
    
    def test_context_manager_with_exception(self):
        """Test context manager handling exceptions."""
        # Close the existing connection first
        self.db.close()
        
        try:
            with Database(self.temp_db_file.name) as db:
                self.assertIsNotNone(db.connection)
                # Raise an exception to test rollback
                raise ValueError("Test exception")
        except ValueError:
            pass  # Expected exception
        
        # Check if the connection was closed
        self.assertIsNone(self.db.connection)
        self.assertIsNone(self.db.cursor)

    def test_initialize_database(self):
        """Test database initialization."""
        # Check if tables exist
        self.db.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in self.db.cursor.fetchall()]
        
        # Check if all required tables exist
        self.assertIn('active_filings', tables)
        self.assertIn('franchise_metadata', tables)
        self.assertIn('fdd_metadata', tables)

    def test_insert_active_filing(self):
        """Test inserting an active filing."""
        franchise_name = "Test Franchise"
        expiration_date = "2023-12-31"
        active_state = "wisconsin"
        
        # Insert a filing
        filing_id = self.db.insert_active_filing(franchise_name, expiration_date, active_state)
        
        # Check if the filing was inserted
        self.assertIsNotNone(filing_id)
        self.db.cursor.execute("SELECT * FROM active_filings WHERE id = ?", (filing_id,))
        row = self.db.cursor.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row['franchise_name'], franchise_name)
        self.assertEqual(row['expiration_date'], expiration_date)
        self.assertEqual(row['active_state'], active_state)

    def test_insert_franchise_metadata(self):
        """Test inserting franchise metadata."""
        # Insert an active filing first
        filing_id = self.db.insert_active_filing("Test Franchise", "2023-12-31", "wisconsin")
        
        # Insert franchise metadata
        file_number = "123456"
        legal_name = "Test Legal Name"
        effective_date = "2022-01-01"
        expiration_date = "2023-12-31"
        status = "Registered"
        address_line1 = "123 Test St"
        address_line2 = "Suite 100"
        city = "Testville"
        state = "TS"
        zip_code = "12345"
        wi_webpage_url = "https://example.com"
        
        metadata_id = self.db.insert_franchise_metadata(
            filing_id, file_number, legal_name, effective_date, expiration_date,
            status, address_line1, address_line2, city, state, zip_code, wi_webpage_url
        )
        
        # Check if the metadata was inserted
        self.assertIsNotNone(metadata_id)
        self.db.cursor.execute("SELECT * FROM franchise_metadata WHERE id = ?", (metadata_id,))
        row = self.db.cursor.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row['active_filing_id'], filing_id)
        self.assertEqual(row['file_number'], file_number)
        self.assertEqual(row['legal_name'], legal_name)
        self.assertEqual(row['effective_date'], effective_date)
        self.assertEqual(row['expiration_date'], expiration_date)
        self.assertEqual(row['status'], status)
        self.assertEqual(row['address_line1'], address_line1)
        self.assertEqual(row['address_line2'], address_line2)
        self.assertEqual(row['city'], city)
        self.assertEqual(row['state'], state)
        self.assertEqual(row['zip'], zip_code)
        self.assertEqual(row['wi_webpage_url'], wi_webpage_url)

    def test_insert_franchise_metadata_minimal(self):
        """Test inserting franchise metadata with minimal information."""
        # Insert an active filing first
        filing_id = self.db.insert_active_filing("Test Franchise", "2023-12-31", "wisconsin")
        
        # Insert franchise metadata with minimal information
        file_number = "123456"
        legal_name = "Test Legal Name"
        effective_date = "2022-01-01"
        expiration_date = "2023-12-31"
        status = "Registered"
        
        metadata_id = self.db.insert_franchise_metadata(
            filing_id, file_number, legal_name, effective_date, expiration_date, status
        )
        
        # Check if the metadata was inserted
        self.assertIsNotNone(metadata_id)
        self.db.cursor.execute("SELECT * FROM franchise_metadata WHERE id = ?", (metadata_id,))
        row = self.db.cursor.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row['active_filing_id'], filing_id)
        self.assertEqual(row['file_number'], file_number)
        self.assertEqual(row['legal_name'], legal_name)
        self.assertEqual(row['effective_date'], effective_date)
        self.assertEqual(row['expiration_date'], expiration_date)
        self.assertEqual(row['status'], status)
        self.assertIsNone(row['address_line1'])
        self.assertIsNone(row['address_line2'])
        self.assertIsNone(row['city'])
        self.assertIsNone(row['state'])
        self.assertIsNone(row['zip'])
        self.assertIsNone(row['wi_webpage_url'])

    def test_insert_fdd_metadata(self):
        """Test inserting FDD metadata."""
        # Insert an active filing
        filing_id = self.db.insert_active_filing("Test Franchise", "2023-12-31", "wisconsin")
        
        # Insert franchise metadata
        metadata_id = self.db.insert_franchise_metadata(
            filing_id, "123456", "Test Legal Name", "2022-01-01", "2023-12-31",
            "Registered", "123 Test St", "Suite 100", "Testville", "TS", "12345", "https://example.com"
        )
        
        # Insert FDD metadata
        fdd_url = "https://example.com/fdd"
        fdd_file_name = "123456_Test_Franchise_2022.pdf"
        fdd_file_path = "/path/to/fdd/123456_Test_Franchise_2022.pdf"
        fdd_file_size = 1024
        fdd_file_download_date = "2022-01-01"
        num_pages = 100
        
        fdd_id = self.db.insert_fdd_metadata(
            metadata_id, fdd_url, fdd_file_name, fdd_file_path,
            fdd_file_size, fdd_file_download_date, num_pages
        )
        
        # Check if the FDD metadata was inserted
        self.assertIsNotNone(fdd_id)
        self.db.cursor.execute("SELECT * FROM fdd_metadata WHERE id = ?", (fdd_id,))
        row = self.db.cursor.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row['franchise_metadata_id'], metadata_id)
        self.assertEqual(row['fdd_url'], fdd_url)
        self.assertEqual(row['fdd_file_name'], fdd_file_name)
        self.assertEqual(row['fdd_file_path'], fdd_file_path)
        self.assertEqual(row['fdd_file_size'], fdd_file_size)
        self.assertEqual(row['fdd_file_download_date'], fdd_file_download_date)
        self.assertEqual(row['num_pages'], num_pages)

    def test_insert_fdd_metadata_minimal(self):
        """Test inserting FDD metadata with minimal information."""
        # Insert an active filing
        filing_id = self.db.insert_active_filing("Test Franchise", "2023-12-31", "wisconsin")
        
        # Insert franchise metadata
        metadata_id = self.db.insert_franchise_metadata(
            filing_id, "123456", "Test Legal Name", "2022-01-01", "2023-12-31",
            "Registered"
        )
        
        # Insert FDD metadata with minimal information
        fdd_url = "https://example.com/fdd"
        fdd_file_name = "123456_Test_Franchise_2022.pdf"
        fdd_file_path = "/path/to/fdd/123456_Test_Franchise_2022.pdf"
        
        fdd_id = self.db.insert_fdd_metadata(
            metadata_id, fdd_url, fdd_file_name, fdd_file_path
        )
        
        # Check if the FDD metadata was inserted
        self.assertIsNotNone(fdd_id)
        self.db.cursor.execute("SELECT * FROM fdd_metadata WHERE id = ?", (fdd_id,))
        row = self.db.cursor.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row['franchise_metadata_id'], metadata_id)
        self.assertEqual(row['fdd_url'], fdd_url)
        self.assertEqual(row['fdd_file_name'], fdd_file_name)
        self.assertEqual(row['fdd_file_path'], fdd_file_path)
        self.assertIsNone(row['fdd_file_size'])
        self.assertIsNone(row['fdd_file_download_date'])
        self.assertIsNone(row['num_pages'])

    def test_get_all_active_filings(self):
        """Test getting all active filings."""
        # Insert some active filings
        self.db.insert_active_filing("Test Franchise 1", "2023-12-31", "wisconsin")
        self.db.insert_active_filing("Test Franchise 2", "2023-12-31", "wisconsin")
        self.db.insert_active_filing("Test Franchise 3", "2023-12-31", "wisconsin")
        
        # Get all filings
        filings = self.db.get_all_active_filings()
        
        # Check if all filings were returned
        self.assertEqual(len(filings), 3)
        
        # Check if the filings have the correct format
        for filing in filings:
            self.assertIn('id', filing)
            self.assertIn('franchise_name', filing)
            self.assertIn('expiration_date', filing)
            self.assertIn('active_state', filing)

    def test_get_franchise_by_name(self):
        """Test getting a franchise by name."""
        # Insert an active filing
        franchise_name = "Test Franchise"
        expiration_date = "2023-12-31"
        active_state = "wisconsin"
        self.db.insert_active_filing(franchise_name, expiration_date, active_state)
        
        # Get the franchise by name
        franchise = self.db.get_franchise_by_name(franchise_name)
        
        # Check if the franchise was returned
        self.assertIsNotNone(franchise)
        self.assertEqual(franchise['franchise_name'], franchise_name)
        self.assertEqual(franchise['expiration_date'], expiration_date)
        self.assertEqual(franchise['active_state'], active_state)

    def test_get_franchise_by_name_not_found(self):
        """Test getting a franchise by name that doesn't exist."""
        # Get a franchise that doesn't exist
        franchise = self.db.get_franchise_by_name("Non-existent Franchise")
        
        # Check if None was returned
        self.assertIsNone(franchise)


if __name__ == '__main__':
    unittest.main() 