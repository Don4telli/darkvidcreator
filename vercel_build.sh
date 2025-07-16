#!/bin/bash
set -e  # Exit on error

# Enable debugging
set -x

echo "=== Starting build process ==="

# Install system dependencies
echo "Updating package lists..."
apt-get update -qq

# Install FFmpeg and other required system packages
echo "Installing system dependencies..."
DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1-mesa-glx

# Verify FFmpeg installation
echo "FFmpeg version:"
ffmpeg -version

# Install Python dependencies
echo "Installing Python dependencies..."
python -m pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt

# Verify Python packages
echo "=== Installed Python packages ==="
pip list | grep -E 'moviepy|numpy|Pillow|imageio|ffmpeg|flask|Werkzeug'

# Check Python version and paths
echo "\n=== Python environment ==="
python --version
which python

# Check if moviepy is importable
echo -e "\n=== Testing moviepy import ==="
python -c "
import sys
print('Python path:', sys.path)
try:
    import moviepy.editor
    print('✅ moviepy.editor imported successfully')
    print(f'moviepy version: {moviepy.__version__}')
    print(f'moviepy location: {moviepy.__file__}')
except Exception as e:
    print(f'❌ Error importing moviepy: {str(e)}')
    import traceback
    traceback.print_exc()
"

echo "=== Build process completed ==="

