#!/usr/bin/env python3
"""
Netlify Function entry point for the DarkVidCreator Flask application.
This file serves as the serverless function handler.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    # Import the Flask app
    from gui_web import app
    
    # Import serverless WSGI handler
    from serverless_wsgi import handle_request
    
    def handler(event, context):
        """Netlify Function handler."""
        return handle_request(app, event, context)
        
except ImportError as e:
    print(f"Import error: {e}")
    
    def handler(event, context):
        """Fallback handler for import errors."""
        return {
            'statusCode': 500,
            'body': f'Import error: {str(e)}'
        }