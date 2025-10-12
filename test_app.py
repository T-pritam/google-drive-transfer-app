#!/usr/bin/env python3
"""
Test script for Google Drive Transfer App
Run this to test the app locally
"""

import os
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 9):
        print("❌ Python 3.9+ required. Current version:", sys.version)
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def create_env_file():
    """Create .env file if it doesn't exist"""
    env_file = Path(".env")
    if not env_file.exists():
        print("📝 Creating .env file...")
        with open(".env", "w") as f:
            f.write("""# Google OAuth Credentials - REPLACE WITH YOUR OWN VALUES
CLIENT_ID=your-google-oauth-client-id
CLIENT_SECRET=your-google-oauth-client-secret
REFRESH_TOKEN=your-google-oauth-refresh-token

# Application Authentication
AUTH_USERNAME=admin
AUTH_PASSWORD=secure123

# Flask Configuration
SECRET_KEY=dev-secret-key-change-in-production
FLASK_ENV=development
PORT=5000
""")
        print("✅ .env file created")
    else:
        print("✅ .env file already exists")

def test_import():
    """Test if all imports work"""
    print("🧪 Testing imports...")
    try:
        import flask
        import requests
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def start_server():
    """Start the Flask development server"""
    print("🚀 Starting Flask development server...")
    print("📱 App will be available at: http://localhost:5000")
    print("🔐 Login credentials: admin / secure123")
    print("⏹️  Press Ctrl+C to stop the server")
    
    # Wait a moment then open browser
    time.sleep(2)
    try:
        webbrowser.open("http://localhost:5000")
    except:
        pass
    
    # Start the app
    os.environ['FLASK_ENV'] = 'development'
    try:
        subprocess.run([sys.executable, "app.py"])
    except KeyboardInterrupt:
        print("\n👋 Server stopped")

def main():
    """Main test function"""
    print("🔧 Google Drive Transfer App - Local Test")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return
    
    # Install dependencies
    if not install_dependencies():
        return
    
    # Create .env file
    create_env_file()
    
    # Test imports
    if not test_import():
        return
    
    print("\n🎉 All tests passed! Starting server...")
    print("\nℹ️  To test the app:")
    print("1. Open http://localhost:5000")
    print("2. Login with: admin / secure123")
    print("3. Try transferring a small Google Drive file")
    print("4. Use this test URL: https://drive.google.com/file/d/1kKoD6alsXMGIyGL656vF4xmDuUJB3-uY/view?usp=drivesdk")
    
    input("\nPress Enter to start the server...")
    start_server()

if __name__ == "__main__":
    main()