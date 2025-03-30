# FDD WebScrape Tests

This directory contains automated tests for the FDD WebScrape project.

## Running Tests

To run the tests, you can use the following commands from the project root directory:

```bash
# Run all tests with coverage
./run_tests.sh

# Run a specific test file
python -m pytest tests/test_database.py -v

# Run a specific test case
python -m pytest tests/test_database.py::TestDatabase::test_connection -v
```

## Test Coverage

The project aims to maintain at least 80% test coverage. You can view the coverage report after running the tests with:

```bash
# View the HTML coverage report (generated after running tests)
open htmlcov/index.html
```

## Test Structure

- `conftest.py`: Configuration file for pytest
- `utils.py`: Utility functions for testing
- `test_*.py`: Individual test files for different modules

## Writing New Tests

When writing new tests, follow these guidelines:

1. Create test files with the prefix `test_` followed by the name of the module being tested
2. Use descriptive test names that explain what functionality is being tested
3. Follow the existing pattern of using unittest's `TestCase` classes
4. Mock external dependencies where appropriate
5. Test both successful and error cases

Example of a good test method name:
```python
def test_get_franchise_by_name_not_found(self):
    """Test getting a franchise by name that doesn't exist."""
    # Test implementation
```

## Troubleshooting

If you encounter import errors when running tests directly, make sure to:

1. Run tests from the project root directory
2. Use `python -m pytest` instead of just `pytest`
3. Check that the virtual environment is activated 