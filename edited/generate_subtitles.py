#!/usr/bin/env python3
"""
Video Subtitle Generator using faster-whisper
Generates subtitles for video files and creates both hard-burned and soft-subtitle versions.
"""

import os
import sys
from pathlib import Path
import subprocess
import json

# Check if ffmpeg is available
def check_ffmpeg():
    """Check if ffmpeg is installed and accessible."""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, check=True)
        print("✓ FFmpeg found")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ FFmpeg not found. Please install FFmpeg first.")
        print("Windows: Download from https://ffmpeg.org/download.html")
        print("macOS: brew install ffmpeg")
        print("Ubuntu/Debian: sudo apt install ffmpeg")
        return False

def install_requirements():
    """Install required Python packages."""
    packages = [
        'faster-whisper',
        'pysubs2',
        'ffmpeg-python'
    ]
    
    print("Installing required packages...")
    for package in packages:
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', package], 
                          check=True, capture_output=True)
            print(f"✓ {package} installed")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install {package}: {e}")
            return False
    return True

def transcribe_audio(video_path, model_size="small", output_srt="output.srt"):
    """
    Transcribe audio from video using faster-whisper.
    
    Args:
        video_path (str): Path to input video file
        model_size (str): Model size ('tiny', 'small', 'medium', 'large')
        output_srt (str): Output SRT file path
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        from faster_whisper import WhisperModel
        import pysubs2
        
        print(f"Loading {model_size} model...")
        # Use CPU with optimized compute type for better performance
        model = WhisperModel(
            model_size, 
            device="cpu", 
            compute_type="int8_float32"
        )
        
        print("Transcribing audio (this may take a while)...")
        segments, info = model.transcribe(
            video_path, 
            beam_size=5
            # Language will be auto-detected by the model
        )
        
        print("Creating subtitle file...")
        subs = pysubs2.SSAFile()
        
        for i, segment in enumerate(segments, start=1):
            # Convert seconds to milliseconds
            start_ms = int(segment.start * 1000)
            end_ms = int(segment.end * 1000)
            text = segment.text.strip()
            
            if text:  # Only add non-empty segments
                # Split text into words and create shorter subtitle segments
                words = text.split()
                if len(words) <= 5:
                    # If 5 words or less, keep as is
                    subs.append(pysubs2.SSAEvent(
                        start=start_ms, 
                        end=end_ms, 
                        text=text
                    ))
                else:
                    # Split into segments of 3-5 words
                    segment_duration = end_ms - start_ms
                    num_segments = max(1, len(words) // 4)  # Aim for 4 words per segment
                    words_per_segment = len(words) // num_segments
                    
                    for j in range(0, len(words), words_per_segment):
                        segment_words = words[j:j + words_per_segment]
                        if segment_words:
                            segment_text = ' '.join(segment_words)
                            # Calculate timing for this segment
                            segment_start = start_ms + (j * segment_duration // len(words))
                            segment_end = start_ms + ((j + len(segment_words)) * segment_duration // len(words))
                            
                            subs.append(pysubs2.SSAEvent(
                                start=segment_start, 
                                end=segment_end, 
                                text=segment_text
                            ))
        
        # Save SRT file
        subs.save(output_srt)
        print(f"✓ Subtitles saved to: {output_srt}")
        
        # Print some stats
        duration = info.duration if hasattr(info, 'duration') else 0
        print(f"Video duration: {duration:.2f} seconds")
        print(f"Generated {len(subs)} subtitle segments")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        print("Please install required packages first.")
        return False
    except Exception as e:
        print(f"✗ Transcription failed: {e}")
        return False

def create_hard_subtitles(video_path, srt_path, output_path="output_hardsub.mp4"):
    """
    Create hard-burned subtitles (subtitles are part of the video frames).
    Uses the proven working method with temporary files.
    
    Args:
        video_path (str): Input video file path
        srt_path (str): SRT subtitle file path
        output_path (str): Output video file path
    
    Returns:
        bool: True if successful, False otherwise
    """
    print("Creating hard-burned subtitles (using proven working method)...")
    
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
        import shutil
        shutil.copy2(video_path, temp_video)
        shutil.copy2(srt_path, temp_srt)
        
        # Use simple paths without quotes - this is the proven working method
        cmd = [
            'ffmpeg', '-i', temp_video,
            '-vf', f'subtitles={temp_srt}',
            '-c:v', 'libx264', '-c:a', 'copy', '-crf', '23', '-y', temp_output
        ]
        
        print(f"🔍 Command: {' '.join(cmd)}")
        
        # Run the command
        result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        
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
        
        # Clean up temporary files even on error
        cleanup_files = [temp_video, temp_srt, temp_output]
        for temp_file in cleanup_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        
        # Clean up temporary files even on error
        cleanup_files = [temp_video, temp_srt, temp_output]
        for temp_file in cleanup_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        return False

def create_soft_subtitles(video_path, srt_path, output_path="output_softsub.mp4"):
    """
    Create soft subtitles (subtitles as a separate track that can be toggled).
    
    Args:
        video_path (str): Input video file path
        srt_path (str): SRT subtitle file path
        output_path (str): Output video file path
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        import ffmpeg
        
        print("Creating soft subtitles (adding subtitle track)...")
        
        video = ffmpeg.input(video_path)
        subs = ffmpeg.input(srt_path)
        
        (
            ffmpeg
            .output(
                video, subs, output_path,
                c="copy",  # Copy video and audio without re-encoding
                c_s="mov_text"  # MP4-compatible subtitle codec
            )
            .overwrite_output()
            .run(quiet=True)
        )
        
        print(f"✓ Soft-subtitled video saved to: {output_path}")
        return True
        
    except ImportError:
        # Fallback to command line ffmpeg
        print("Using command line ffmpeg...")
        cmd = [
            'ffmpeg', '-i', video_path,
            '-i', srt_path,
            '-c', 'copy',
            '-c:s', 'mov_text',
            '-y',
            output_path
        ]
        
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"✓ Soft-subtitled video saved to: {output_path}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ FFmpeg failed: {e}")
            return False
    except Exception as e:
        print(f"✗ Soft subtitle creation failed: {e}")
        return False

def main():
    """Main function to process video and generate subtitles."""
    print("🎬 Video Subtitle Generator")
    print("=" * 50)
    
    # Check ffmpeg
    if not check_ffmpeg():
        return
    
    # Find video file
    video_files = [f for f in os.listdir('.') if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))]
    
    if not video_files:
        print("✗ No video files found in current directory")
        return
    
    # Use the first video file found
    video_path = video_files[0]
    print(f"Found video: {video_path}")
    
    # Check if requirements are installed
    try:
        import faster_whisper
        import pysubs2
        print("✓ Required packages found")
    except ImportError:
        print("Installing required packages...")
        if not install_requirements():
            print("✗ Failed to install required packages")
            return
    
    # Generate SRT file
    srt_file = f"{Path(video_path).stem}_subtitles.srt"
    if not transcribe_audio(video_path, model_size="small", output_srt=srt_file):
        return
    
    # Create output filenames
    base_name = Path(video_path).stem
    hard_output = f"{base_name}_hardsub.mp4"
    soft_output = f"{base_name}_softsub.mp4"
    
    print("\n" + "=" * 50)
    print("Creating subtitle videos...")
    
    # Create hard-burned subtitles
    if create_hard_subtitles(video_path, srt_file, hard_output):
        print(f"✓ Hard subtitles: {hard_output}")
    
    # Create soft subtitles
    if create_soft_subtitles(video_path, srt_file, soft_output):
        print(f"✓ Soft subtitles: {soft_output}")
    
    print("\n" + "=" * 50)
    print("🎉 Subtitle generation complete!")
    print(f"📝 SRT file: {srt_file}")
    print(f"🎬 Hard subtitles: {hard_output}")
    print(f"🎬 Soft subtitles: {soft_output}")
    print("\nNotes:")
    print("- Hard subtitles are burned into the video (larger file, always visible)")
    print("- Soft subtitles can be toggled on/off in video players")
    print("- SRT file can be used with other video players")

if __name__ == "__main__":
    main()
