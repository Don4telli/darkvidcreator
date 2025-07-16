#!/usr/bin/env python3
"""
Web-based GUI for ImageToVideo application using Flask.
This provides a cross-platform alternative to the Tkinter GUI.
"""

import os
import sys
import threading
import webbrowser
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import tempfile
import shutil
from pathlib import Path
import subprocess

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.video_processor import VideoProcessor
from core.tiktok_transcription import transcribe_tiktok_video

app = Flask(__name__)
# Enable CORS for all routes
CORS(app, resources={
    r"/*": {
        "origins": ["*"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size

# Global variables for progress tracking
progress_data = {}
transcription_results = {}  # Global storage for transcription results
video_processor = VideoProcessor()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    try:
        # Create temporary directory for this session
        temp_dir = tempfile.mkdtemp()
        
        # Handle image files
        image_files = request.files.getlist('images')
        if not image_files or len(image_files) == 0:
            return jsonify({'error': 'No image files provided'}), 400
        
        image_paths = []
        for i, file in enumerate(image_files):
            if file.filename == '':
                continue
            filename = secure_filename(f"image_{i:03d}_{file.filename}")
            filepath = os.path.join(temp_dir, filename)
            file.save(filepath)
            image_paths.append(filepath)
        
        if len(image_paths) == 0:
            return jsonify({'error': 'No valid image files uploaded'}), 400
        
        # Handle audio file (optional)
        audio_path = None
        audio_file = request.files.get('audio')
        if audio_file and audio_file.filename != '':
            audio_filename = secure_filename(f"audio_{audio_file.filename}")
            audio_path = os.path.join(temp_dir, audio_filename)
            audio_file.save(audio_path)
        
        # Get video settings
        width = int(request.form.get('width', 1920))
        height = int(request.form.get('height', 1080))
        fps = int(request.form.get('fps', 30))
        
        # Output path
        output_filename = secure_filename(request.form.get('output_name', 'output.mp4'))
        if not output_filename.endswith('.mp4'):
            output_filename += '.mp4'
        output_path = os.path.join(temp_dir, output_filename)
        
        # Store paths in session data
        session_data = {
            'temp_dir': temp_dir,
            'image_paths': image_paths,
            'audio_path': audio_path,
            'output_path': output_path,
            'width': width,
            'height': height,
            'fps': fps
        }
        
        return jsonify({
            'success': True,
            'session_id': os.path.basename(temp_dir),
            'image_count': len(image_paths),
            'has_audio': audio_path is not None,
            'settings': {'width': width, 'height': height, 'fps': fps}
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/create_video', methods=['POST'])
def create_video():
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({'error': 'No session ID provided'}), 400
        
        # Reconstruct session data (in a real app, you'd store this in a database or session)
        temp_dir = os.path.join(tempfile.gettempdir(), session_id)
        if not os.path.exists(temp_dir):
            return jsonify({'error': 'Session expired or invalid'}), 400
        
        # Find files in temp directory
        image_files = sorted([f for f in os.listdir(temp_dir) if f.startswith('image_')])
        audio_files = [f for f in os.listdir(temp_dir) if f.startswith('audio_')]
        
        image_paths = [os.path.join(temp_dir, f) for f in image_files]
        audio_path = os.path.join(temp_dir, audio_files[0]) if audio_files else None
        output_path = os.path.join(temp_dir, 'output.mp4')
        
        # Get video settings
        aspect_ratio = data.get('aspect_ratio', '9:16')
        fps = data.get('fps', 30)
        multi_video_mode = data.get('multi_video_mode', True)  # Always True by default
        green_screen_duration = data.get('green_screen_duration', 5.0)  # Default 5 seconds
        
        # Debug logging
        print(f"DEBUG: Received request data: {data}")
        print(f"DEBUG: multi_video_mode = {multi_video_mode}")
        print(f"DEBUG: green_screen_duration = {green_screen_duration}")
        print(f"DEBUG: Found {len(image_paths)} images")
        if image_paths:
            print(f"DEBUG: First few image names: {[os.path.basename(p) for p in image_paths[:5]]}")
        
        # Reset progress
        key = f"{session_id}_create"
        progress_data[key] = {'progress': 0, 'message': 'Starting video creation...'}
        
        def progress_callback(message, progress=None):
            if progress is not None:
                progress_data[key]['progress'] = progress
            progress_data[key]['message'] = message
        
        # Create video in a separate thread
        def create_video_thread():
            try:
                if multi_video_mode:
                    video_processor.create_multi_video_with_separators(
                        image_paths=image_paths,
                        audio_path=audio_path,
                        output_path=output_path,
                        aspect_ratio=aspect_ratio,
                        fps=fps,
                        green_screen_duration=green_screen_duration,
                        progress_callback=progress_callback
                    )
                else:
                    # Get dimensions from aspect ratio for single video mode
                    width, height = video_processor.get_aspect_ratio_dimensions(aspect_ratio)
                    video_processor.create_video_from_images(
                        image_paths=image_paths,
                        audio_path=audio_path,
                        output_path=output_path,
                        width=width,
                        height=height,
                        fps=fps,
                        progress_callback=progress_callback
                    )
                progress_data[key]['progress'] = 100
                progress_data[key]['message'] = 'Video creation completed!'
            except Exception as e:
                import traceback
                tb_str = traceback.format_exc()
                error_message = f'Error: {str(e)}\nTraceback:\n{tb_str}'
                progress_data[key]['message'] = error_message
                app.logger.error(error_message)
        
        thread = threading.Thread(target=create_video_thread)
        thread.start()
        
        return jsonify({'success': True, 'message': 'Video creation started'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/progress')
def get_progress():
    session_id = request.args.get('session_id')
    task_type = request.args.get('type', 'create') # Default to 'create'
    if not session_id:
        return jsonify({'error': 'Session ID required'}), 400

    key = f"{session_id}_{task_type}"
    return jsonify(progress_data.get(key, {'progress': 0, 'message': 'Waiting...'}))

@app.route('/download/<session_id>')
def download_video(session_id):
    try:
        temp_dir = os.path.join(tempfile.gettempdir(), session_id)
        output_path = os.path.join(temp_dir, 'output.mp4')
        
        if not os.path.exists(output_path):
            return jsonify({'error': 'Video file not found'}), 404
        
        return send_file(output_path, as_attachment=True, download_name='video_output.mp4')
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/upload_video', methods=['POST'])
def upload_video():
    try:
        # Create temporary directory for this session
        temp_dir = tempfile.mkdtemp()
        
        # Handle video file
        video_file = request.files.get('video')
        if not video_file or video_file.filename == '':
            return jsonify({'error': 'No video file provided'}), 400
        
        # Save video file
        video_filename = secure_filename(f"input_{video_file.filename}")
        video_path = os.path.join(temp_dir, video_filename)
        video_file.save(video_path)
        
        # Get settings
        green_threshold = float(request.form.get('green_threshold', 0.8))
        
        # Store session data
        session_data = {
            'temp_dir': temp_dir,
            'video_path': video_path,
            'green_threshold': green_threshold
        }
        
        return jsonify({
            'success': True,
            'session_id': os.path.basename(temp_dir),
            'video_name': video_file.filename,
            'settings': {'green_threshold': green_threshold}
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/transcribe_tiktok', methods=['POST'])
def transcribe_tiktok():
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'No TikTok URL provided'}), 400
        
        # Create session for this transcription
        temp_dir = tempfile.mkdtemp()
        session_id = os.path.basename(temp_dir)
        
        # Reset progress
        key = f"{session_id}_transcribe"
        progress_data[key] = {'progress': 0, 'message': 'Starting TikTok transcription...'}
        
        def progress_callback(message, progress=None):
            if progress is not None:
                progress_data[key]['progress'] = progress
            progress_data[key]['message'] = message
        
        # Transcribe in a separate thread
        def transcribe_thread():
            try:
                result = transcribe_tiktok_video(url, progress_callback)
                transcription_results[session_id] = result
                
                if result['success']:
                    progress_data[key]['progress'] = 100
                    progress_data[key]['message'] = 'Transcription completed successfully!'
                else:
                    progress_data[key]['message'] = f'Transcription failed: {result.get("error", "Unknown error")}'
                    
            except Exception as e:
                import traceback
                tb_str = traceback.format_exc()
                error_message = f'Error: {str(e)}\nTraceback\n{tb_str}'
                progress_data[key]['message'] = error_message
                transcription_results[session_id] = {'success': False, 'error': error_message}
                app.logger.error(error_message)
        
        thread = threading.Thread(target=transcribe_thread)
        thread.start()
        
        return jsonify({'success': True, 'session_id': session_id, 'message': 'Transcription started'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_transcription/<session_id>')
def get_transcription(session_id):
    try:
        # Check if transcription results exist
        if session_id not in transcription_results:
            return jsonify({'error': 'Transcription not found or still in progress'}), 404
        
        result = transcription_results[session_id]
        
        if result['success']:
            return jsonify({
                'success': True,
                'text': result['text'],
                'session_id': session_id,
                'url': result.get('url', '')
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Unknown error'),
                'session_id': session_id
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/debug')
def debug_info():
    """Debug endpoint to check environment and dependencies."""
    try:
        debug_data = {
            'python_version': sys.version,
            'python_path': sys.path,
            'current_directory': os.getcwd(),
            'environment_variables': dict(os.environ),
            'installed_packages': [],
            'ffmpeg_check': None,
            'file_structure': {}
        }
        
        # Check installed packages
        try:
            result = subprocess.run([sys.executable, '-m', 'pip', 'list'], 
                                  capture_output=True, text=True, timeout=30)
            debug_data['installed_packages'] = result.stdout.split('\n')
        except Exception as e:
            debug_data['installed_packages'] = f'Error getting packages: {str(e)}'
        
        # Check FFmpeg
        try:
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True, timeout=10)
            debug_data['ffmpeg_check'] = 'FFmpeg available'
        except Exception as e:
            debug_data['ffmpeg_check'] = f'FFmpeg not available: {str(e)}'
        
        # Check file structure
        try:
            current_dir = os.getcwd()
            for root, dirs, files in os.walk(current_dir):
                # Limit depth to avoid too much data
                level = root.replace(current_dir, '').count(os.sep)
                if level < 3:
                    rel_path = os.path.relpath(root, current_dir)
                    debug_data['file_structure'][rel_path] = {
                        'dirs': dirs[:10],  # Limit to first 10
                        'files': files[:10]  # Limit to first 10
                    }
        except Exception as e:
            debug_data['file_structure'] = f'Error reading file structure: {str(e)}'
        
        return jsonify(debug_data)
        
    except Exception as e:
         return jsonify({'error': f'Debug endpoint error: {str(e)}'}), 500

@app.route('/debug/moviepy')
def debug_moviepy():
    """Comprehensive MoviePy and FFmpeg test endpoint."""
    import traceback
    import json
    from io import BytesIO
    import numpy as np
    from PIL import Image
    import subprocess
    import platform
    import sys
    import pkg_resources
    
    def get_system_info():
        """Collect system and environment information."""
        return {
            'platform': platform.platform(),
            'python_version': sys.version,
            'executable': sys.executable,
            'path': sys.path,
            'environment': {k: v for k, v in os.environ.items() 
                          if k in ('PATH', 'LD_LIBRARY_PATH', 'PYTHONPATH', 'VERCEL')},
            'installed_packages': sorted([f"{p.project_name}=={p.version}" 
                                      for p in pkg_resources.working_set])
        }
    
    def test_ffmpeg():
        """Test FFmpeg installation and functionality."""
        result = {'status': 'not_tested'}
        try:
            # Check if ffmpeg is in PATH
            ffmpeg_path = subprocess.check_output(['which', 'ffmpeg'], 
                                               stderr=subprocess.STDOUT).decode().strip()
            result['path'] = ffmpeg_path
            
            # Get version
            version_output = subprocess.check_output(
                ['ffmpeg', '-version'], 
                stderr=subprocess.STDOUT
            ).decode('utf-8', errors='replace')
            
            result['version'] = version_output.split('\n')[0]
            
            # Check codecs
            codec_output = subprocess.check_output(
                ['ffmpeg', '-codecs'], 
                stderr=subprocess.STDOUT
            ).decode('utf-8', errors='replace')
            
            result['codecs'] = {
                'libx264': 'libx264' in codec_output,
                'aac': 'aac' in codec_output,
                'libmp3lame': 'libmp3lame' in codec_output
            }
            
            # Test simple conversion
            test_input = os.path.join(os.path.dirname(__file__), '..', 'test', 'test_input.txt')
            test_output = os.path.join(os.path.dirname(__file__), '..', 'test', 'test_output.mp4')
            
            # Create test input
            os.makedirs(os.path.dirname(test_input), exist_ok=True)
            with open(test_input, 'w') as f:
                f.write("file 'test_input.txt'\nduration 1\nfile 'test_input.txt'")
            
            ffmpeg_cmd = [
                'ffmpeg',
                '-f', 'lavfi',
                '-i', 'testsrc=duration=1:size=320x240:rate=30',
                '-c:v', 'libx264',
                '-pix_fmt', 'yuv420p',
                '-y',  # Overwrite output file
                test_output
            ]
            
            try:
                subprocess.run(
                    ffmpeg_cmd,
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=10
                )
                result['test_video_creation'] = 'success'
                if os.path.exists(test_output):
                    result['test_video_size'] = f"{os.path.getsize(test_output) / 1024:.1f} KB"
                    os.remove(test_output)
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
                result['test_video_creation'] = f'failed: {str(e)}'
                if hasattr(e, 'stderr') and e.stderr:
                    result['ffmpeg_error'] = e.stderr.decode('utf-8', errors='replace')
            
            result['status'] = 'success'
            
        except subprocess.CalledProcessError as e:
            result['status'] = f'error: {str(e)}'
            if hasattr(e, 'output') and e.output:
                result['error_output'] = e.output.decode('utf-8', errors='replace')
        except Exception as e:
            result['status'] = f'unexpected error: {str(e)}'
            
        return result
    
    def test_moviepy():
        """Test MoviePy functionality."""
        result = {'status': 'not_tested'}
        
        try:
            # Import moviepy
            import moviepy
            result['version'] = getattr(moviepy, '__version__', 'unknown')
            
            # Test basic imports
            from moviepy.editor import VideoFileClip, AudioFileClip, ImageClip, ColorClip, concatenate_videoclips
            result['imports'] = 'success'
            
            # Create test directory
            test_dir = os.path.join(os.path.dirname(__file__), '..', 'test')
            os.makedirs(test_dir, exist_ok=True)
            
            # Test 1: Create and save a simple color clip
            try:
                clip = ColorClip((320, 240), color=(255, 0, 0), duration=1)
                test_video = os.path.join(test_dir, 'test_color.mp4')
                clip.write_videofile(
                    test_video, 
                    fps=24, 
                    codec='libx264',
                    audio_codec='aac',
                    logger=None
                )
                result['color_clip'] = 'success'
                if os.path.exists(test_video):
                    result['color_clip_size'] = f"{os.path.getsize(test_video) / 1024:.1f} KB"
                    os.remove(test_video)
            except Exception as e:
                result['color_clip'] = f'error: {str(e)}'
            
            # Test 2: Create and save an audio clip
            try:
                audio = AudioClip(
                    lambda t: [np.sin(440 * 2 * np.pi * t)],
                    duration=1,
                    fps=44100
                )
                test_audio = os.path.join(test_dir, 'test_audio.mp3')
                audio.write_audiofile(
                    test_audio,
                    codec='libmp3lame',
                    bitrate='128k',
                    logger=None
                )
                result['audio_clip'] = 'success'
                if os.path.exists(test_audio):
                    result['audio_clip_size'] = f"{os.path.getsize(test_audio) / 1024:.1f} KB"
                    os.remove(test_audio)
            except Exception as e:
                result['audio_clip'] = f'error: {str(e)}'
            
            # Test 3: Create and save an image clip
            try:
                img = Image.new('RGB', (320, 240), color='green')
                img_byte_arr = BytesIO()
                img.save(img_byte_arr, format='PNG')
                img_byte_arr = img_byte_arr.getvalue()
                
                image_clip = ImageClip(img_byte_arr).set_duration(1)
                test_image_video = os.path.join(test_dir, 'test_image.mp4')
                image_clip.write_videofile(
                    test_image_video,
                    fps=24,
                    codec='libx264',
                    audio_codec='aac',
                    logger=None
                )
                result['image_clip'] = 'success'
                if os.path.exists(test_image_video):
                    result['image_clip_size'] = f"{os.path.getsize(test_image_video) / 1024:.1f} KB"
                    os.remove(test_image_video)
            except Exception as e:
                result['image_clip'] = f'error: {str(e)}'
            
            result['status'] = 'success'
            
        except ImportError as e:
            result['status'] = f'import error: {str(e)}'
            result['traceback'] = traceback.format_exc()
        except Exception as e:
            result['status'] = f'unexpected error: {str(e)}'
            result['traceback'] = traceback.format_exc()
            
        return result
    
    # Main test execution
    try:
        results = {
            'system': get_system_info(),
            'ffmpeg': test_ffmpeg(),
            'moviepy': test_moviepy(),
            'timestamp': datetime.datetime.utcnow().isoformat(),
            'status': 'complete'
        }
        
        # Clean up test directory
        test_dir = os.path.join(os.path.dirname(__file__), '..', 'test')
        if os.path.exists(test_dir):
            for f in os.listdir(test_dir):
                try:
                    os.remove(os.path.join(test_dir, f))
                except:
                    pass
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({'error': f'MoviePy debug error: {str(e)}'}), 500

@app.route('/api/debug-public')
def debug_public():
    """Public debug endpoint that bypasses authentication."""
    try:
        debug_info = {
            'timestamp': datetime.now().isoformat(),
            'python_version': sys.version,
            'working_directory': os.getcwd(),
            'moviepy_status': 'checking...',
            'video_processor_status': 'checking...'
        }
        
        # Check MoviePy
        try:
            import moviepy
            debug_info['moviepy_status'] = f'SUCCESS - version {getattr(moviepy, "__version__", "unknown")}'
            
            # Try editor import
            try:
                import moviepy.editor
                debug_info['moviepy_editor_status'] = 'SUCCESS - editor module available'
            except ImportError as e:
                debug_info['moviepy_editor_status'] = f'FAILED - {str(e)}'
                
        except ImportError as e:
            debug_info['moviepy_status'] = f'FAILED - {str(e)}'
        
        # Check VideoProcessor
        try:
            from core.video_processor import VideoProcessor
            debug_info['video_processor_status'] = 'SUCCESS - VideoProcessor imported'
        except ImportError as e:
            debug_info['video_processor_status'] = f'FAILED - {str(e)}'
        
        return jsonify(debug_info)
        
    except Exception as e:
        return jsonify({'error': f'Debug error: {str(e)}', 'timestamp': datetime.now().isoformat()}), 500
 

def find_free_port(start_port=5001):
    """Find a free port starting from start_port."""
    import socket
    for port in range(start_port, start_port + 100):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    return None

def main():
    """Main function to run the web GUI."""
    print("ImageToVideo Web GUI")
    print("====================")
    
    # Find available port (avoid 5000 which is used by macOS AirPlay)
    port = find_free_port(5001)
    if not port:
        print("❌ Error: Could not find an available port.")
        return
    
    print(f"\n🌐 Starting web server on http://localhost:{port}")
    print("The web interface will open automatically in your browser.")
    print("Press Ctrl+C to stop the server.\n")
    
    # Open browser after a short delay
    def open_browser():
        import time
        time.sleep(1.5)
        webbrowser.open(f'http://localhost:{port}')
    
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Run the Flask app
    try:
        app.run(host='localhost', port=port, debug=False)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        print("💡 Try running with a different port or check if another service is using the port.")

if __name__ == '__main__':
    # Check if running in production (cloud deployment)
    if os.environ.get('PORT'):
        # Production mode - use environment variables
        port = int(os.environ.get('PORT', 5000))
        debug = os.environ.get('FLASK_ENV') != 'production'
        print(f"🚀 Starting in production mode on port {port}")
        app.run(host='0.0.0.0', port=port, debug=debug)
    else:
        # Development mode - use local setup
        main()