#!/usr/bin/env python3
"""
Test script to check if subtitle generation is working
"""

import os
import sys
from pathlib import Path

# Add the edited directory to Python path
edited_dir = Path("edited")
sys.path.insert(0, str(edited_dir))

def test_subtitles():
    """Test if subtitle generation functionality works"""
    print("🧪 Testing Subtitle Generation Functionality")
    print("=" * 50)
    
    try:
        # Check if we can import the subtitle module
        print("🔍 Importing subtitle module...")
        from generate_subtitles import create_hard_subtitles
        print("✅ Successfully imported create_hard_subtitles function")
        
        # Check if we have the required files
        video_path = "output/final_reel_transitions.mp4"
        srt_path = "output/final_reel_transitions_subtitles.srt"
        
        if not os.path.exists(video_path):
            print(f"❌ Video file not found: {video_path}")
            return False
        
        if not os.path.exists(srt_path):
            print(f"❌ SRT file not found: {srt_path}")
            return False
        
        print(f"📹 Video file: {video_path}")
        print(f"📝 SRT file: {srt_path}")
        
        # Test the subtitle generation
        print("\n🎬 Testing hard subtitle creation...")
        output_path = "output/final_reel_transitions_subtitles.mp4"
        
        try:
            success = create_hard_subtitles(video_path, srt_path, output_path)
            
            if success:
                print(f"✅ Subtitle generation successful!")
                if os.path.exists(output_path):
                    file_size = os.path.getsize(output_path)
                    print(f"🎬 Output file: {output_path}")
                    print(f"📊 File size: {file_size / (1024*1024):.2f} MB")
                else:
                    print("📝 Subtitles available as separate SRT file")
                return True
            else:
                print("❌ Subtitle generation failed")
                return False
                
        except Exception as e:
            print(f"❌ Subtitle generation failed with error: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except ImportError as e:
        print(f"❌ Failed to import subtitle module: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_subtitles()
    if success:
        print("\n🎉 Subtitle generation is working correctly!")
    else:
        print("\n❌ Subtitle generation has issues that need to be fixed")
