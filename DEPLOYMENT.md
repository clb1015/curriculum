# 🚀 Educational Assistant - Comprehensive Deployment Guide

This guide provides detailed instructions for deploying the Educational Assistant to various cloud platforms and environments.

## 📋 Prerequisites

Before deploying to any platform, ensure you have:

- ✅ Python 3.9+ installed locally
- ✅ Git installed and configured
- ✅ Your project files ready (app.py, requirements.txt, etc.)
- ✅ Google Drive API credentials (credentials.json)
- ✅ Document index files (document.index, documents.json) - run `python ingest.py` first

## 🌐 Cloud Platform Options

### 1. 🟣 **Heroku** (Recommended for Beginners)

**💰 Cost:** Free tier available (550 dyno hours/month), Paid plans start at $7/month

**⚡ Pros:** Easy deployment, good documentation, automatic SSL
**⚠️ Cons:** Free tier sleeps after 30min inactivity, limited to 512MB RAM on free tier

#### Step-by-Step Deployment:

1. **Install Heroku CLI**
   ```bash
   # macOS
   brew tap heroku/brew && brew install heroku

   # Ubuntu/Debian
   curl https://cli-assets.heroku.com/install.sh | sh

   # Windows
   # Download from: https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Login to Heroku**
   ```bash
   heroku login
   ```

3. **Create Heroku App**
   ```bash
   heroku create your-educational-assistant
   # Or let Heroku generate a name:
   heroku create
   ```

4. **Set Environment Variables**
   ```bash
   heroku config:set FLASK_ENV=production
   heroku config:set FLASK_DEBUG=False
   heroku config:set CHUNK_SIZE=300
   heroku config:set CHUNK_OVERLAP=50
   heroku config:set MAX_CHUNKS=4
   heroku config:set EMBEDDING_MODEL=all-MiniLM-L6-v2
   ```

5. **Deploy**
   ```bash
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```

6. **Open Your App**
   ```bash
   heroku open
   ```

#### Heroku Troubleshooting:
- **Memory Issues:** Upgrade to Hobby dyno ($7/month) for 512MB → 1GB RAM
- **Timeout Issues:** Add `--timeout 120` to Procfile
- **Build Failures:** Check `heroku logs --tail` for detailed error messages

---

### 2. 🚂 **Railway** (Modern & Developer-Friendly)

**💰 Cost:** $5/month for 500 hours, then $0.000463/GB-hour
**⚡ Pros:** Modern interface, automatic deployments, good free tier
**⚠️ Cons:** Newer platform, smaller community

#### Step-by-Step Deployment:

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   # Or using curl:
   curl -fsSL https://railway.app/install.sh | sh
   ```

2. **Login to Railway**
   ```bash
   railway login
   ```

3. **Initialize Project**
   ```bash
   railway init
   ```

4. **Set Environment Variables**
   ```bash
   railway variables set FLASK_ENV=production
   railway variables set FLASK_DEBUG=False
   railway variables set CHUNK_SIZE=300
   railway variables set CHUNK_OVERLAP=50
   railway variables set MAX_CHUNKS=4
   railway variables set EMBEDDING_MODEL=all-MiniLM-L6-v2
   ```

5. **Deploy**
   ```bash
   railway up
   ```

#### Railway Troubleshooting:
- **Build Issues:** Check the build logs in Railway dashboard
- **Memory Limits:** Railway automatically scales, but monitor usage
- **Custom Domain:** Available in Railway dashboard under Settings

---

### 3. ☁️ **Google Cloud Run** (Serverless & Scalable)

**💰 Cost:** Pay-per-use, ~$0.40/million requests, 2M requests/month free
**⚡ Pros:** Serverless, scales to zero, enterprise-grade
**⚠️ Cons:** More complex setup, requires Google Cloud account

#### Step-by-Step Deployment:

1. **Install Google Cloud SDK**
   ```bash
   # macOS
   brew install --cask google-cloud-sdk

   # Ubuntu/Debian
   curl https://sdk.cloud.google.com | bash
   exec -l $SHELL

   # Windows: Download from https://cloud.google.com/sdk/docs/install
   ```

2. **Authenticate**
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

3. **Enable APIs**
   ```bash
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable run.googleapis.com
   ```

4. **Deploy**
   ```bash
   gcloud run deploy educational-assistant \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --memory 2Gi \
     --cpu 2 \
     --timeout 300 \
     --set-env-vars FLASK_ENV=production,FLASK_DEBUG=False,CHUNK_SIZE=300
   ```

#### Google Cloud Run Troubleshooting:
- **Cold Starts:** Use `--min-instances 1` to keep one instance warm
- **Memory Issues:** Increase `--memory` to 4Gi if needed
- **Timeout Issues:** Increase `--timeout` to 900 (max)

---

### 4. 🎨 **Render** (Simple & Reliable)

**💰 Cost:** Free tier available, Paid plans start at $7/month
**⚡ Pros:** Simple setup, automatic SSL, good free tier
**⚠️ Cons:** Free tier spins down after 15min inactivity

#### Step-by-Step Deployment:

1. **Push Code to GitHub**
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

2. **Create Render Account**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub

3. **Create Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Use these settings:
     - **Build Command:** `pip install -r cloud-requirements.txt`
     - **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT`

4. **Set Environment Variables**
   ```
   FLASK_ENV=production
   FLASK_DEBUG=False
   CHUNK_SIZE=300
   CHUNK_OVERLAP=50
   MAX_CHUNKS=4
   EMBEDDING_MODEL=all-MiniLM-L6-v2
   ```

5. **Deploy**
   - Click "Create Web Service"
   - Render will automatically deploy

#### Render Troubleshooting:
- **Build Failures:** Check build logs in Render dashboard
- **Memory Issues:** Upgrade to paid plan for more RAM
- **Custom Domain:** Available in Render dashboard

---

### 5. 🔷 **DigitalOcean App Platform**

**💰 Cost:** $5/month for basic plan
**⚡ Pros:** Simple pricing, good performance, managed databases
**⚠️ Cons:** No free tier for apps

#### Step-by-Step Deployment:

1. **Create DigitalOcean Account**
   - Go to [digitalocean.com](https://digitalocean.com)
   - Sign up and verify account

2. **Create App**
   - Go to Apps → Create App
   - Connect GitHub repository
   - Select your repository and branch

3. **Configure App**
   - **Build Command:** `pip install -r cloud-requirements.txt`
   - **Run Command:** `gunicorn app:app --bind 0.0.0.0:$PORT`
   - **HTTP Port:** 8080

4. **Set Environment Variables**
   ```
   FLASK_ENV=production
   FLASK_DEBUG=False
   CHUNK_SIZE=300
   CHUNK_OVERLAP=50
   MAX_CHUNKS=4
   EMBEDDING_MODEL=all-MiniLM-L6-v2
   ```

5. **Deploy**
   - Review settings and click "Create Resources"

---

## 🔧 Production Optimizations

### Memory Management
```python
# Add to app.py for better memory usage
import gc
import psutil

@app.after_request
def after_request(response):
    gc.collect()  # Force garbage collection
    return response
```

### Caching
```python
# Add simple caching for embeddings
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_cached_embedding(text):
    return embedding_model.encode(text)
```

### Health Checks
```python
# Already included in app.py
@app.route('/health')
def health_check():
    return {'status': 'healthy', 'timestamp': datetime.now().isoformat()}
```

## 🚨 Common Issues & Solutions

### 1. **Large Model Files**
**Problem:** Transformers models are too large for some platforms
**Solution:** Use smaller models or model caching
```python
# Use smaller model for production
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # 90MB instead of 500MB+
LLM_MODEL = "microsoft/DialoGPT-medium"  # Smaller than Llama
```

### 2. **Memory Errors**
**Problem:** Out of memory during model loading
**Solution:** 
- Upgrade to higher memory tier
- Use CPU-only versions: `torch==2.0.1+cpu`
- Implement lazy loading

### 3. **Cold Start Issues**
**Problem:** First request takes too long
**Solution:**
- Keep one instance warm (paid tiers)
- Implement health check endpoints
- Use smaller models

### 4. **File Upload Issues**
**Problem:** Can't upload document.index files
**Solution:**
- Use cloud storage (Google Cloud Storage, AWS S3)
- Rebuild index on first startup
- Use environment variables for configuration

## 📊 Cost Comparison

| Platform | Free Tier | Paid Tier | Best For |
|----------|-----------|-----------|----------|
| **Heroku** | 550 hours/month | $7/month | Beginners |
| **Railway** | $5 credit | $5/month | Developers |
| **Google Cloud Run** | 2M requests/month | Pay-per-use | Enterprise |
| **Render** | 750 hours/month | $7/month | Simplicity |
| **DigitalOcean** | None | $5/month | Predictable costs |

## 🔐 Security Considerations

### Environment Variables
Never commit these to git:
- `GOOGLE_DRIVE_FOLDER_ID`
- `credentials.json`
- `token.json`
- Any API keys

### HTTPS
All recommended platforms provide automatic HTTPS/SSL certificates.

### Rate Limiting
Consider adding rate limiting for production:
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)
```

## 🎯 Quick Start Commands

### Automated Deployment
```bash
# Make deploy script executable
chmod +x deploy.sh

# Run deployment script
./deploy.sh
```

### Manual Deployment (Any Platform)
```bash
# 1. Prepare files
cp requirements.txt cloud-requirements.txt

# 2. Set up git (if not already)
git init
git add .
git commit -m "Initial commit"

# 3. Follow platform-specific instructions above
```

## 📞 Support & Resources

- **Heroku:** [devcenter.heroku.com](https://devcenter.heroku.com)
- **Railway:** [docs.railway.app](https://docs.railway.app)
- **Google Cloud:** [cloud.google.com/run/docs](https://cloud.google.com/run/docs)
- **Render:** [render.com/docs](https://render.com/docs)
- **DigitalOcean:** [docs.digitalocean.com/products/app-platform](https://docs.digitalocean.com/products/app-platform)

## 🔄 Updates & Maintenance

### Updating Your Deployment
```bash
# 1. Update your code
git add .
git commit -m "Update application"

# 2. Push to deploy (most platforms auto-deploy)
git push origin main

# 3. For Heroku specifically:
git push heroku main
```

### Monitoring
- Check application logs regularly
- Monitor memory and CPU usage
- Set up alerts for downtime
- Keep dependencies updated

---

**🎉 Congratulations!** Your Educational Assistant is now running in the cloud and accessible to teachers worldwide!

For additional help, check the troubleshooting section or contact support through your chosen platform.
