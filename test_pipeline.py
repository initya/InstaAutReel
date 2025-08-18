#!/usr/bin/env python3
"""
Test script for the Instagram Reel Creation Pipeline
Verifies that all components are properly configured and accessible
"""

import os
import sys
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing module imports...")
    
    try:
        # Test configuration
        from config import GEMINI_DIR, CONTENT_DIR, EDITED_DIR, OUTPUT_DIR, GEMINI_API_KEY, PEXELS_API_KEY
        print("✅ Configuration imported successfully")
        
        # Test Gemini voice module
        sys.path.insert(0, str(GEMINI_DIR))
        from app import generate_tts_script_and_audio
        print("✅ Gemini voice module imported successfully")
        
        # Test content module
        sys.path.insert(0, str(CONTENT_DIR))
        from app import search_and_download_videos
        print("✅ Content module imported successfully")
        
        # Test editing module
        sys.path.insert(0, str(EDITED_DIR))
        from editing import beat_synced_reel
        print("✅ Video editing module imported successfully")
        
        # Test subtitle module
        from generate_subtitles import transcribe_audio
        print("✅ Subtitle module imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_directories():
    """Test if all required directories exist"""
    print("\n📁 Testing directory structure...")
    
    required_dirs = [
        GEMINI_DIR,
        CONTENT_DIR,
        EDITED_DIR,
        OUTPUT_DIR
    ]
    
    for directory in required_dirs:
        if directory.exists():
            print(f"✅ {directory.name} directory exists")
        else:
            print(f"❌ {directory.name} directory missing")
            return False
    
    return True

def test_api_keys():
    """Test if API keys are configured"""
    print("\n🔑 Testing API key configuration...")
    
    if GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_api_key_here":
        print("✅ Gemini API key configured")
    else:
        print("⚠️  Gemini API key not configured")
    
    if PEXELS_API_KEY and PEXELS_API_KEY != "your_pexels_api_key_here":
        print("✅ Pexels API key configured")
    else:
        print("⚠️  Pexels API key not configured")
    
    return True

def test_dependencies():
    """Test if required Python packages are installed"""
    print("\n📦 Testing Python dependencies...")
    
    required_packages = [
        'flask',
        'google.generativeai',
        'moviepy',
        'librosa',
        'faster_whisper',
        'pysubs2',
        'PIL'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'PIL':
                import PIL
            elif package == 'google.generativeai':
                import google.generativeai
            else:
                __import__(package)
            print(f"✅ {package} installed")
        except ImportError:
            print(f"❌ {package} missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    return True

def test_ffmpeg():
    """Test if FFmpeg is available"""
    print("\n🎬 Testing FFmpeg availability...")
    
    try:
        import subprocess
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, check=True)
        print("✅ FFmpeg found and working")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ FFmpeg not found")
        print("Please install FFmpeg:")
        print("Windows: Download from https://ffmpeg.org/download.html")
        print("macOS: brew install ffmpeg")
        print("Ubuntu/Debian: sudo apt install ffmpeg")
        return False

def main():
    """Run all tests"""
    print("🚀 Instagram Reel Pipeline - Component Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_directories,
        test_api_keys,
        test_dependencies,
        test_ffmpeg
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with error: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Pipeline is ready to use.")
        print("\nNext steps:")
        print("1. Configure your API keys in .env file")
        print("2. Run: python main_pipeline.py")
        print("3. Or double-click run_pipeline.bat (Windows)")
    else:
        print("⚠️  Some tests failed. Please fix the issues above.")
        print("\nCommon solutions:")
        print("1. Install missing packages: pip install -r requirements.txt")
        print("2. Install FFmpeg for video processing")
        print("3. Check API key configuration")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
