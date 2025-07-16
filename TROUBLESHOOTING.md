# Troubleshooting Guide

## Common Installation Issues

### NPM Permission Errors (EACCES)

**Problem**: Getting permission denied errors when installing global npm packages like `netlify-cli` or `vercel`.

**Error Example**:
```
npm error code EACCES
npm error syscall mkdir
npm error path /usr/local/lib/node_modules/netlify-cli
npm error errno -13
```

**Solutions**:

#### Option 1: Use sudo (Quick Fix)
```bash
sudo npm install -g netlify-cli
sudo npm install -g vercel
sudo npm install -g @railway/cli
```

#### Option 2: Fix npm permissions (Recommended)
```bash
# Create a directory for global packages
mkdir ~/.npm-global

# Configure npm to use the new directory
npm config set prefix '~/.npm-global'

# Add to your shell profile (~/.zshrc or ~/.bash_profile)
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.zshrc

# Reload your shell
source ~/.zshrc

# Now install without sudo
npm install -g netlify-cli
npm install -g vercel
npm install -g @railway/cli
```

#### Option 3: Use npx (No Installation Required)
```bash
# Use npx to run commands without global installation
npx netlify-cli deploy --prod
npx vercel --prod
```

#### Option 4: Use Homebrew (macOS)
```bash
# Install via Homebrew instead
brew install netlify-cli
brew install vercel-cli
```

## Python Environment Issues

### Virtual Environment Setup
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### FFmpeg Issues
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

## Deployment Issues

### Port Already in Use
```bash
# Find process using port 5000
lsof -ti:5000

# Kill the process
kill -9 $(lsof -ti:5000)

# Or use a different port
PORT=5001 python gui_web.py
```

### Memory Issues During Video Processing
- Reduce image resolution before processing
- Process fewer images at once
- Increase server memory allocation
- Use cloud platforms with more RAM

### File Upload Limits
```python
# In gui_web.py, adjust max file size
app.config['MAX_CONTENT_LENGTH'] = 1000 * 1024 * 1024  # 1GB
```

## Platform-Specific Issues

### Netlify
- **Issue**: Flask apps don't work directly on Netlify
- **Solution**: Convert to Netlify Functions or use Vercel/Railway instead

### Vercel
- **Issue**: Function timeout errors
- **Solution**: Optimize video processing or use Railway for longer processes

### Railway
- **Issue**: Build failures
- **Solution**: Check Python version in runtime.txt matches Railway's supported versions

### Heroku
- **Issue**: Slug size too large
- **Solution**: Add more files to .gitignore, optimize dependencies

## Performance Optimization

### Video Processing
```python
# Optimize MoviePy settings
from moviepy.config import FFMPEG_BINARY

# Use hardware acceleration if available
ffmpeg_params = ["-hwaccel", "auto"]
```

### Memory Management
```python
# Clean up temporary files
import tempfile
import shutil

def cleanup_temp_files(temp_dir):
    try:
        shutil.rmtree(temp_dir)
    except Exception as e:
        print(f"Warning: Could not clean up {temp_dir}: {e}")
```

## Security Best Practices

### Environment Variables
```bash
# Create .env file (never commit this)
SECRET_KEY=your-secret-key-here
DEEPGRAM_API_KEY=your-api-key
FLASK_ENV=production
```

### File Upload Security
```python
# Validate file types
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp3', 'wav', 'mp4'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
```

## Getting Help

1. **Check logs**: Look at server.log or console output
2. **Test locally**: Use `python start.py` to test before deploying
3. **Check platform status**: Visit status pages of deployment platforms
4. **Community support**: Check platform documentation and forums

## Quick Fixes

### Reset Everything
```bash
# Clean Python cache
find . -type d -name "__pycache__" -delete
find . -name "*.pyc" -delete

# Reinstall dependencies
pip uninstall -r requirements.txt -y
pip install -r requirements.txt

# Reset git (if needed)
git clean -fd
git reset --hard HEAD
```

### Test Deployment Locally
```bash
# Test production mode
PORT=8000 FLASK_ENV=production python gui_web.py

# Test with gunicorn
gunicorn --bind 0.0.0.0:8000 gui_web:app
```