#!/usr/bin/env python3
"""
Quick start script for ImageToVideo Creator
Provides easy access to different modes of operation
"""

import os
import sys
import subprocess
import webbrowser
import time
import threading
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import flask
        import moviepy
        import numpy
        import PIL
        print("✅ All dependencies found")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("\n📦 Installing dependencies...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            print("Please run: pip install -r requirements.txt")
            return False

def start_web_gui():
    """Start the web GUI."""
    print("\n🌐 Starting Web GUI...")
    print("The web interface will open in your browser automatically.")
    print("Press Ctrl+C to stop the server.\n")
    
    try:
        subprocess.run([sys.executable, "gui_web.py"])
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except FileNotFoundError:
        print("❌ gui_web.py not found")

def start_production_mode():
    """Start in production mode for testing deployment."""
    print("\n🚀 Starting in Production Mode...")
    print("This simulates how the app will run when deployed.")
    print("Access at: http://localhost:8000")
    print("Press Ctrl+C to stop.\n")
    
    # Set production environment variables
    env = os.environ.copy()
    env['PORT'] = '8000'
    env['FLASK_ENV'] = 'production'
    
    try:
        subprocess.run([sys.executable, "gui_web.py"], env=env)
    except KeyboardInterrupt:
        print("\n👋 Production server stopped")
    except FileNotFoundError:
        print("❌ gui_web.py not found")

def test_with_gunicorn():
    """Test with Gunicorn (production server)."""
    print("\n🔧 Testing with Gunicorn...")
    print("This tests the exact setup used in deployment.")
    print("Access at: http://localhost:8000")
    print("Press Ctrl+C to stop.\n")
    
    try:
        # Check if gunicorn is installed
        subprocess.check_call([sys.executable, "-c", "import gunicorn"])
    except (subprocess.CalledProcessError, ImportError):
        print("Installing gunicorn...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "gunicorn"])
    
    try:
        subprocess.run([
            sys.executable, "-m", "gunicorn", 
            "--bind", "0.0.0.0:8000",
            "--workers", "1",
            "--threads", "8",
            "--timeout", "300",
            "gui_web:app"
        ])
    except KeyboardInterrupt:
        print("\n👋 Gunicorn server stopped")
    except FileNotFoundError:
        print("❌ Could not start gunicorn")

def run_deployment_helper():
    """Run the deployment helper script."""
    print("\n🚀 Starting Deployment Helper...")
    try:
        subprocess.run([sys.executable, "deploy.py"])
    except FileNotFoundError:
        print("❌ deploy.py not found")
    except KeyboardInterrupt:
        print("\n👋 Deployment helper stopped")

def show_system_info():
    """Show system information."""
    print("\n💻 System Information")
    print("=" * 25)
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    print(f"Working directory: {os.getcwd()}")
    
    # Check for required files
    required_files = ['gui_web.py', 'requirements.txt', 'core/', 'templates/']
    print("\n📁 Required files:")
    for file in required_files:
        path = Path(file)
        status = "✅" if path.exists() else "❌"
        print(f"   {status} {file}")
    
    # Check Python packages
    print("\n📦 Key dependencies:")
    packages = ['flask', 'moviepy', 'numpy', 'PIL', 'cv2']
    for package in packages:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package}")

def run_code_quality_checks():
    """Run code quality and security checks."""
    print("\n🔍 Running Code Quality Checks...")
    
    checks = [
        ("flake8 --max-line-length=88 .", "Code style (flake8)"),
        ("black --check .", "Code formatting (black)"),
        ("bandit -r . -f json", "Security scan (bandit)"),
        ("mypy .", "Type checking (mypy)")
    ]
    
    for command, description in checks:
        print(f"\n📋 {description}...")
        try:
            result = subprocess.run(command.split(), capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {description} passed")
            else:
                print(f"⚠️  {description} found issues:")
                print(result.stdout)
                if result.stderr:
                    print(result.stderr)
        except FileNotFoundError:
            print(f"❌ Tool not installed. Install with: pip install {command.split()[0]}")
        except Exception as e:
            print(f"❌ Error running {description}: {e}")

def view_documentation():
    """View available documentation files."""
    print("\n📚 Available Documentation:")
    print("=" * 40)
    print("1. 📖 README.md - Main documentation")
    print("2. 🚀 DEPLOYMENT.md - Deployment guide")
    print("3. 🔧 TROUBLESHOOTING.md - Common issues")
    print("4. 💎 CODE_QUALITY.md - Code quality guide")
    print("0. ⬅️  Back to main menu")
    
    while True:
        choice = input("\nSelect documentation to view (0-4): ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            open_file_in_editor("README.md")
        elif choice == "2":
            open_file_in_editor("DEPLOYMENT.md")
        elif choice == "3":
            open_file_in_editor("TROUBLESHOOTING.md")
        elif choice == "4":
            open_file_in_editor("CODE_QUALITY.md")
        else:
            print("❌ Invalid choice. Please select 0-4.")

def open_file_in_editor(filename):
    """Open file in default editor."""
    try:
        if os.path.exists(filename):
            if sys.platform == "darwin":  # macOS
                subprocess.run(["open", filename])
            elif sys.platform == "linux":
                subprocess.run(["xdg-open", filename])
            elif sys.platform == "win32":
                subprocess.run(["start", filename], shell=True)
            print(f"📖 Opened {filename} in default editor")
        else:
            print(f"❌ File {filename} not found")
    except Exception as e:
        print(f"❌ Error opening {filename}: {e}")

def show_menu():
    """Show the main menu."""
    print("\n🎬 ImageToVideo Creator - Quick Start")
    print("=" * 40)
    print("1. 🌐 Start Web GUI (Development)")
    print("2. 🚀 Start Production Mode (Testing)")
    print("3. 🔧 Test with Gunicorn")
    print("4. 📤 Deployment Helper")
    print("5. 🔍 Run Code Quality Checks")
    print("6. 💻 System Information")
    print("7. 📚 View Documentation")
    print("8. 🚪 Exit")
    print("=" * 40)

def open_documentation():
    """Open documentation files."""
    print("\n📖 Opening Documentation...")
    
    docs = {
        'README.md': 'Main documentation',
        'DEPLOYMENT.md': 'Deployment guide'
    }
    
    for doc, description in docs.items():
        if Path(doc).exists():
            print(f"✅ {description}: {doc}")
            try:
                if sys.platform == 'darwin':  # macOS
                    subprocess.run(['open', doc])
                elif sys.platform == 'win32':  # Windows
                    subprocess.run(['start', doc], shell=True)
                else:  # Linux
                    subprocess.run(['xdg-open', doc])
            except:
                print(f"   Could not open {doc} automatically")
        else:
            print(f"❌ {description}: {doc} (not found)")

def main():
    """Main function."""
    print("🎬 ImageToVideo Creator")
    print("Welcome to the quick start helper!")
    
    # Check if we're in the right directory
    if not Path('gui_web.py').exists():
        print("❌ Error: gui_web.py not found")
        print("Please run this script from the ImageToVideo directory")
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    while True:
        show_menu()
        choice = input("\nSelect an option (1-8): ").strip()
        
        if choice == '1':
            start_web_gui()
        elif choice == '2':
            start_production_mode()
        elif choice == '3':
            test_with_gunicorn()
        elif choice == '4':
            run_deployment_helper()
        elif choice == '5':
            run_code_quality_checks()
        elif choice == '6':
            show_system_info()
        elif choice == '7':
            view_documentation()
        elif choice == '8':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid option. Please try again.")
        
        if choice in ['1', '2', '3', '4', '5']:
            input("\nPress Enter to return to menu...")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)