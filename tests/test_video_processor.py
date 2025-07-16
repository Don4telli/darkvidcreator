#!/usr/bin/env python3
"""
Unit tests for the video processor module.
"""

import unittest
import tempfile
import os
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add the project root to the path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.video_processor import VideoProcessor


class TestVideoProcessor(unittest.TestCase):
    """Test cases for VideoProcessor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.processor = VideoProcessor()
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up temporary files
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_init(self):
        """Test VideoProcessor initialization."""
        self.assertIsInstance(self.processor, VideoProcessor)
        self.assertEqual(self.processor.fps, 30)
        self.assertEqual(self.processor.aspect_ratio, (9, 16))
    
    def test_validate_image_files(self):
        """Test image file validation."""
        # Test with valid extensions
        valid_files = ['test.jpg', 'test.png', 'test.jpeg', 'test.bmp']
        for file in valid_files:
            self.assertTrue(self.processor._is_valid_image(file))
        
        # Test with invalid extensions
        invalid_files = ['test.txt', 'test.mp4', 'test.doc']
        for file in invalid_files:
            self.assertFalse(self.processor._is_valid_image(file))
    
    def test_validate_audio_files(self):
        """Test audio file validation."""
        # Test with valid extensions
        valid_files = ['test.mp3', 'test.wav', 'test.aac', 'test.m4a']
        for file in valid_files:
            self.assertTrue(self.processor._is_valid_audio(file))
        
        # Test with invalid extensions
        invalid_files = ['test.txt', 'test.mp4', 'test.doc']
        for file in invalid_files:
            self.assertFalse(self.processor._is_valid_audio(file))
    
    def test_calculate_image_duration(self):
        """Test image duration calculation."""
        # Test with 60 second audio and 12 images
        duration = self.processor._calculate_image_duration(60.0, 12)
        self.assertEqual(duration, 5.0)
        
        # Test with edge cases
        duration = self.processor._calculate_image_duration(30.0, 1)
        self.assertEqual(duration, 30.0)
        
        # Test with zero images (should not crash)
        with self.assertRaises(ValueError):
            self.processor._calculate_image_duration(60.0, 0)
    
    def test_aspect_ratio_calculation(self):
        """Test aspect ratio calculations."""
        # Test standard aspect ratios
        width, height = self.processor._calculate_dimensions('16:9', None, None)
        self.assertEqual(width / height, 16 / 9)
        
        width, height = self.processor._calculate_dimensions('1:1', None, None)
        self.assertEqual(width, height)
        
        width, height = self.processor._calculate_dimensions('9:16', None, None)
        self.assertEqual(height / width, 16 / 9)
    
    def test_group_images_by_prefix(self):
        """Test image grouping by filename prefix."""
        image_files = [
            'A01.jpg', 'A02.jpg', 'A03.jpg',
            'B01.jpg', 'B02.jpg',
            'C01.jpg', 'C02.jpg', 'C03.jpg', 'C04.jpg'
        ]
        
        groups = self.processor._group_images_by_prefix(image_files)
        
        self.assertEqual(len(groups), 3)
        self.assertIn('A', groups)
        self.assertIn('B', groups)
        self.assertIn('C', groups)
        self.assertEqual(len(groups['A']), 3)
        self.assertEqual(len(groups['B']), 2)
        self.assertEqual(len(groups['C']), 4)
    
    @patch('core.video_processor.AudioFileClip')
    def test_get_audio_duration(self, mock_audio):
        """Test audio duration retrieval."""
        # Mock audio file with 60 second duration
        mock_audio_instance = MagicMock()
        mock_audio_instance.duration = 60.0
        mock_audio.return_value = mock_audio_instance
        
        duration = self.processor._get_audio_duration('test.mp3')
        self.assertEqual(duration, 60.0)
        mock_audio.assert_called_once_with('test.mp3')
    
    def test_validate_inputs(self):
        """Test input validation."""
        # Test with empty lists
        with self.assertRaises(ValueError):
            self.processor._validate_inputs([], 'audio.mp3', 'output.mp4')
        
        # Test with non-existent audio file
        with self.assertRaises(FileNotFoundError):
            self.processor._validate_inputs(['image.jpg'], 'nonexistent.mp3', 'output.mp4')
    
    def test_error_handling(self):
        """Test error handling in video processing."""
        # Test with invalid parameters
        with self.assertRaises(ValueError):
            self.processor.create_video(
                image_files=[],
                audio_file='test.mp3',
                output_path='output.mp4'
            )


if __name__ == '__main__':
    unittest.main()