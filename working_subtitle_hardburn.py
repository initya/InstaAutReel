#!/usr/bin/env python3
"""
Working subtitle hard-burning function
Based on successful testing, this uses the correct FFmpeg command format
"""

import subprocess
import os
import shutil

def create_hard_subtitles_working(video_path, srt_path, output_path):
    """
    Working version of hard subtitle creation
    Uses temporary files with simple names to avoid Windows path issues
    """
    print("Creating hard-burned subtitles (using working method)...")
    
    # Convert to absolute paths
    video_path = os.path.abspath(str(video_path))
    srt_path = os.path.abspath(str(srt_path))
    output_path = os.path.abspath(str(output_path))
    
    # Debug: print the paths
    print(f"🔍 Video path: {video_path}")
    print(f"🔍 SRT path: {srt_path}")
    print(f"🔍 Output path: {output_path}")
    
    # Check if input files exist
    if not os.path.exists(video_path):
        print(f"❌ Video file not found: {video_path}")
        return False
    
    if not os.path.exists(srt_path):
        print(f"❌ SRT file not found: {srt_path}")
        return False
    
    # Use temporary files with simple names to avoid Windows path issues
    temp_video = "temp_video_sub.mp4"
    temp_srt = "temp_subs.srt"
    temp_output = "temp_output_sub.mp4"
    
    try:
        # Copy input files to simple named temporary files
        print("🔄 Creating temporary files...")
        shutil.copy2(video_path, temp_video)
        shutil.copy2(srt_path, temp_srt)
        
        # Use simple paths without quotes - this is what worked in our manual test
        cmd = [
            'ffmpeg', '-i', temp_video,
            '-vf', f'subtitles={temp_srt}',
            '-c:v', 'libx264', '-c:a', 'copy', '-crf', '23', '-y', temp_output
        ]
        
        print(f"🔍 Command: {' '.join(cmd)}")
        
        # Run the command
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        # Copy result back to desired output location
        if os.path.exists(temp_output):
            shutil.move(temp_output, output_path)
        
        # Clean up temporary files
        cleanup_files = [temp_video, temp_srt, temp_output]
        for temp_file in cleanup_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        
        # Check if output file was created
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"✓ Hard-subtitled video saved to: {output_path}")
            print(f"📊 File size: {file_size / (1024*1024):.2f} MB")
            return True
        else:
            print("✗ Output file not created")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"✗ FFmpeg failed: {e}")
        print(f"🔍 Return code: {e.returncode}")
        if e.stdout:
            print(f"🔍 Stdout: {e.stdout}")
        if e.stderr:
            print(f"🔍 Stderr: {e.stderr}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

def test_working_function():
    """Test the working function"""
    print("🧪 Testing Working Subtitle Function")
    print("=" * 50)
    
    # Test with existing files
    video_path = "output/test_editing_output.mp4"
    srt_path = "output/final_reel_transitions_subtitles.srt"
    output_path = "output/test_working_function.mp4"
    
    if not os.path.exists(video_path):
        print(f"❌ Test video not found: {video_path}")
        return False
    
    if not os.path.exists(srt_path):
        print(f"❌ Test SRT not found: {srt_path}")
        return False
    
    # Test the function
    success = create_hard_subtitles_working(video_path, srt_path, output_path)
    
    if success:
        print("🎉 Working function test PASSED!")
        return True
    else:
        print("❌ Working function test FAILED!")
        return False

if __name__ == "__main__":
    test_working_function()
