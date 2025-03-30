#!/bin/bash
# Run tests with coverage for FDD WebScrape project

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Run pytest with coverage
python -m pytest tests/ --cov=src --cov-report=term-missing --cov-report=html --cov-fail-under=80

# Show the coverage report location
echo "Detailed HTML coverage report available at: htmlcov/index.html" 