#!/bin/bash

# Configuration
VENV_DIR="venv"
PYTHON_CMD="python3"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Local RAG App Setup...${NC}"

# Check if python3 is installed
if ! command -v $PYTHON_CMD &> /dev/null; then
    echo -e "${RED}Error: python3 could not be found.${NC}"
    echo "Please install Python (recommended version 3.10 or 3.11)."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}Creating virtual environment in $VENV_DIR...${NC}"
    $PYTHON_CMD -m venv $VENV_DIR
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to create virtual environment.${NC}"
        exit 1
    fi
    echo -e "${GREEN}Virtual environment created.${NC}"
else
    echo -e "${GREEN}Virtual environment found.${NC}"
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Upgrade pip
echo -e "${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip

# Install dependencies
if [ -f "requirements.txt" ]; then
    echo -e "${YELLOW}Installing/Updating dependencies...${NC}"
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to install dependencies.${NC}"
        echo "If you are on Python 3.12 and this failed, try using Python 3.11."
        exit 1
    fi
else
    echo -e "${RED}requirements.txt not found!${NC}"
    exit 1
fi

# Run the application
echo -e "${GREEN}Starting Streamlit App...${NC}"
streamlit run app/main.py
