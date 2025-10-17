# 🚀 Render Deployment Guide

## Prerequisites
1. **Render Account**: Sign up at [render.com](https://render.com)
2. **GitHub Repository**: Push your code to GitHub
3. **Gemini API Key**: Get from [Google AI Studio](https://makersuite.google.com/app/apikey)

## Deployment Steps

### 1. **Connect GitHub Repository**
- Go to Render Dashboard
- Click "New" → "Web Service"
- Connect your GitHub repository

### 2. **Configure Build Settings**
```
Build Command: ./build.sh
Start Command: streamlit run app.py --server.port $PORT --server.address 0.0.0.0
```

### 3. **Set Environment Variables**
In Render dashboard, add:
```
GEMINI_API_KEY = your_actual_api_key_here
PYTHONPATH = /opt/render/project/src
```

### 4. **Advanced Settings**
- **Runtime**: Python 3.9+
- **Region**: Choose closest to your users
- **Instance Type**: Starter (512MB RAM minimum)

## Alternative: Docker Deployment

### Build Docker Image
```bash
docker build -t google-review-analyser .
docker run -p 8501:8501 -e GEMINI_API_KEY=your_key google-review-analyser
```

## Troubleshooting

### Chrome Issues
- Render automatically installs Chrome via build.sh
- Scraper uses headless mode with optimized settings
- Fallback to Chromium if Chrome fails

### Memory Issues
- Upgrade to higher instance type if needed
- Scraper limits review processing to prevent timeouts

### API Rate Limits
- Gemini API has usage limits
- Consider implementing caching for production

## Testing Deployment
1. Check logs for Chrome installation success
2. Test scraping with a simple Google Maps URL
3. Verify all visualizations load correctly

## Production Considerations
- Set up monitoring and alerts
- Implement error tracking
- Consider Redis for session management
- Add rate limiting for scraping requests