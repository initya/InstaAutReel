#!/usr/bin/env python3
"""
Dependency Installer for Instagram Reel Creation Pipeline
Installs all required packages automatically
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and show progress"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def main():
    """Install all required dependencies"""
    print("🚀 Installing Dependencies for Instagram Reel Pipeline")
    print("=" * 60)
    
    # Check Python version
    python_version = sys.version_info
    print(f"🐍 Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version < (3, 8):
        print("❌ Python 3.8+ required. Please upgrade Python.")
        return False
    
    # Upgrade pip first
    print("\n📦 Upgrading pip...")
    run_command(f"{sys.executable} -m pip install --upgrade pip", "Pip upgrade")
    
    # Install packages one by one to avoid conflicts
    packages = [
        ("flask", "Flask web framework"),
        ("requests", "HTTP library"),
        ("google-generativeai", "Google Gemini AI"),
        ("moviepy", "Video editing library"),
        ("librosa", "Audio processing library"),
        ("faster-whisper", "AI speech recognition"),
        ("pysubs2", "Subtitle processing"),
        ("Pillow", "Image processing"),
        ("numpy", "Numerical computing"),
        ("scipy", "Scientific computing"),
        ("ffmpeg-python", "FFmpeg wrapper")
    ]
    
    success_count = 0
    total_count = len(packages)
    
    for package, description in packages:
        print(f"\n📦 Installing {package}...")
        if run_command(f"{sys.executable} -m pip install {package}", f"Install {package}"):
            success_count += 1
        else:
            print(f"⚠️  Failed to install {package}, continuing...")
    
    print("\n" + "=" * 60)
    print(f"📊 Installation Results: {success_count}/{total_count} packages installed")
    
    if success_count == total_count:
        print("🎉 All dependencies installed successfully!")
        print("\n🚀 You can now run the pipeline:")
        print("   python main_pipeline.py")
        print("   Or double-click run_pipeline.bat (Windows)")
        return True
    else:
        print("⚠️  Some packages failed to install.")
        print("\n💡 Try these solutions:")
        print("   1. Run: pip install --upgrade pip")
        print("   2. Use virtual environment: python -m venv pipeline_env")
        print("   3. Use Windows launcher: run_pipeline.bat")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
