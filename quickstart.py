#!/usr/bin/env python3
"""Quick start script for ConsumeSafe"""

import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path

def print_header():
    print("""
    🇵🇸 ConsumeSafe - Quick Start 🇵🇸
    ================================
    Stand with Palestine | Support Tunisia
    """)

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing dependencies...")
    print("   This may take a minute...\n")
    
    # Upgrade pip first
    subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                   capture_output=True)
    
    # Install packages individually with simpler versions
    packages = [
        "fastapi==0.109.0",
        "uvicorn[standard]==0.27.0",
        "aiofiles==23.2.1",
    ]
    
    for package in packages:
        print(f"   Installing {package}...")
        result = subprocess.run([sys.executable, "-m", "pip", "install", package], 
                               capture_output=True, text=True)
        if result.returncode != 0:
            print(f"   ⚠️  Warning installing {package}")
    
    print("✓ Dependencies installed\n")

def start_api():
    """Start the FastAPI server"""
    print("🚀 Starting API server...")
    print("   API will be available at: http://localhost:8000")
    print("   API Docs at: http://localhost:8000/docs\n")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
        cwd=base_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

def start_frontend():
    """Start a simple HTTP server for the frontend"""
    print("🎨 Starting Frontend server...")
    print("   Frontend will be available at: http://localhost:8080\n")
    
    frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app")
    subprocess.Popen(
        [sys.executable, "-m", "http.server", "8080"],
        cwd=frontend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

def test_api():
    """Test if API is responding"""
    import urllib.request
    max_retries = 15
    for i in range(max_retries):
        try:
            response = urllib.request.urlopen("http://localhost:8000/api/health", timeout=2)
            if response.status == 200:
                print("✓ API is responding\n")
                return True
        except:
            if i < max_retries - 1:
                sys.stdout.write(f"\r   Waiting for API... ({i+1}/{max_retries})")
                sys.stdout.flush()
                time.sleep(1)
    print("\n")
    return False

def main():
    print_header()
    
    # Check Python version
    if sys.version_info < (3, 9):
        print("❌ Python 3.9+ is required")
        sys.exit(1)
    
    print(f"✓ Python {sys.version.split()[0]} OK\n")
    
    # Install dependencies
    try:
        install_dependencies()
    except Exception as e:
        print(f"⚠️  Dependency installation issue (trying to continue): {e}\n")
    
    # Start servers
    print("Starting servers in background...\n")
    start_api()
    time.sleep(3)
    start_frontend()
    time.sleep(2)
    
    # Test API
    if test_api():
        print("🎉 ConsumeSafe is ready!")
        print("\n" + "="*60)
        print("Access the application at:")
        print("="*60)
        print("  📍 Frontend: http://localhost:8080")
        print("  📍 API: http://localhost:8000")
        print("  📍 API Docs: http://localhost:8000/docs")
        print("="*60)
        print("\n🇵🇸 Stand with Palestine | Support Tunisia 🇹🇳\n")
        
        # Open browser
        try:
            webbrowser.open("http://localhost:8080")
            print("✓ Browser opened automatically\n")
        except:
            print("(Could not open browser automatically)\n")
        
        # Keep running
        print("Press Ctrl+C to stop the servers")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n✓ Shutting down...")
            sys.exit(0)
    else:
        print("❌ API failed to start")
        print("   This might be due to missing dependencies.")
        print("   Try installing manually:")
        print("   pip install fastapi uvicorn[standard]")
        print("   Then run the API with:")
        print("   python -m uvicorn app.main:app --reload")
        sys.exit(1)

if __name__ == "__main__":
    main()
