# Deployment Guide for ImageToVideo Creator

This guide covers various deployment options to make your ImageToVideo Creator publicly accessible.

## Quick Deployment Options

### 1. Ngrok (Fastest - For Testing/Demo)

**Best for:** Quick sharing, testing, demos
**Cost:** Free tier available
**Setup time:** 2 minutes

```bash
# Install ngrok
brew install ngrok  # macOS
# or download from https://ngrok.com/

# Start your Flask app
python gui_web.py

# In another terminal, expose it publicly
ngrok http 5000
```

Ngrok will provide a public URL like `https://abc123.ngrok.io` that anyone can access.

### 2. Railway (Easy Cloud Deployment)

**Best for:** Simple cloud hosting
**Cost:** Free tier available
**Setup time:** 10 minutes

1. Create account at [railway.app](https://railway.app)
2. Install Railway CLI:
   ```bash
   npm install -g @railway/cli
   ```
3. Deploy:
   ```bash
   railway login
   railway init
   railway up
   ```

### 3. Vercel (Serverless Platform)

**Best for:** Serverless Python apps
**Cost:** Free tier available
**Setup time:** 5 minutes

1. Create account at [vercel.com](https://vercel.com)
2. Connect your GitHub repository
3. Vercel auto-detects and deploys

### 4. Netlify (Static Sites + Functions)

**Best for:** Static sites with serverless functions
**Cost:** Free tier available
**Setup time:** 10 minutes
**Note:** Requires converting Flask app to Netlify Functions

1. Create account at [netlify.com](https://netlify.com)
2. Connect GitHub repository
3. Configure build settings

### 5. Heroku (Popular Platform)

**Best for:** Established cloud platform
**Cost:** Paid plans only (no free tier)
**Setup time:** 15 minutes

1. Install Heroku CLI
2. Create deployment files (see Production Setup below)
3. Deploy:
   ```bash
   heroku create your-app-name
   git push heroku main
   ```

## Production Deployment Setup

### Required Files for Cloud Deployment

Create these files in your project root:

#### 1. Procfile (for Heroku/Railway)
```
web: gunicorn gui_web:app
```

#### 2. runtime.txt (specify Python version)
```
python-3.11.0
```

#### 3. Updated requirements.txt
Add production dependencies:
```
moviepy>=1.0.3
numpy>=1.21.0
Pillow>=8.0.0
imageio>=2.9.0
imageio-ffmpeg>=0.4.0
requests>=2.25.0
flask>=2.0.0
opencv-python>=4.5.0
yt-dlp>=2023.1.6
deepgram-sdk>=3.0.0
gunicorn>=20.1.0
```

#### 4. app.json (for easy deployment)
```json
{
  "name": "ImageToVideo Creator",
  "description": "Create videos from images with audio",
  "repository": "https://github.com/yourusername/ImageToVideo",
  "keywords": ["video", "images", "flask", "python"],
  "env": {
    "FLASK_ENV": {
      "description": "Flask environment",
      "value": "production"
    }
  },
  "formation": {
    "web": {
      "quantity": 1,
      "size": "basic"
    }
  }
}
```

### Production Code Changes

Update `gui_web.py` for production:

```python
# Add at the end of gui_web.py
if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug)
```

## Advanced Deployment Options

### 4. DigitalOcean App Platform

**Best for:** Scalable cloud hosting
**Cost:** $5+/month
**Setup time:** 20 minutes

1. Create DigitalOcean account
2. Connect your GitHub repository
3. Configure build settings:
   - Build command: `pip install -r requirements.txt`
   - Run command: `gunicorn gui_web:app`

### 5. AWS Elastic Beanstalk

**Best for:** Enterprise deployment
**Cost:** Pay for resources used
**Setup time:** 30 minutes

1. Install EB CLI:
   ```bash
   pip install awsebcli
   ```
2. Initialize and deploy:
   ```bash
   eb init
   eb create production
   eb deploy
   ```

### 6. Google Cloud Run

**Best for:** Serverless deployment
**Cost:** Pay per use
**Setup time:** 25 minutes

1. Create Dockerfile:
   ```dockerfile
   FROM python:3.11-slim
   
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   
   COPY . .
   
   CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 gui_web:app
   ```

2. Deploy:
   ```bash
   gcloud run deploy --source .
   ```

### 7. Self-Hosted VPS

**Best for:** Full control, cost-effective
**Cost:** $5-20/month
**Setup time:** 45 minutes

#### Ubuntu/Debian VPS Setup:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3 python3-pip nginx supervisor git -y

# Clone your repository
git clone https://github.com/yourusername/ImageToVideo.git
cd ImageToVideo

# Install Python dependencies
pip3 install -r requirements.txt

# Install FFmpeg
sudo apt install ffmpeg -y

# Create systemd service
sudo nano /etc/systemd/system/imagetovideo.service
```

#### Service file content:
```ini
[Unit]
Description=ImageToVideo Flask App
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/ImageToVideo
Environment="PATH=/usr/local/bin"
ExecStart=/usr/local/bin/gunicorn --bind 127.0.0.1:5000 gui_web:app
Restart=always

[Install]
WantedBy=multi-user.target
```

#### Nginx configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    client_max_body_size 500M;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Security Considerations

### 1. Environment Variables
Store sensitive data in environment variables:
```python
import os
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
```

### 2. File Upload Security
The app already implements:
- File size limits (500MB)
- Secure filename handling
- Temporary file cleanup

### 3. Rate Limiting
Add rate limiting for production:
```bash
pip install Flask-Limiter
```

### 4. HTTPS
Always use HTTPS in production:
- Most cloud platforms provide automatic HTTPS
- For VPS: Use Let's Encrypt with Certbot

## Performance Optimization

### 1. Resource Limits
- Increase server memory for video processing
- Consider worker processes for concurrent requests
- Implement request queuing for heavy operations

### 2. File Storage
- Use cloud storage (AWS S3, Google Cloud Storage) for large files
- Implement file cleanup policies
- Consider CDN for static assets

### 3. Monitoring
- Add application monitoring (Sentry, New Relic)
- Set up server monitoring
- Implement logging

## Domain and DNS

1. **Purchase a domain** from providers like:
   - Namecheap
   - GoDaddy
   - Google Domains

2. **Configure DNS** to point to your deployment:
   - For cloud platforms: Use provided DNS settings
   - For VPS: Point A record to server IP

## Recommended Deployment Path

### For Beginners:
1. Start with **Ngrok** for immediate testing
2. Move to **Railway** or **Heroku** for permanent hosting
3. Add custom domain when ready

### For Production:
1. Use **DigitalOcean App Platform** or **AWS**
2. Implement proper monitoring and backups
3. Set up CI/CD pipeline
4. Add SSL certificate

## Cost Estimates

- **Ngrok**: Free (with limitations)
- **Railway**: $5-20/month
- **Vercel**: Free tier, then $20+/month
- **Netlify**: Free tier, then $19+/month
- **Heroku**: $7-25/month
- **DigitalOcean**: $5-50/month
- **AWS/GCP**: Variable, $10-100+/month
- **VPS**: $5-20/month + domain ($10-15/year)

## Support and Maintenance

- Monitor application logs
- Keep dependencies updated
- Regular security updates
- Backup important data
- Monitor resource usage

Choose the deployment option that best fits your technical expertise, budget, and requirements!