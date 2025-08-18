#!/usr/bin/env python3
"""
Test script for Pexels API key validation
Run this script to check if your API key is working correctly
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_pexels_api():
    """Test the Pexels API with the current API key"""
    
    # Get API key from environment or use the one from app.py
    api_key = os.getenv('PEXELS_API_KEY', 'TOv7wzLAVTXwkt00DMN5vqcqjuwtH2iv5oMQFVWfX2vNc9IvlihKDQiV')
    
    print("🔍 Testing Pexels API Connection...")
    print(f"   API Key: {api_key[:10]}...{api_key[-10:] if len(api_key) > 20 else 'TOO_SHORT'}")
    print()
    
    if not api_key:
        print("❌ ERROR: No API key found!")
        print()
        print("💡 To fix this:")
        print("   1. Go to https://www.pexels.com/api/")
        print("   2. Sign up for a free account")
        print("   3. Get your API key")
        print("   4. Set it as an environment variable:")
        print("      Windows: set PEXELS_API_KEY=your_key_here")
        print("      Mac/Linux: export PEXELS_API_KEY=your_key_here")
        print("   5. Or create a .env file with: PEXELS_API_KEY=your_key_here")
        return False
    
    # Test the API
    headers = {"Authorization": api_key}
    params = {"query": "nature", "per_page": 1}
    
    try:
        print("🌐 Making API request...")
        response = requests.get("https://api.pexels.com/videos/search", headers=headers, params=params)
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            total_results = data.get('total_results', 0)
            print(f"   ✅ SUCCESS! API is working correctly")
            print(f"   📊 Total results for 'nature': {total_results}")
            print(f"   🎬 Videos returned: {len(data.get('videos', []))}")
            return True
            
        elif response.status_code == 401:
            print("   ❌ ERROR: 401 Unauthorized")
            print("      This means your API key is invalid or expired")
            print("      Please check your API key and try again")
            
        elif response.status_code == 429:
            print("   ⚠️  WARNING: 429 Rate Limited")
            print("      You've hit the API rate limit. Please wait before trying again")
            
        elif response.status_code == 403:
            print("   ❌ ERROR: 403 Forbidden")
            print("      Your API key may be invalid or you may have exceeded your quota")
            
        else:
            print(f"   ❌ ERROR: Unexpected status code {response.status_code}")
            print(f"      Response: {response.text[:200]}...")
            
        return False
        
    except requests.exceptions.RequestException as e:
        print(f"   ❌ ERROR: Network/connection error: {e}")
        print("      Please check your internet connection")
        return False
    except Exception as e:
        print(f"   ❌ ERROR: Unexpected error: {e}")
        return False

def main():
    """Main function"""
    print("=" * 60)
    print("🎬 PEXELS API KEY TESTER")
    print("=" * 60)
    print()
    
    success = test_pexels_api()
    
    print()
    print("=" * 60)
    if success:
        print("🎉 Your Pexels API key is working correctly!")
        print("   You can now run the Flask application: python app.py")
    else:
        print("⚠️  Please fix the API key issue before running the Flask app")
    print("=" * 60)

if __name__ == "__main__":
    main()
