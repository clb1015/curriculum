#!/bin/bash

# Educational Assistant - Automated Setup Script
# This script sets up the development environment

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

print_status "🚀 Educational Assistant Setup Script"
print_status "===================================="

# Check Python version
print_status "Checking Python installation..."
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

    if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 9 ]; then
        print_success "Python $PYTHON_VERSION found"
    else
        print_error "Python 3.9+ required, found $PYTHON_VERSION"
        exit 1
    fi
else
    print_error "Python 3 not found. Please install Python 3.9+"
    exit 1
fi

# Check pip
print_status "Checking pip installation..."
if command_exists pip || command_exists pip3; then
    print_success "pip found"
else
    print_error "pip not found. Please install pip"
    exit 1
fi

# Ask about virtual environment
echo ""
read -p "Do you want to create a virtual environment? (recommended) [y/N]: " create_venv
if [[ $create_venv =~ ^[Yy]$ ]]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv

    print_status "Activating virtual environment..."
    source venv/bin/activate

    print_success "Virtual environment created and activated"
    print_warning "Remember to activate it with: source venv/bin/activate"
fi

# Install dependencies
print_status "Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_success "Dependencies installed from requirements.txt"
else
    print_warning "requirements.txt not found, installing basic dependencies..."
    pip install flask gunicorn
fi

# Create .env file from template
print_status "Setting up environment configuration..."
if [ -f ".env.example" ] && [ ! -f ".env" ]; then
    cp .env.example .env
    print_success "Created .env file from template"
    print_warning "Please edit .env file with your actual configuration values"
else
    print_warning ".env file already exists or .env.example not found"
fi

# Check for credentials.json
print_status "Checking Google Drive API credentials..."
if [ ! -f "credentials.json" ]; then
    print_warning "credentials.json not found"
    print_status "To set up Google Drive API:"
    print_status "1. Go to Google Cloud Console"
    print_status "2. Create a new project or select existing"
    print_status "3. Enable Google Drive API"
    print_status "4. Create credentials (OAuth 2.0)"
    print_status "5. Download and save as credentials.json"
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p logs
mkdir -p temp
print_success "Directories created"

# Check for document index
print_status "Checking document index..."
if [ ! -f "document.index" ] || [ ! -f "documents.json" ]; then
    print_warning "Document index not found"
    print_status "Run 'python ingest.py' to process your documents"
fi

# Summary
echo ""
print_success "🎉 Setup completed successfully!"
print_status "Next steps:"
print_status "1. Edit .env file with your configuration"
print_status "2. Add credentials.json for Google Drive API"
print_status "3. Run 'python ingest.py' to process documents"
print_status "4. Run 'python app.py' to start the application"
echo ""
