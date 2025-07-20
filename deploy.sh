#!/bin/bash

# Educational Assistant - Multi-Platform Deployment Script
# This script helps deploy the educational assistant to various cloud platforms

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

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."

    # Check Python
    if ! command_exists python3; then
        print_error "Python 3 is required but not installed."
        exit 1
    fi

    # Check pip
    if ! command_exists pip; then
        print_error "pip is required but not installed."
        exit 1
    fi

    # Check git
    if ! command_exists git; then
        print_error "git is required but not installed."
        exit 1
    fi

    print_success "Prerequisites check passed"
}

# Function to prepare for deployment
prepare_deployment() {
    print_status "Preparing deployment..."

    # Create necessary directories
    mkdir -p logs temp

    # Check if required files exist
    if [ ! -f "app.py" ]; then
        print_error "app.py not found. Make sure you're in the project directory."
        exit 1
    fi

    if [ ! -f "requirements.txt" ]; then
        print_error "requirements.txt not found."
        exit 1
    fi

    # Create production requirements if it doesn't exist
    if [ ! -f "cloud-requirements.txt" ]; then
        print_warning "cloud-requirements.txt not found. Creating from requirements.txt..."
        cp requirements.txt cloud-requirements.txt
    fi

    print_success "Deployment preparation completed"
}

# Function to deploy to Heroku
deploy_heroku() {
    print_status "Deploying to Heroku..."

    if ! command_exists heroku; then
        print_error "Heroku CLI is not installed. Please install it first."
        print_status "Visit: https://devcenter.heroku.com/articles/heroku-cli"
        return 1
    fi

    # Check if user is logged in
    if ! heroku auth:whoami >/dev/null 2>&1; then
        print_status "Please log in to Heroku:"
        heroku login
    fi

    # Create Heroku app if it doesn't exist
    read -p "Enter your Heroku app name (or press Enter for auto-generated): " app_name

    if [ -z "$app_name" ]; then
        heroku create
    else
        heroku create "$app_name" || print_warning "App might already exist"
    fi

    # Set environment variables
    print_status "Setting environment variables..."
    heroku config:set FLASK_ENV=production
    heroku config:set FLASK_DEBUG=False
    heroku config:set CHUNK_SIZE=300
    heroku config:set CHUNK_OVERLAP=50
    heroku config:set MAX_CHUNKS=4
    heroku config:set EMBEDDING_MODEL=all-MiniLM-L6-v2

    # Deploy
    git add .
    git commit -m "Deploy to Heroku" || print_warning "No changes to commit"
    git push heroku main || git push heroku master

    print_success "Heroku deployment completed!"
    heroku open
}

# Function to deploy to Railway
deploy_railway() {
    print_status "Deploying to Railway..."

    if ! command_exists railway; then
        print_error "Railway CLI is not installed. Please install it first."
        print_status "Visit: https://docs.railway.app/develop/cli"
        return 1
    fi

    # Login to Railway
    railway login

    # Initialize project
    railway init

    # Deploy
    railway up

    print_success "Railway deployment completed!"
}

# Function to deploy to Google Cloud Run
deploy_gcp() {
    print_status "Deploying to Google Cloud Run..."

    if ! command_exists gcloud; then
        print_error "Google Cloud SDK is not installed. Please install it first."
        print_status "Visit: https://cloud.google.com/sdk/docs/install"
        return 1
    fi

    # Check authentication
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -n 1 >/dev/null; then
        print_status "Please authenticate with Google Cloud:"
        gcloud auth login
    fi

    # Set project
    read -p "Enter your Google Cloud Project ID: " project_id
    gcloud config set project "$project_id"

    # Enable required APIs
    print_status "Enabling required APIs..."
    gcloud services enable cloudbuild.googleapis.com
    gcloud services enable run.googleapis.com

    # Build and deploy
    read -p "Enter service name (default: educational-assistant): " service_name
    service_name=${service_name:-educational-assistant}

    gcloud run deploy "$service_name" \
        --source . \
        --platform managed \
        --region us-central1 \
        --allow-unauthenticated \
        --memory 2Gi \
        --cpu 2 \
        --timeout 300 \
        --set-env-vars FLASK_ENV=production,FLASK_DEBUG=False

    print_success "Google Cloud Run deployment completed!"
}

# Function to deploy to Render
deploy_render() {
    print_status "Deploying to Render..."

    print_status "For Render deployment:"
    echo "1. Go to https://render.com and create an account"
    echo "2. Connect your GitHub repository"
    echo "3. Create a new Web Service"
    echo "4. Use these settings:"
    echo "   - Build Command: pip install -r cloud-requirements.txt"
    echo "   - Start Command: gunicorn app:app --bind 0.0.0.0:\$PORT"
    echo "   - Environment Variables:"
    echo "     FLASK_ENV=production"
    echo "     FLASK_DEBUG=False"
    echo "     CHUNK_SIZE=300"
    echo "     CHUNK_OVERLAP=50"
    echo "     MAX_CHUNKS=4"
    echo "     EMBEDDING_MODEL=all-MiniLM-L6-v2"

    print_success "Render deployment instructions provided!"
}

# Function to show deployment options
show_menu() {
    echo ""
    echo "=== Educational Assistant Deployment Script ==="
    echo ""
    echo "Choose a deployment platform:"
    echo "1) Heroku (Free tier available)"
    echo "2) Railway (Free tier available)"
    echo "3) Google Cloud Run (Pay-as-you-go)"
    echo "4) Render (Free tier available)"
    echo "5) Show all deployment instructions"
    echo "6) Exit"
    echo ""
}

# Main deployment function
main() {
    print_status "Educational Assistant Deployment Script"
    print_status "========================================"

    check_prerequisites
    prepare_deployment

    while true; do
        show_menu
        read -p "Enter your choice (1-6): " choice

        case $choice in
            1)
                deploy_heroku
                ;;
            2)
                deploy_railway
                ;;
            3)
                deploy_gcp
                ;;
            4)
                deploy_render
                ;;
            5)
                echo ""
                echo "=== Deployment Instructions ==="
                echo ""
                echo "HEROKU:"
                echo "- Install Heroku CLI"
                echo "- Run: heroku login"
                echo "- Run: heroku create your-app-name"
                echo "- Run: git push heroku main"
                echo ""
                echo "RAILWAY:"
                echo "- Install Railway CLI"
                echo "- Run: railway login"
                echo "- Run: railway init"
                echo "- Run: railway up"
                echo ""
                echo "GOOGLE CLOUD RUN:"
                echo "- Install Google Cloud SDK"
                echo "- Run: gcloud auth login"
                echo "- Run: gcloud run deploy --source ."
                echo ""
                echo "RENDER:"
                echo "- Connect GitHub repo to Render"
                echo "- Set build command: pip install -r cloud-requirements.txt"
                echo "- Set start command: gunicorn app:app --bind 0.0.0.0:\$PORT"
                echo ""
                ;;
            6)
                print_success "Goodbye!"
                exit 0
                ;;
            *)
                print_error "Invalid choice. Please try again."
                ;;
        esac

        echo ""
        read -p "Press Enter to continue..."
    done
}

# Run main function
main "$@"
