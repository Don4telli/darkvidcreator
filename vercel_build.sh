#!/bin/bash
set -e  # Exit on error

echo "=== Starting build process ==="

# Install FFmpeg
echo "Installing FFmpeg..."
apt-get update
apt-get install -y ffmpeg

# Verify FFmpeg installation
echo "Verifying FFmpeg installation..."
ffmpeg -version

# Create a symbolic link for libx264 if needed
if [ ! -f /usr/lib/x86_64-linux-gnu/libx264.so ] && [ -f /usr/lib/x86_64-linux-gnu/libx264.so.* ]; then
    echo "Creating libx264.so symbolic link..."
    ln -s /usr/lib/x86_64-linux-gnu/libx264.so.* /usr/lib/x86_64-linux-gnu/libx264.so
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Verify Python packages
echo "Verifying Python packages..."
pip freeze | grep -E 'moviepy|numpy|Pillow|imageio|imageio-ffmpeg'

echo "=== Build process completed successfully ==="

