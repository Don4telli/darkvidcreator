3#!/usr/bin/env python3
"""
Quick deployment script for ImageToVideo Creator
Supports multiple deployment platforms
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def run_command(cmd, check=True):
    """Run a shell command and return the result."""
    print(f"Running: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return None

def check_requirements():
    """Check if required files exist."""
    required_files = ['gui_web.py', 'requirements.txt', 'Procfile']
    missing = [f for f in required_files if not Path(f).exists()]
    
    if missing:
        print(f"❌ Missing required files: {', '.join(missing)}")
        return False
    
    print("✅ All required files found")
    return True

def deploy_railway():
    """Deploy to Railway."""
    print("\n🚂 Deploying to Railway...")
    
    # Check if Railway CLI is installed
    result = run_command("railway --version", check=False)
    if not result or result.returncode != 0:
        print("❌ Railway CLI not found. Install it with:")
        print("   npm install -g @railway/cli")
        return False
    
    # Login and deploy
    print("Please login to Railway if prompted...")
    run_command("railway login")
    
    # Initialize project if needed
    if not Path(".railway").exists():
        run_command("railway init")
    
    # Deploy
    result = run_command("railway up")
    if result and result.returncode == 0:
        print("✅ Successfully deployed to Railway!")
        run_command("railway status")
        return True
    
    return False

def deploy_heroku():
    """Deploy to Heroku."""
    print("\n🟣 Deploying to Heroku...")
    
    # Check if Heroku CLI is installed
    result = run_command("heroku --version", check=False)
    if not result or result.returncode != 0:
        print("❌ Heroku CLI not found. Install it from: https://devcenter.heroku.com/articles/heroku-cli")
        return False
    
    # Check if git repo exists
    if not Path(".git").exists():
        print("Initializing git repository...")
        run_command("git init")
        run_command("git add .")
        run_command('git commit -m "Initial commit"')
    
    # Get app name
    app_name = input("Enter Heroku app name (or press Enter for auto-generated): ").strip()
    
    # Create Heroku app
    if app_name:
        result = run_command(f"heroku create {app_name}")
    else:
        result = run_command("heroku create")
    
    if not result or result.returncode != 0:
        print("❌ Failed to create Heroku app")
        return False
    
    # Deploy
    result = run_command("git push heroku main")
    if result and result.returncode == 0:
        print("✅ Successfully deployed to Heroku!")
        run_command("heroku open")
        return True
    
    return False

def deploy_docker():
    """Build Docker image."""
    print("\n🐳 Building Docker image...")
    
    # Check if Docker is installed
    result = run_command("docker --version", check=False)
    if not result or result.returncode != 0:
        print("❌ Docker not found. Install it from: https://docker.com")
        return False
    
    # Build image
    image_name = "imagetovideo-creator"
    result = run_command(f"docker build -t {image_name} .")
    
    if result and result.returncode == 0:
        print(f"✅ Docker image '{image_name}' built successfully!")
        print(f"\nTo run locally: docker run -p 8080:8080 {image_name}")
        print(f"To push to registry: docker tag {image_name} your-registry/{image_name}")
        return True
    
    return False

def setup_ngrok():
    """Setup ngrok for quick testing."""
    print("\n🌐 Setting up ngrok for quick testing...")
    
    # Check if ngrok is installed
    result = run_command("ngrok version", check=False)
    if not result or result.returncode != 0:
        print("❌ ngrok not found. Install it from: https://ngrok.com")
        print("   macOS: brew install ngrok")
        return False
    
    print("✅ ngrok found!")
    print("\nTo expose your local server:")
    print("1. Start your app: python gui_web.py")
    print("2. In another terminal: ngrok http 5001")
    print("3. Use the provided https URL to access your app publicly")
    
    return True

def deploy_vercel():
    """Deploy to Vercel."""
    print("\n▲ Deploying to Vercel...")
    
    # Check if Vercel CLI is installed
    result = run_command("vercel --version", check=False)
    if not result or result.returncode != 0:
        print("❌ Vercel CLI not found.")
        print("\n📦 Installation options:")
        print("   1. npm install -g vercel")
        print("   2. sudo npm install -g vercel  (if permission error)")
        print("   3. npx vercel --prod  (no installation needed)")
        print("   4. brew install vercel-cli  (macOS with Homebrew)")
        print("\n💡 If you get EACCES errors, see TROUBLESHOOTING.md")
        
        choice = input("\nTry with npx instead? (y/n): ").lower().strip()
        if choice == 'y':
            print("\n🔄 Using npx...")
            result = run_command("npx vercel login")
            if result and result.returncode == 0:
                result = run_command("npx vercel --prod")
                if result and result.returncode == 0:
                    print("✅ Successfully deployed to Vercel using npx!")
                    return True
        return False
    
    # Login and deploy
    print("Please login to Vercel if prompted...")
    run_command("vercel login")
    
    # Deploy
    result = run_command("vercel --prod")
    if result and result.returncode == 0:
        print("✅ Successfully deployed to Vercel!")
        return True
    
    return False

def deploy_netlify():
    """Deploy to Netlify."""
    print("\n🌐 Deploying to Netlify...")
    print("⚠️  Note: Netlify is better for static sites. Consider Railway or Vercel for this Flask app.")
    
    # Check if Netlify CLI is installed
    result = run_command("netlify --version", check=False)
    if not result or result.returncode != 0:
        print("❌ Netlify CLI not found.")
        print("\n📦 Installation options:")
        print("   1. npm install -g netlify-cli")
        print("   2. sudo npm install -g netlify-cli  (if permission error)")
        print("   3. npx netlify-cli deploy --prod  (no installation needed)")
        print("   4. brew install netlify-cli  (macOS with Homebrew)")
        print("\n💡 If you get EACCES errors, see TROUBLESHOOTING.md")
        
        choice = input("\nTry with npx instead? (y/n): ").lower().strip()
        if choice == 'y':
            print("\n🔄 Using npx...")
            result = run_command("npx netlify-cli login")
            if result and result.returncode == 0:
                result = run_command("npx netlify-cli deploy --prod")
                if result and result.returncode == 0:
                    print("✅ Successfully deployed to Netlify using npx!")
                    return True
        return False
    
    # Login and deploy
    print("Please login to Netlify if prompted...")
    run_command("netlify login")
    
    # Deploy
    result = run_command("netlify deploy --prod")
    if result and result.returncode == 0:
        print("✅ Successfully deployed to Netlify!")
        print("⚠️  Note: You may need to configure Netlify Functions for full Flask functionality.")
        return True
    
    return False

def show_menu():
    """Show deployment options menu."""
    print("\n🚀 ImageToVideo Creator - Deployment Helper")
    print("=" * 50)
    print("1. 🚂 Deploy to Railway (Recommended)")
    print("2. ▲ Deploy to Vercel")
    print("3. 🌐 Deploy to Netlify")
    print("4. 🟣 Deploy to Heroku")
    print("5. 🐳 Build Docker image")
    print("6. 🌍 Setup ngrok (Quick testing)")
    print("7. ❓ Show deployment guide")
    print("8. 🚪 Exit")
    print("=" * 50)

def show_guide():
    """Show deployment guide."""
    print("\n📖 Deployment Guide")
    print("=" * 25)
    print("\n🚂 Railway (Easiest):")
    print("   - Free tier available")
    print("   - Automatic HTTPS")
    print("   - Easy setup")
    print("\n▲ Vercel (Serverless):")
    print("   - Free tier available")
    print("   - Excellent for Python apps")
    print("   - Auto-scaling")
    print("\n🌐 Netlify (Static + Functions):")
    print("   - Free tier available")
    print("   - Better for static sites")
    print("   - Requires function conversion")
    print("\n🟣 Heroku:")
    print("   - Popular platform")
    print("   - Paid plans only")
    print("   - Good documentation")
    print("\n🐳 Docker:")
    print("   - Works with any cloud provider")
    print("   - Google Cloud Run, AWS, etc.")
    print("   - More technical setup")
    print("\n🌍 ngrok:")
    print("   - Instant public URL")
    print("   - Great for testing/demos")
    print("   - Free tier with limitations")
    print("\nFor detailed instructions, see DEPLOYMENT.md")

def main():
    """Main deployment script."""
    print("🎬 ImageToVideo Creator - Deployment Helper")
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    while True:
        show_menu()
        choice = input("\nSelect an option (1-8): ").strip()
        
        if choice == '1':
            deploy_railway()
        elif choice == '2':
            deploy_vercel()
        elif choice == '3':
            deploy_netlify()
        elif choice == '4':
            deploy_heroku()
        elif choice == '5':
            deploy_docker()
        elif choice == '6':
            setup_ngrok()
        elif choice == '7':
            show_guide()
        elif choice == '8':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid option. Please try again.")
        
        input("\nPress Enter to continue...")

if __name__ == '__main__':
    main()