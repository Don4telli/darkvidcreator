#!/bin/bash

# Vercel build script to ensure correct moviepy installation
echo "Installing dependencies with constraints..."
pip install --constraint constraints.txt -r requirements.txt

echo "Verifying moviepy installation..."
python -c "from moviepy.editor import AudioFileClip; print('MoviePy editor module verified!')"

echo "Build completed successfully!"