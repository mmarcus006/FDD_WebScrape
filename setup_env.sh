#!/bin/bash
# Setup script for FDD WebScrape project

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov

# Install the package in development mode
pip install -e .

echo "Environment setup complete! Activate with: source .venv/bin/activate" 