# 🎓 Educational Assistant - AI-Powered Lesson Plan Generator

[![CI/CD Pipeline](https://github.com/YOUR_USERNAME/educational-assistant/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/educational-assistant/actions/workflows/ci.yml)
[![Deploy](https://github.com/YOUR_USERNAME/educational-assistant/actions/workflows/deploy.yml/badge.svg)](https://github.com/YOUR_USERNAME/educational-assistant/actions/workflows/deploy.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful web-based educational assistant that generates standards-aligned lesson plans for K-12 teachers using Retrieval-Augmented Generation (RAG) technology. The system processes district curriculum documents and creates customized lesson plans based on teacher requirements.

## 🌟 Features

### 🔍 **Intelligent Document Processing**
- **Google Drive Integration**: Automatically processes PDF documents from your district's Google Drive folder
- **Advanced Text Extraction**: Uses PyMuPDF for high-quality text extraction from curriculum documents
- **Smart Chunking**: Splits documents into overlapping chunks for optimal retrieval
- **Vector Search**: FAISS-powered semantic search for relevant content retrieval

### 🎯 **Specialized Lesson Plan Generation**
- **Elementary Music Format**: 12-section comprehensive format with Florida Standards, Marzano elements, and SELARTS framework
- **General Subject Format**: 6-section streamlined format for all other subjects and grade levels
- **Duration Intelligence**: Automatically extracts lesson duration and adds 5-minute extension activities
- **Standards Alignment**: Incorporates relevant state and national standards

### 🌐 **Dual Knowledge Modes**
- **📚 Document-Grounded**: Responses based solely on district curriculum documents
- **🌐 External Knowledge**: Incorporates general best practices when explicitly requested
- **Smart Detection**: Automatically identifies when external knowledge is needed

### 💻 **Modern Web Interface**
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Real-time Feedback**: Live character counting, form validation, and progress indicators
- **Markdown Rendering**: Beautiful formatting of generated lesson plans
- **Export Options**: Copy to clipboard and download as Markdown files

### ☁️ **Cloud-Ready Deployment**
- **Multiple Platforms**: Deploy to Heroku, Railway, Render, Vercel, Google Cloud, and more
- **GitHub Integration**: One-click deployment buttons and automated CI/CD
- **Docker Support**: Containerized deployment with Docker and docker-compose
- **Auto-scaling**: Serverless and container-based scaling options

## 🚀 Quick Start

### Option 1: One-Click Cloud Deployment

[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/YOUR_USERNAME/educational-assistant)
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/YOUR_USERNAME/educational-assistant)
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template/your-template-id)

### Option 2: Local Development

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/educational-assistant.git
cd educational-assistant

# Run automated setup
chmod +x setup.sh
./setup.sh

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Add Google Drive credentials
# Download credentials.json from Google Cloud Console

# Process documents
python ingest.py

# Start the application
python app.py
```

### Option 3: GitHub Codespaces

1. Click the green "Code" button in this repository
2. Select "Codespaces" tab
3. Click "Create codespace on main"
4. Wait for the environment to set up (2-3 minutes)
5. Start coding immediately in VS Code in your browser!

## 📋 System Requirements

### Minimum Requirements
- **Python**: 3.9 or higher
- **Memory**: 2GB RAM (4GB recommended)
- **Storage**: 1GB free space
- **Internet**: Stable connection for model downloads

### Recommended for Production
- **Memory**: 4GB+ RAM
- **CPU**: 2+ cores
- **Storage**: 5GB+ free space
- **Platform**: Cloud deployment (Heroku, Railway, etc.)

## 🛠️ Installation & Setup

### 1. Prerequisites

```bash
# Check Python version
python3 --version  # Should be 3.9+

# Install pip if not available
python3 -m ensurepip --upgrade
```

### 2. Environment Setup

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Google Drive API Setup

1. **Go to [Google Cloud Console](https://console.cloud.google.com/)**
2. **Create a new project** or select existing
3. **Enable Google Drive API**
4. **Create credentials** (OAuth 2.0 Client ID)
5. **Download credentials.json** and place in project root
6. **Get your Google Drive folder ID** from the URL when viewing the folder

### 4. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your settings
GOOGLE_DRIVE_FOLDER_ID=your_folder_id_here
CHUNK_SIZE=300
CHUNK_OVERLAP=50
MAX_CHUNKS=4
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

### 5. Document Processing

```bash
# Run the ingestion script
python ingest.py

# Follow prompts to authenticate and process documents
# This creates document.index and documents.json files
```

### 6. Start the Application

```bash
# Development mode
python app.py

# Production mode with Gunicorn
gunicorn app:app --bind 0.0.0.0:5000 --workers 1 --timeout 120
```

## 📁 Project Structure

```
educational-assistant/
├── 📄 app.py                 # Main Flask application
├── 📄 ingest.py              # Document processing script
├── 📄 requirements.txt       # Development dependencies
├── 📄 cloud-requirements.txt # Production dependencies
├── 📁 templates/
│   └── 📄 index.html         # Web interface template
├── 📁 static/
│   ├── 📄 style.css          # Responsive CSS styling
│   └── 📄 script.js          # Interactive JavaScript
├── 📁 .github/
│   ├── 📁 workflows/
│   │   ├── 📄 ci.yml         # Continuous integration
│   │   └── 📄 deploy.yml     # Multi-platform deployment
│   └── 📁 .devcontainer/
│       └── 📄 devcontainer.json # GitHub Codespaces config
├── 📄 Procfile               # Heroku deployment
├── 📄 vercel.json            # Vercel serverless config
├── 📄 netlify.toml           # Netlify deployment
├── 📄 railway.json           # Railway platform config
├── 📄 app.yaml               # Google Cloud App Engine
├── 📄 Dockerfile             # Container configuration
├── 📄 docker-compose.yml     # Multi-container setup
├── 📄 setup.sh               # Automated installation
├── 📄 deploy.sh              # Multi-platform deployment
├── 📄 .env.example           # Environment variables template
├── 📄 .gitignore             # Version control exclusions
├── 📄 README.md              # This file
├── 📄 DEPLOYMENT.md          # Detailed deployment guide
└── 📄 GITHUB_DEPLOY.md       # GitHub deployment guide
```

## 🎯 Usage Guide

### Basic Lesson Plan Generation

1. **Open the web interface** at `http://localhost:5000`
2. **Describe your lesson** in the text area (e.g., "Create a 30-minute elementary music lesson about rhythm and beat for 2nd graders")
3. **Select duration** from the dropdown or enter custom duration
4. **Choose knowledge mode**:
   - Default: Uses only district documents
   - Check "Include external knowledge" for broader content
5. **Click "Generate Lesson Plan"**
6. **Review, copy, or download** the generated lesson plan

### Advanced Features

#### Elementary Music Lessons
When the system detects elementary music content, it automatically uses the comprehensive 12-section format:
- Overview with grade level and duration
- Florida Standards (MU)
- Learning Goals (I can...)
- Learning Targets (I will...)
- Materials & Resources
- Activities Timeline with Marzano elements
- Life-Skills Competencies (CASEL + NCAS)
- Assessment strategies
- Teacher Reflection Prompts
- Tech/AI Enhancement suggestions
- Alignment Summary
- SELARTS Framework connections

#### Duration Intelligence
The system automatically:
- Extracts duration from natural language ("30 minutes", "1 hour", "class period")
- Adds 5 minutes for extension and differentiation activities
- Adjusts timeline accordingly

#### External Knowledge Integration
Add phrases like "search the web", "best practices", or "include external ideas" to incorporate general educational knowledge beyond district documents.

## 🔧 Configuration Options

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_ENV` | `development` | Flask environment mode |
| `FLASK_DEBUG` | `True` | Enable debug mode |
| `PORT` | `5000` | Server port |
| `GOOGLE_DRIVE_FOLDER_ID` | - | Google Drive folder containing PDFs |
| `CHUNK_SIZE` | `300` | Text chunk size in words |
| `CHUNK_OVERLAP` | `50` | Overlap between chunks |
| `MAX_CHUNKS` | `4` | Maximum chunks for context |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Sentence transformer model |
| `LLM_MODEL` | `microsoft/DialoGPT-medium` | Language model |

### Model Configuration

#### Embedding Models (Sentence Transformers)
- `all-MiniLM-L6-v2` (default): Fast, 90MB, good quality
- `all-mpnet-base-v2`: Higher quality, 420MB
- `all-distilroberta-v1`: Balanced, 290MB

#### Language Models
- `microsoft/DialoGPT-medium` (default): Conversational, 350MB
- `gpt2`: Classic generative model, 500MB
- `distilgpt2`: Smaller, faster version, 320MB

## 🚀 Deployment Guide

### Cloud Platforms

#### Heroku (Recommended for Beginners)
```bash
# Install Heroku CLI
# Login and create app
heroku login
heroku create your-app-name

# Set environment variables
heroku config:set FLASK_ENV=production
heroku config:set GOOGLE_DRIVE_FOLDER_ID=your_folder_id

# Deploy
git push heroku main
```

#### Railway (Modern & Fast)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

#### Google Cloud Run (Enterprise)
```bash
# Install Google Cloud SDK
# Authenticate and deploy
gcloud auth login
gcloud run deploy --source .
```

#### Render (Simple & Reliable)
1. Connect GitHub repository at render.com
2. Set build command: `pip install -r cloud-requirements.txt`
3. Set start command: `gunicorn app:app --bind 0.0.0.0:$PORT`
4. Add environment variables
5. Deploy!

### Docker Deployment

```bash
# Build and run with Docker
docker build -t educational-assistant .
docker run -p 5000:5000 educational-assistant

# Or use docker-compose
docker-compose up -d
```

### Automated Deployment

```bash
# Use the deployment script
chmod +x deploy.sh
./deploy.sh

# Or use GitHub Actions
# Push to main branch triggers automatic deployment
```

## 🧪 Testing

### Run Tests
```bash
# Install test dependencies
pip install pytest pytest-cov flake8

# Run tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Lint code
flake8 .
```

### Manual Testing
1. **Health Check**: Visit `/health` endpoint
2. **Basic Generation**: Create a simple lesson plan
3. **Elementary Music**: Test with music-related queries
4. **External Knowledge**: Test with "best practices" queries
5. **Duration Extraction**: Test various duration formats

## 🔒 Security Considerations

### Sensitive Data
- **Never commit** `credentials.json` or `.env` files
- **Use environment variables** for all secrets
- **Rotate API keys** regularly
- **Enable HTTPS** in production

### API Security
- **Rate limiting** implemented for production
- **Input validation** on all endpoints
- **CORS protection** configured
- **Error handling** prevents information leakage

### Data Privacy
- **No user data storage** by default
- **Document processing** happens locally
- **API calls** are logged but not stored
- **GDPR compliant** design

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Workflow
1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Code Standards
- **Python**: Follow PEP 8 style guide
- **JavaScript**: Use ES6+ features
- **CSS**: Follow BEM methodology
- **Documentation**: Update README for new features

## 📞 Support & Community

### Getting Help
- **📖 Documentation**: Check [DEPLOYMENT.md](DEPLOYMENT.md) for detailed guides
- **🐛 Issues**: Report bugs via [GitHub Issues](https://github.com/YOUR_USERNAME/educational-assistant/issues)
- **💡 Discussions**: Join [GitHub Discussions](https://github.com/YOUR_USERNAME/educational-assistant/discussions)
- **📧 Email**: Contact support@educational-assistant.com

### Community Resources
- **🎓 Teacher Forum**: Share lesson plans and tips
- **🔧 Developer Chat**: Technical discussions and contributions
- **📚 Knowledge Base**: FAQs and troubleshooting guides
- **🎥 Video Tutorials**: Step-by-step setup and usage guides

## 📊 Performance & Scaling

### Performance Metrics
- **Response Time**: < 10 seconds for lesson generation
- **Throughput**: 100+ concurrent users (with proper scaling)
- **Memory Usage**: ~500MB base + models
- **Storage**: ~1GB for models and indices

### Scaling Options
- **Horizontal**: Multiple app instances with load balancer
- **Vertical**: Increase memory/CPU for single instance
- **Caching**: Redis for embedding and response caching
- **CDN**: Static asset delivery optimization

## 🔄 Updates & Maintenance

### Regular Maintenance
- **Dependencies**: Update monthly for security patches
- **Models**: Refresh quarterly for improved performance
- **Documents**: Re-run ingestion when curriculum updates
- **Monitoring**: Check logs and performance metrics

### Update Process
```bash
# Update dependencies
pip install --upgrade -r requirements.txt

# Update models (if needed)
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Re-process documents (if curriculum changed)
python ingest.py

# Deploy updates
git push origin main  # Triggers auto-deployment
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Hugging Face** for transformers and sentence-transformers
- **Facebook AI** for FAISS vector search
- **Google** for Drive API and Cloud services
- **Flask** community for the web framework
- **Teachers everywhere** who inspire this project

## 📈 Roadmap

### Version 2.0 (Coming Soon)
- **Multi-language support** for international schools
- **Advanced analytics** for lesson plan effectiveness
- **Collaborative features** for teacher teams
- **Mobile app** for iOS and Android

### Version 3.0 (Future)
- **AI-powered assessment** generation
- **Student progress tracking** integration
- **Parent communication** features
- **District-wide analytics** dashboard

---

**Made with ❤️ for educators worldwide**

*Empowering teachers with AI-powered lesson planning since 2024*
