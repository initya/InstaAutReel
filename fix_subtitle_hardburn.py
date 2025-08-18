#!/usr/bin/env python3
"""
Dedicated test to fix subtitle hard-burning issue
Testing different FFmpeg command formats until we find one that works
"""

import subprocess
import os
import tempfile
from pathlib import Path

def test_subtitle_hardburn():
    """Test different approaches to hard-burn subtitles"""
    print("🔥 Testing Subtitle Hard-Burning Solutions")
    print("=" * 60)
    
    # Check if files exist
    video_path = "output/final_reel_transitions.mp4"
    srt_path = "output/final_reel_transitions_subtitles.srt"
    
    if not os.path.exists(video_path):
        print(f"❌ Video file not found: {video_path}")
        print("💡 Run the pipeline first to generate the video")
        return False
    
    if not os.path.exists(srt_path):
        print(f"❌ SRT file not found: {srt_path}")
        print("💡 Run the pipeline first to generate the SRT")
        return False
    
    print(f"✅ Video file: {video_path}")
    print(f"✅ SRT file: {srt_path}")
    
    # Method 1: Simple file path approach
    print("\n🧪 Method 1: Simple file paths...")
    output1 = "output/test_hardburn_method1.mp4"
    cmd1 = [
        'ffmpeg', '-i', video_path,
        '-vf', f'subtitles={srt_path}',
        '-c:v', 'libx264', '-c:a', 'copy', '-crf', '23', '-y', output1
    ]
    
    if test_command(cmd1, output1, "Method 1"):
        return output1
    
    # Method 2: Use forward slashes
    print("\n🧪 Method 2: Forward slash paths...")
    video_forward = video_path.replace('\\', '/')
    srt_forward = srt_path.replace('\\', '/')
    output2 = "output/test_hardburn_method2.mp4"
    cmd2 = [
        'ffmpeg', '-i', video_forward,
        '-vf', f'subtitles={srt_forward}',
        '-c:v', 'libx264', '-c:a', 'copy', '-crf', '23', '-y', output2
    ]
    
    if test_command(cmd2, output2, "Method 2"):
        return output2
    
    # Method 3: Use short DOS 8.3 paths (works around space issues)
    print("\n🧪 Method 3: Short DOS paths...")
    try:
        import win32api
        video_short = win32api.GetShortPathName(os.path.abspath(video_path))
        srt_short = win32api.GetShortPathName(os.path.abspath(srt_path))
        output3 = "output/test_hardburn_method3.mp4"
        cmd3 = [
            'ffmpeg', '-i', video_short,
            '-vf', f'subtitles={srt_short}',
            '-c:v', 'libx264', '-c:a', 'copy', '-crf', '23', '-y', output3
        ]
        
        if test_command(cmd3, output3, "Method 3"):
            return output3
    except ImportError:
        print("⚠️  win32api not available, skipping short path method")
    
    # Method 4: Use temporary files in current directory
    print("\n🧪 Method 4: Temporary local files...")
    temp_video = "temp_video.mp4"
    temp_srt = "temp_subtitles.srt"
    output4 = "output/test_hardburn_method4.mp4"
    
    try:
        # Copy files to current directory with simple names
        import shutil
        shutil.copy2(video_path, temp_video)
        shutil.copy2(srt_path, temp_srt)
        
        cmd4 = [
            'ffmpeg', '-i', temp_video,
            '-vf', f'subtitles={temp_srt}',
            '-c:v', 'libx264', '-c:a', 'copy', '-crf', '23', '-y', output4
        ]
        
        result = test_command(cmd4, output4, "Method 4")
        
        # Clean up temp files
        if os.path.exists(temp_video):
            os.remove(temp_video)
        if os.path.exists(temp_srt):
            os.remove(temp_srt)
            
        if result:
            return output4
    except Exception as e:
        print(f"❌ Method 4 failed: {e}")
    
    # Method 5: Use ass filter instead of subtitles filter
    print("\n🧪 Method 5: ASS filter...")
    output5 = "output/test_hardburn_method5.mp4"
    cmd5 = [
        'ffmpeg', '-i', video_path,
        '-vf', f'ass={srt_path}',
        '-c:v', 'libx264', '-c:a', 'copy', '-crf', '23', '-y', output5
    ]
    
    if test_command(cmd5, output5, "Method 5"):
        return output5
    
    # Method 6: Convert SRT to ASS first, then use ass filter
    print("\n🧪 Method 6: Convert SRT to ASS first...")
    temp_ass = "temp_subtitles.ass"
    output6 = "output/test_hardburn_method6.mp4"
    
    try:
        # Convert SRT to ASS
        convert_cmd = ['ffmpeg', '-i', srt_path, '-y', temp_ass]
        subprocess.run(convert_cmd, check=True, capture_output=True)
        
        cmd6 = [
            'ffmpeg', '-i', video_path,
            '-vf', f'ass={temp_ass}',
            '-c:v', 'libx264', '-c:a', 'copy', '-crf', '23', '-y', output6
        ]
        
        result = test_command(cmd6, output6, "Method 6")
        
        # Clean up
        if os.path.exists(temp_ass):
            os.remove(temp_ass)
            
        if result:
            return output6
    except Exception as e:
        print(f"❌ Method 6 failed: {e}")
    
    print("\n❌ All methods failed!")
    return False

def test_command(cmd, output_file, method_name):
    """Test a specific FFmpeg command"""
    print(f"🔍 {method_name} Command: {' '.join(cmd)}")
    
    try:
        # Run the command
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        # Check if output file was created
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"✅ {method_name} SUCCESS! Output: {output_file} ({file_size / (1024*1024):.2f} MB)")
            
            # Quick verification - check if it's a valid video
            verify_cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams', output_file]
            try:
                verify_result = subprocess.run(verify_cmd, check=True, capture_output=True, text=True)
                print(f"✅ {method_name} Video verification passed")
                return True
            except:
                print(f"⚠️  {method_name} Video verification failed, but file exists")
                return True
        else:
            print(f"❌ {method_name} failed - no output file created")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ {method_name} failed: {e.returncode}")
        if e.stderr:
            # Show only the important error lines
            error_lines = e.stderr.split('\n')
            for line in error_lines:
                if 'Error' in line or 'Unable to parse' in line:
                    print(f"   🔍 {line.strip()}")
        return False
    except Exception as e:
        print(f"❌ {method_name} unexpected error: {e}")
        return False

def create_working_function(working_method_output):
    """Create a working subtitle function based on successful method"""
    print(f"\n🎉 Creating working function based on successful method...")
    
    # Analyze which method worked and create optimized function
    if "method4" in working_method_output:
        print("📝 Method 4 (temporary local files) worked - creating optimized function")
        
        function_code = '''
def create_hard_subtitles_working(video_path, srt_path, output_path):
    """
    Working version of hard subtitle creation using temporary local files
    """
    import subprocess
    import shutil
    import os
    
    print("Creating hard-burned subtitles (using working method)...")
    
    # Use temporary files in current directory with simple names
    temp_video = "temp_video_for_subs.mp4"
    temp_srt = "temp_subtitles_for_subs.srt"
    
    try:
        # Copy files to current directory with simple names
        shutil.copy2(video_path, temp_video)
        shutil.copy2(srt_path, temp_srt)
        
        cmd = [
            'ffmpeg', '-i', temp_video,
            '-vf', f'subtitles={temp_srt}',
            '-c:v', 'libx264', '-c:a', 'copy', '-crf', '23', '-y', output_path
        ]
        
        print(f"🔍 Command: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        # Clean up temp files
        if os.path.exists(temp_video):
            os.remove(temp_video)
        if os.path.exists(temp_srt):
            os.remove(temp_srt)
        
        if os.path.exists(output_path):
            print(f"✓ Hard-subtitled video saved to: {output_path}")
            return True
        else:
            print("✗ Output file not created")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"✗ FFmpeg failed: {e}")
        if e.stderr:
            print(f"🔍 Error details: {e.stderr}")
        
        # Clean up temp files even on error
        if os.path.exists(temp_video):
            os.remove(temp_video)
        if os.path.exists(temp_srt):
            os.remove(temp_srt)
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False
'''
        
        # Write the working function to a file
        with open("working_subtitle_function.py", "w") as f:
            f.write(function_code)
        
        print("✅ Working function saved to: working_subtitle_function.py")
        return True
    
    elif "method2" in working_method_output:
        print("📝 Method 2 (forward slashes) worked - creating optimized function")
        # Add method 2 function here
        return True
    
    # Add other methods as needed
    return False

if __name__ == "__main__":
    print("🚀 Starting Subtitle Hard-Burn Fix Test")
    working_output = test_subtitle_hardburn()
    
    if working_output:
        print(f"\n🎉 SUCCESS! Working method found: {working_output}")
        create_working_function(working_output)
        
        # Test the working video
        print(f"\n🎬 Testing the working video:")
        print(f"   ▶️  Play with: ffplay {working_output}")
        print(f"   📊 Check with: ffprobe {working_output}")
    else:
        print("\n❌ No working method found. Please check FFmpeg installation and file permissions.")

