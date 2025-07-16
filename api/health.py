#!/usr/bin/env python3
"""
Simple health check endpoint for Vercel deployment debugging
"""

import sys
import os
import json
from datetime import datetime

def handler(request):
    """Vercel serverless function handler"""
    try:
        # Basic environment info
        health_info = {
            'status': 'ok',
            'timestamp': datetime.now().isoformat(),
            'python_version': sys.version,
            'python_path': sys.path[:5],  # First 5 entries
            'working_directory': os.getcwd(),
            'environment_vars': {
                'PYTHON_VERSION': os.environ.get('PYTHON_VERSION', 'not_set'),
                'PIP_CONSTRAINT': os.environ.get('PIP_CONSTRAINT', 'not_set'),
                'VERCEL': os.environ.get('VERCEL', 'not_set'),
                'VERCEL_ENV': os.environ.get('VERCEL_ENV', 'not_set')
            },
            'moviepy_check': 'checking...'
        }
        
        # Try MoviePy import
        try:
            import moviepy
            health_info['moviepy_check'] = {
                'status': 'success',
                'version': getattr(moviepy, '__version__', 'unknown'),
                'location': moviepy.__file__
            }
            
            # Try editor import
            try:
                import moviepy.editor
                health_info['moviepy_editor_check'] = {
                    'status': 'success',
                    'location': moviepy.editor.__file__
                }
            except ImportError as e:
                health_info['moviepy_editor_check'] = {
                    'status': 'failed',
                    'error': str(e)
                }
                
        except ImportError as e:
            health_info['moviepy_check'] = {
                'status': 'failed',
                'error': str(e)
            }
        
        # Try VideoProcessor import
        try:
            sys.path.append('/var/task')  # Vercel task directory
            from core.video_processor import VideoProcessor
            health_info['video_processor_check'] = 'success'
        except ImportError as e:
            health_info['video_processor_check'] = f'failed: {str(e)}'
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(health_info, indent=2)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
        }