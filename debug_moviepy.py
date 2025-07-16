#!/usr/bin/env python3
"""
Debug script to check MoviePy installation in Vercel environment
"""

import sys
import os
import subprocess

def check_moviepy_installation():
    print("=== Python Environment Debug ===")
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"Python path: {sys.path}")
    
    print("\n=== Installed Packages ===")
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', 'list'], 
                              capture_output=True, text=True)
        print(result.stdout)
    except Exception as e:
        print(f"Error getting pip list: {e}")
    
    print("\n=== MoviePy Installation Check ===")
    try:
        import moviepy
        print(f"MoviePy version: {moviepy.__version__}")
        print(f"MoviePy location: {moviepy.__file__}")
        print(f"MoviePy directory contents: {os.listdir(os.path.dirname(moviepy.__file__))}")
    except ImportError as e:
        print(f"MoviePy import error: {e}")
        return
    
    print("\n=== MoviePy Editor Module Check ===")
    try:
        import moviepy.editor
        print("SUCCESS: moviepy.editor imported successfully")
        print(f"Editor module location: {moviepy.editor.__file__}")
    except ImportError as e:
        print(f"FAILED: moviepy.editor import error: {e}")
        
        # Check what's available in moviepy
        try:
            moviepy_dir = os.path.dirname(moviepy.__file__)
            print(f"\nMoviePy directory structure:")
            for root, dirs, files in os.walk(moviepy_dir):
                level = root.replace(moviepy_dir, '').count(os.sep)
                indent = ' ' * 2 * level
                print(f"{indent}{os.path.basename(root)}/")
                subindent = ' ' * 2 * (level + 1)
                for file in files:
                    if file.endswith('.py'):
                        print(f"{subindent}{file}")
        except Exception as e:
            print(f"Error exploring moviepy directory: {e}")
    
    print("\n=== Alternative Import Check ===")
    try:
        from moviepy import VideoFileClip, AudioFileClip
        print("SUCCESS: Direct imports from moviepy work")
    except ImportError as e:
        print(f"FAILED: Direct imports from moviepy: {e}")

if __name__ == "__main__":
    check_moviepy_installation()