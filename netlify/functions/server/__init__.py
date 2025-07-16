"""
Serverless function entry point for Netlify deployment.
This file allows the Flask app to run in a serverless environment.
"""
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import the Flask app from gui_web
from gui_web import app as application

def handler(event, context):
    """Handle the incoming request."""
    from serverless_wsgi import handle_request
    return handle_request(application, event, context)
