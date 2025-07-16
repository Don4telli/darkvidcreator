# ImageToVideo Creator

A simple desktop application that creates videos from a collection of images and an audio file. The images are distributed evenly across the duration of the audio to create a slideshow-style video.

## Features

- **Multi-image selection**: Select multiple images at once
- **Audio synchronization**: Automatically distributes images evenly across audio duration
- **Aspect ratio presets**: Choose from 1:1 (Square), 16:9 (Landscape), or 9:16 (Portrait)
- **Multi-video mode**: Create multiple video segments with green screen separators
- **Filename grouping**: Automatically groups images by prefix (A01, A02... B01, B02...)
- **Green screen transitions**: Customizable green screen duration between video segments
- **Progress tracking**: Real-time progress updates during video creation
- **Multiple formats**: Supports various image and audio formats
- **Cross-platform GUI**: Modern web-based interface and traditional desktop GUI

## Supported Formats

### Images
- JPG/JPEG
- PNG
- BMP
- TIFF
- WebP

### Audio
- MP3
- WAV
- AAC
- M4A
- OGG
- FLAC

## Installation

1. Make sure you have Python 3.7+ installed
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Quick Start (Recommended)

```bash
python launcher.py
```

The launcher provides an interactive menu to choose between:
1. **Web GUI** - Modern browser-based interface (recommended)
2. **Desktop GUI** - Traditional Tkinter interface
3. **CLI** - Command-line interface with interactive prompts

### Direct Interface Access

#### Web GUI (Recommended - Cross-platform)

```bash
python gui_web.py
```

This will start a web server and automatically open your browser to `http://localhost:5000`. The web interface provides:
- Drag & drop file upload
- Aspect ratio selection (1:1, 16:9, 9:16)
- Multi-video mode with green screen separators
- Real-time progress tracking
- Cross-platform compatibility
- No GUI framework dependencies

#### Desktop GUI (May have compatibility issues on macOS)

1. Run the GUI application:
   ```bash
   python main.py
   ```

2. Use the GUI to:
   - Select multiple images using the "Select Images" button
   - Choose an audio file using the "Select Audio" button
   - Specify the output path for your video
   - Click "Create Video" to start the process

3. Monitor the progress bar and wait for completion

**Note:** The Tkinter-based GUI may crash on macOS with `NSInvalidArgumentException`. Use the Web GUI or CLI instead.

### CLI Version (Recommended for automation and macOS)

1. Basic usage:
   ```bash
   python cli.py -i image1.jpg image2.png image3.jpeg -a audio.mp3 -o output.mp4
   ```

2. With aspect ratio preset:
   ```bash
   python cli.py -i *.jpg -a music.wav -o video.mp4 --aspect-ratio 16:9
   ```

3. Multi-video mode with green screen separators:
   ```bash
   python cli.py -i A*.jpg B*.jpg C*.jpg -a music.wav -o video.mp4 --multi-video --green-screen-duration 3.0
   ```

3. List supported formats:
   ```bash
   python cli.py --list-formats
   ```

4. Get help:
   ```bash
   python cli.py --help
   ```

### CLI Options

- `-i, --images`: Input image files (required)
- `-a, --audio`: Input audio file (required)
- `-o, --output`: Output video file path (required)
- `--aspect-ratio`: Video aspect ratio: 1:1, 16:9, or 9:16 (default: 9:16)
- `--width`: Video width in pixels (overrides aspect ratio)
- `--height`: Video height in pixels (overrides aspect ratio)
- `--fps`: Video frame rate (default: 30)
- `--multi-video`: Enable multi-video mode with filename grouping
- `--green-screen-duration`: Duration of green screen separators in seconds (default: 2.0)
- `--list-formats`: Show supported file formats

## How It Works

### Single Video Mode
The application calculates the duration of your audio file and divides it by the number of images to determine how long each image should be displayed. For example:

- Audio duration: 60 seconds
- Number of images: 12
- Each image displays for: 5 seconds

The final video will have the same duration as your audio file, with images transitioning smoothly throughout.

### Multi-Video Mode
When enabled, the application groups images by their filename prefix and creates separate video segments with green screen separators:

**Example with 40 images:**
- A01.jpg, A02.jpg, ..., A10.jpg (Group A - 10 images)
- B01.jpg, B02.jpg, ..., B10.jpg (Group B - 10 images) 
- C01.jpg, C02.jpg, ..., C10.jpg (Group C - 10 images)
- D01.jpg, D02.jpg, ..., D10.jpg (Group D - 10 images)

**Result:** One merged video with:
1. Group A video segment
2. Green screen separator (2 seconds)
3. Group B video segment
4. Green screen separator (2 seconds)
5. Group C video segment
6. Green screen separator (2 seconds)
7. Group D video segment

The green screen separators can be used later for video editing to mark split points. All segments use the same audio track.

## Output

The application creates an MP4 video file with:
- 30 FPS
- H.264 video codec
- AAC audio codec
- Same duration as the input audio

## Requirements

- Python 3.7+
- MoviePy
- Tkinter (usually included with Python)
- FFmpeg (automatically handled by moviepy)

## Troubleshooting

### GUI Issues
- **macOS GUI Crash**: If you encounter `NSInvalidArgumentException` or similar crashes on macOS, use the Web GUI or CLI version instead:
  
  **Web GUI (Recommended):**
  ```bash
  python gui_web.py
  ```
  
  **CLI:**
  ```bash
  python cli.py -i your_images*.jpg -a your_audio.mp3 -o output.mp4
  ```
- **Tkinter Issues**: The desktop GUI requires a properly configured Tkinter installation. Use the Web GUI or CLI as an alternative.

### General Issues
- **FFmpeg not found**: Make sure FFmpeg is installed and accessible in your PATH
- **Memory issues**: For large images or long audio files, ensure you have sufficient RAM
- **Codec errors**: The application uses H.264 video and AAC audio codecs by default
- **File format issues**: Check that your images and audio files are in supported formats
- **Permission errors**: Ensure you have write permissions to the output directory

### Testing
Run the test script to verify functionality:
```bash
python test_core.py  # Test core functionality
python test_cli.py   # Test CLI with sample files
```

### Common Issues

1. **"No module named 'moviepy'"**: Install dependencies with `pip install -r requirements.txt`
2. **Video creation fails**: Ensure all image files are valid and accessible
3. **Audio not working**: Check that the audio file format is supported
4. **FFmpeg not found**: Make sure FFmpeg is installed and accessible in your PATH
5. **Memory issues**: For large images or long audio files, ensure you have sufficient RAM
6. **Codec errors**: The application uses H.264 video and AAC audio codecs by default
7. **File format issues**: Check that your images and audio files are in supported formats
8. **Permission errors**: Ensure you have write permissions to the output directory

### Performance Tips

- Use images with similar dimensions for best results
- Larger images will take longer to process
- Keep the number of images reasonable (under 100 for best performance)

## License

This project is open source and available under the MIT License.