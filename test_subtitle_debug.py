#!/usr/bin/env python3
"""
Debug script to test subtitle hard-burning and see the exact error
"""

import subprocess
import os
from pathlib import Path

def test_ffmpeg_subtitle_command():
    """Test the exact FFmpeg command that's failing"""
    print("🧪 Testing FFmpeg Subtitle Hard-Burning")
    print("=" * 50)
    
    # Check if files exist
    video_path = "output/final_reel_transitions.mp4"
    srt_path = "output/final_reel_transitions_subtitles.srt"
    output_path = "output/debug_hardburned.mp4"
    
    if not os.path.exists(video_path):
        print(f"❌ Video file not found: {video_path}")
        return False
    
    if not os.path.exists(srt_path):
        print(f"❌ SRT file not found: {srt_path}")
        return False
    
    print(f"✅ Video file: {video_path}")
    print(f"✅ SRT file: {srt_path}")
    
    # Test the exact command that's being used in the Python script
    print("\n🔍 Testing Python script command format...")
    
    cmd = [
        'ffmpeg', '-i', video_path,
        '-vf', f'subtitles={srt_path}',
        '-c:v', 'libx264',
        '-c:a', 'copy',
        '-crf', '23',
        '-y',
        output_path
    ]
    
    print(f"🔍 Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        print("✅ Command succeeded!")
        
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"📊 Output file size: {file_size / (1024*1024):.2f} MB")
            return True
        else:
            print("❌ No output file created")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {e}")
        print(f"🔍 Return code: {e.returncode}")
        print(f"🔍 Stdout: {e.stdout}")
        print(f"🔍 Stderr: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_alternative_formats():
    """Test different subtitle command formats"""
    print("\n🔍 Testing alternative command formats...")
    
    video_path = "output/final_reel_transitions.mp4"
    srt_path = "output/final_reel_transitions_subtitles.srt"
    
    # Convert paths to absolute paths
    video_abs = os.path.abspath(video_path)
    srt_abs = os.path.abspath(srt_path)
    
    print(f"📁 Absolute video path: {video_abs}")
    print(f"📁 Absolute SRT path: {srt_abs}")
    
    # Test 1: With quotes around the subtitle path
    output1 = "output/debug_test1.mp4"
    cmd1 = [
        'ffmpeg', '-i', video_abs,
        '-vf', f'subtitles="{srt_abs}"',
        '-c:v', 'libx264', '-c:a', 'copy', '-crf', '23', '-y', output1
    ]
    
    print(f"\n🧪 Test 1 - Quoted paths: {' '.join(cmd1)}")
    try:
        subprocess.run(cmd1, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("✅ Test 1 succeeded!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Test 1 failed: {e.stderr.decode() if e.stderr else 'No error info'}")
    
    # Test 2: Escape backslashes for Windows
    srt_escaped = srt_abs.replace('\\', '\\\\')
    output2 = "output/debug_test2.mp4"
    cmd2 = [
        'ffmpeg', '-i', video_abs,
        '-vf', f'subtitles={srt_escaped}',
        '-c:v', 'libx264', '-c:a', 'copy', '-crf', '23', '-y', output2
    ]
    
    print(f"\n🧪 Test 2 - Escaped paths: {' '.join(cmd2)}")
    try:
        subprocess.run(cmd2, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("✅ Test 2 succeeded!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Test 2 failed: {e.stderr.decode() if e.stderr else 'No error info'}")
    
    # Test 3: Use forward slashes
    srt_forward = srt_abs.replace('\\', '/')
    output3 = "output/debug_test3.mp4"
    cmd3 = [
        'ffmpeg', '-i', video_abs,
        '-vf', f'subtitles={srt_forward}',
        '-c:v', 'libx264', '-c:a', 'copy', '-crf', '23', '-y', output3
    ]
    
    print(f"\n🧪 Test 3 - Forward slashes: {' '.join(cmd3)}")
    try:
        subprocess.run(cmd3, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("✅ Test 3 succeeded!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Test 3 failed: {e.stderr.decode() if e.stderr else 'No error info'}")
    
    return False

if __name__ == "__main__":
    success1 = test_ffmpeg_subtitle_command()
    if not success1:
        print("\n" + "=" * 50)
        success2 = test_alternative_formats()
        if success2:
            print("\n🎉 Found working subtitle format!")
        else:
            print("\n❌ All subtitle formats failed")
    else:
        print("\n🎉 Original format works!")
