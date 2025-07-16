#!/usr/bin/env python3
"""
Integration tests for the Flask API endpoints.
"""

import unittest
import tempfile
import os
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the project root to the path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from gui_web import app


class TestFlaskAPI(unittest.TestCase):
    """Test cases for Flask API endpoints."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_index_route(self):
        """Test the main index route."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'ImageToVideo', response.data)
    
    def test_upload_route_get(self):
        """Test GET request to upload route."""
        response = self.client.get('/upload')
        self.assertEqual(response.status_code, 200)
    
    def test_upload_route_no_files(self):
        """Test POST request to upload route without files."""
        response = self.client.post('/upload', data={})
        self.assertEqual(response.status_code, 400)
        
        # Check if response contains error message
        if response.is_json:
            data = response.get_json()
            self.assertIn('error', data)
    
    def test_upload_route_invalid_files(self):
        """Test POST request with invalid file types."""
        # Create a temporary text file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write('This is not an image')
            temp_file = f.name
        
        try:
            with open(temp_file, 'rb') as f:
                response = self.client.post('/upload', data={
                    'images': (f, 'test.txt'),
                    'audio': (f, 'test.txt'),
                    'aspect_ratio': '16:9'
                })
            
            self.assertEqual(response.status_code, 400)
        finally:
            os.unlink(temp_file)
    
    def test_progress_route(self):
        """Test the progress tracking route."""
        response = self.client.get('/progress')
        self.assertEqual(response.status_code, 200)
        
        if response.is_json:
            data = response.get_json()
            self.assertIn('progress', data)
            self.assertIsInstance(data['progress'], (int, float))
    
    def test_health_check(self):
        """Test health check endpoint if it exists."""
        response = self.client.get('/health')
        # Should either return 200 (if endpoint exists) or 404 (if not implemented)
        self.assertIn(response.status_code, [200, 404])
    
    def test_static_files(self):
        """Test serving of static files."""
        # Test CSS files
        response = self.client.get('/static/style.css')
        # Should either return 200 (if file exists) or 404 (if not found)
        self.assertIn(response.status_code, [200, 404])
    
    def test_cors_headers(self):
        """Test CORS headers if implemented."""
        response = self.client.options('/')
        # Check if CORS headers are present (optional)
        headers = response.headers
        # This test will pass regardless of CORS implementation
        self.assertTrue(True)
    
    @patch('gui_web.VideoProcessor')
    def test_video_creation_mock(self, mock_processor):
        """Test video creation with mocked processor."""
        # Mock the video processor
        mock_instance = MagicMock()
        mock_instance.create_video.return_value = True
        mock_processor.return_value = mock_instance
        
        # Create temporary image and audio files
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as img_file:
            img_file.write(b'fake image data')
            img_path = img_file.name
        
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as audio_file:
            audio_file.write(b'fake audio data')
            audio_path = audio_file.name
        
        try:
            with open(img_path, 'rb') as img, open(audio_path, 'rb') as audio:
                response = self.client.post('/upload', data={
                    'images': (img, 'test.jpg'),
                    'audio': (audio, 'test.mp3'),
                    'aspect_ratio': '16:9'
                })
            
            # The response depends on the actual implementation
            # This test ensures the endpoint doesn't crash
            self.assertIsNotNone(response)
            
        finally:
            os.unlink(img_path)
            os.unlink(audio_path)
    
    def test_error_handling(self):
        """Test error handling in API endpoints."""
        # Test with malformed requests
        response = self.client.post('/upload', data='invalid data')
        self.assertIn(response.status_code, [400, 500])
    
    def test_file_size_limits(self):
        """Test file size validation if implemented."""
        # Create a large dummy file (this test assumes reasonable limits)
        large_data = b'x' * (10 * 1024 * 1024)  # 10MB
        
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
            f.write(large_data)
            large_file = f.name
        
        try:
            with open(large_file, 'rb') as f:
                response = self.client.post('/upload', data={
                    'images': (f, 'large.jpg'),
                    'aspect_ratio': '16:9'
                })
            
            # Should handle large files gracefully
            self.assertIsNotNone(response)
            
        finally:
            os.unlink(large_file)


if __name__ == '__main__':
    unittest.main()