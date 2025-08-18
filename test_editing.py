#!/usr/bin/env python3
"""
Test script to check if video editing is working
"""

import os
import sys
from pathlib import Path

# Add the edited directory to Python path
edited_dir = Path("edited")
sys.path.insert(0, str(edited_dir))

def test_editing():
    """Test if video editing functionality works"""
    print("🧪 Testing Video Editing Functionality")
    print("=" * 50)
    
    try:
        # Check if we can import the editing module
        print("🔍 Importing editing module...")
        from editing import beat_synced_reel
        print("✅ Successfully imported beat_synced_reel function")
        
        # Check if videos exist
        videos_dir = Path("output/videos")
        if not videos_dir.exists():
            print("❌ Videos directory not found")
            return False
        
        video_files = list(videos_dir.glob("*.mp4"))
        print(f"📹 Found {len(video_files)} video files")
        
        if len(video_files) == 0:
            print("❌ No video files found")
            return False
        
        # Check if we have an audio file
        audio_files = list(Path("output").glob("*.wav"))
        if len(audio_files) == 0:
            print("⚠️  No audio file found, creating a dummy audio file for testing")
            # Create a dummy audio file for testing
            dummy_audio = Path("output/test_audio.wav")
            try:
                # Try to create a simple audio file using librosa
                import librosa
                import numpy as np
                import soundfile as sf
                
                # Generate 5 seconds of silence
                sample_rate = 22050
                duration = 5.0
                samples = np.zeros(int(sample_rate * duration))
                sf.write(str(dummy_audio), samples, sample_rate)
                print(f"✅ Created dummy audio file: {dummy_audio}")
                audio_path = str(dummy_audio)
            except Exception as e:
                print(f"❌ Failed to create dummy audio: {e}")
                return False
        else:
            audio_path = str(audio_files[0])
            print(f"🎵 Using existing audio file: {audio_path}")
        
        # Test the editing function
        print("\n🎬 Testing video editing...")
        output_path = "output/test_editing_output.mp4"
        
        try:
            beat_synced_reel(audio_path, str(videos_dir), output_path)
            
            if os.path.exists(output_path):
                print(f"✅ Video editing test successful!")
                print(f"🎬 Output file: {output_path}")
                
                # Get file size
                file_size = os.path.getsize(output_path)
                print(f"📊 File size: {file_size / (1024*1024):.2f} MB")
                
                return True
            else:
                print("❌ Video editing failed - no output file generated")
                return False
                
        except Exception as e:
            print(f"❌ Video editing failed with error: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except ImportError as e:
        print(f"❌ Failed to import editing module: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_editing()
    if success:
        print("\n🎉 Video editing is working correctly!")
    else:
        print("\n❌ Video editing has issues that need to be fixed")
