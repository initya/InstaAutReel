import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

class Config:
    # Pexels API Configuration
    PEXELS_API_KEY = os.getenv('PEXELS_API_KEY', '')
    SEARCH_URL = "https://api.pexels.com/videos/search"
    
    # Application Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # File Storage Configuration
    SAVE_DIR = os.getenv('SAVE_DIR', 'videos')
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    ALLOWED_EXTENSIONS = {'txt'}
    
    # Download Configuration
    MAX_VIDEOS_PER_KEYWORD = int(os.getenv('MAX_VIDEOS_PER_KEYWORD', '5'))
    DOWNLOAD_DELAY = float(os.getenv('DOWNLOAD_DELAY', '0.5'))
    
    @classmethod
    def validate_api_key(cls):
        """Validate that the Pexels API key is set and looks valid"""
        if not cls.PEXELS_API_KEY:
            return False, "No Pexels API key found"
        
        if cls.PEXELS_API_KEY == 'TOv7wzLAVTXwkt00DMN5vqcqjuwtH2iv5oMQFVWfX2vNc9IvliVKDQiV':
            return False, "Default/placeholder API key detected"
        
        if len(cls.PEXELS_API_KEY) < 20:
            return False, "API key appears too short"
        
        return True, "API key appears valid"
    
    @classmethod
    def print_config_status(cls):
        """Print the current configuration status"""
        print("🔧 Configuration Status:")
        print(f"   Pexels API Key: {'✅ Set' if cls.PEXELS_API_KEY else '❌ Not Set'}")
        print(f"   Save Directory: {cls.SAVE_DIR}")
        print(f"   Upload Folder: {cls.UPLOAD_FOLDER}")
        print(f"   Debug Mode: {'✅ Enabled' if cls.DEBUG else '❌ Disabled'}")
        
        is_valid, message = cls.validate_api_key()
        if not is_valid:
            print(f"   ⚠️  API Key Issue: {message}")
            print("   💡 Get your free API key at: https://www.pexels.com/api/")
            print("   💡 Set it as an environment variable: PEXELS_API_KEY=your_key_here")
        else:
            print(f"   ✅ API Key: {message}")
        print()
