import os
import shutil
import subprocess
import tempfile
from pathlib import Path

# Try to import video processing libraries
try:
    import librosa
    LIBROSA_AVAILABLE = True
    print("✅ Librosa imported successfully")
except ImportError as e:
    print(f"⚠️ Librosa import failed: {e}")
    LIBROSA_AVAILABLE = False

try:
    from moviepy.editor import *
    MOVIEPY_AVAILABLE = True
    print("✅ MoviePy imported successfully")
except ImportError as e:
    print(f"⚠️ MoviePy import failed: {e}")
    MOVIEPY_AVAILABLE = False

try:
    import cv2
    OPENCV_AVAILABLE = True
    print("✅ OpenCV imported successfully")
except ImportError as e:
    print(f"⚠️ OpenCV import failed: {e}")
    OPENCV_AVAILABLE = False

# Fix for PIL.Image ANTIALIAS deprecation
try:
    from PIL import Image
    if not hasattr(Image, 'ANTIALIAS'):
        Image.ANTIALIAS = Image.LANCZOS
except ImportError:
    pass

def get_audio_duration(audio_path):
    """Get the duration of an audio file using ffmpeg"""
    try:
        cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_entries', 'format=duration', audio_path]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        import json
        data = json.loads(result.stdout)
        duration = float(data['format']['duration'])
        print(f"🎵 Audio duration detected: {duration:.2f} seconds")
        return min(duration, 60)  # Cap at 60 seconds for Instagram
    except Exception as e:
        print(f"⚠️ Could not detect audio duration: {e}, using 30 seconds default")
        return 30.0

def simple_video_concat(audio_path, videos_folder, output_path="final_reel.mp4"):
    """
    Simple video concatenation using ffmpeg directly - fallback when MoviePy is not available
    """
    print("🔄 Using simple video concatenation fallback...")
    
    video_files = sorted([
        os.path.join(videos_folder, f) for f in os.listdir(videos_folder)
        if f.lower().endswith((".mp4", ".mov", ".avi"))
    ])
    
    if not video_files:
        print("❌ No video files found!")
        raise FileNotFoundError("No video files found in the specified folder")
    
    print(f"🎬 Found {len(video_files)} video files")
    
    # Get actual audio duration
    audio_duration = get_audio_duration(audio_path)
    
    # Calculate duration per video
    duration_per_video = audio_duration / len(video_files)
    
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            # Create ffmpeg concat file
            for video_file in video_files:
                f.write(f"file '{video_file}'\n")
                f.write(f"duration {duration_per_video}\n")
            concat_file = f.name
        
        # Use ffmpeg to concatenate videos and add audio
        cmd = [
            'ffmpeg', '-y',
            '-f', 'concat', '-safe', '0', '-i', concat_file,
            '-i', audio_path,
            '-c:v', 'libx264', '-c:a', 'aac',
            '-vf', 'scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920',
            '-t', str(audio_duration),
            '-map', '0:v:0', '-map', '1:a:0',  # Explicitly map video and audio
            output_path
        ]
        
        print("🔧 Running ffmpeg command...")
        print(f"🔍 Command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ FFmpeg error (return code {result.returncode}): {result.stderr}")
            print(f"🔍 FFmpeg stdout: {result.stdout}")
            print("🔄 Falling back to placeholder video...")
            create_placeholder_video(output_path, audio_path)
        else:
            print(f"✅ Video created successfully: {output_path}")
            # Check if file was actually created and has reasonable size
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"📊 File size: {file_size / (1024*1024):.2f} MB")
                if file_size < 100000:  # Less than 100KB is suspicious
                    print("⚠️ Video file seems too small, might be corrupted")
            else:
                print("❌ Output file was not created")
                create_placeholder_video(output_path, audio_path)
            
    except Exception as e:
        print(f"❌ Error in simple concatenation: {e}")
        create_placeholder_video(output_path, audio_path)
    finally:
        # Clean up
        if 'concat_file' in locals() and os.path.exists(concat_file):
            os.unlink(concat_file)

def create_placeholder_video(output_path, audio_path):
    """Create a simple placeholder video with audio"""
    print("🎥 Creating placeholder video...")
    
    # Get actual audio duration
    audio_duration = get_audio_duration(audio_path)
    
    try:
        cmd = [
            'ffmpeg', '-y',
            '-f', 'lavfi', '-i', f'color=c=black:s=1080x1920:d={audio_duration}:r=30',
            '-i', audio_path,
            '-c:v', 'libx264', '-c:a', 'aac',
            '-t', str(audio_duration),
            '-map', '0:v:0', '-map', '1:a:0',  # Explicitly map video and audio
            output_path
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"✅ Placeholder video created: {output_path} ({audio_duration}s)")
    except Exception as e:
        print(f"❌ Failed to create placeholder video: {e}")
        raise

def beat_synced_reel(audio_path, videos_folder, output_path="final_reel.mp4"):
    """
    Main video editing function with fallback options
    """
    print("🎬 Starting video editing process...")
    
    # Try MoviePy first if available
    if MOVIEPY_AVAILABLE and LIBROSA_AVAILABLE:
        try:
            return beat_synced_reel_moviepy(audio_path, videos_folder, output_path)
        except Exception as e:
            print(f"⚠️ MoviePy method failed: {e}")
            print("🔄 Falling back to simple concatenation...")
    
    # Fallback to simple concatenation
    try:
        return simple_video_concat(audio_path, videos_folder, output_path)
    except Exception as e:
        print(f"❌ Simple concatenation failed: {e}")
        # Final fallback - create placeholder
        create_placeholder_video(output_path, audio_path)

def beat_synced_reel_moviepy(audio_path, videos_folder, output_path="final_reel.mp4"):
    """
    Original MoviePy-based video editing (when available)
    """
    print("🔍 Analyzing audio beats...")
    y, sr = librosa.load(audio_path, sr=None)
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beats, sr=sr)
    print(f"🎵 Tempo: {float(tempo):.2f} BPM, Beats detected: {len(beat_times)}")

    video_files = sorted(
        [os.path.join(videos_folder, f) for f in os.listdir(videos_folder)
         if f.lower().endswith((".mp4", ".mov", ".avi"))]
    )

    if not video_files:
        print("❌ No video files found in the folder!")
        return
    print(f"🎬 Found {len(video_files)} video clips.")

    # Resize & crop to 1080x1920 for Instagram Reels
    clips = []
    for vf in video_files:
        clip = VideoFileClip(vf)
        # Calculate scaling to maintain aspect ratio
        if clip.w / clip.h > 1080 / 1920:  # too wide
            clip = clip.resize(height=1920)
            clip = clip.crop(x_center=clip.w / 2, width=1080)
        else:  # too tall or perfect ratio
            clip = clip.resize(width=1080)
            if clip.h > 1920:
                clip = clip.crop(y_center=clip.h / 2, height=1920)
        clips.append(clip)

    # Group beats to keep scenes for ~2 seconds
    print("✂️ Cutting and arranging clips with random variety...")
    final_clips = []
    
    import random
    
    # Handle case where no beats are detected (e.g., silence or very quiet audio)
    if len(beat_times) < 2:
        print("⚠️  No beats detected, using fixed timing (2 seconds per clip)")
        # Use a fixed duration based on audio length or default to 10 seconds
        try:
            total_audio_duration = librosa.get_duration(y=y, sr=sr)
        except:
            total_audio_duration = 10.0  # Default 10 seconds if can't determine
        
        # Create clips with fixed 2-second duration
        current_time = 0
        clip_idx = 0
        
        while current_time < total_audio_duration:
            duration = min(2.0, total_audio_duration - current_time)
            
            # Use current clip (cycle through all available clips)
            current_clip = clips[clip_idx % len(clips)]
            
            # Choose a random starting point in the video
            max_start = max(0, current_clip.duration - duration - 0.5)
            if max_start > 0:
                random_start = random.uniform(0, max_start)
            else:
                random_start = 0
            
            # Ensure we don't exceed the clip's duration
            actual_duration = min(duration, current_clip.duration - random_start)
            
            # Create the trimmed clip
            trimmed = current_clip.subclip(random_start, random_start + actual_duration)
            
            # Apply simple fade transition
            trimmed = trimmed.fx(vfx.fadein, 0.2).fx(vfx.fadeout, 0.2)
            
            final_clips.append(trimmed)
            current_time += actual_duration
            clip_idx += 1
            
    else:
        # Normal beat-based editing
        # Calculate how many beats to group for ~2 second clips
        avg_beat_interval = (beat_times[-1] - beat_times[0]) / len(beat_times)
        beats_per_second = 1.0 / avg_beat_interval
        beats_per_clip = max(1, int(beats_per_second * 2.0))  # ~2 second per clip
        
        print(f"🎬 Using {beats_per_clip} beats per clip for ~2 second scenes")
        
        # Calculate total audio duration and create clips to fill it
        total_audio_duration = beat_times[-1] - beat_times[0]
        current_time = 0
        clip_idx = 0
    
    while current_time < total_audio_duration:
        # Find the closest beat for timing
        target_beat_idx = 0
        for i, beat_time in enumerate(beat_times):
            if beat_time >= current_time:
                target_beat_idx = i
                break
        
        # Calculate duration for this clip (2 seconds or remaining audio time)
        remaining_time = total_audio_duration - current_time
        duration = min(2.0, remaining_time)
        
        # Use current clip (cycle through all available clips)
        current_clip = clips[clip_idx % len(clips)]
        
        # Choose a random starting point in the video (but leave enough for the duration)
        max_start = max(0, current_clip.duration - duration - 0.5)  # Leave 0.5s buffer
        if max_start > 0:
            random_start = random.uniform(0, max_start)
        else:
            random_start = 0
        
        # Ensure we don't exceed the clip's duration
        actual_duration = min(duration, current_clip.duration - random_start)
        
        # Create the trimmed clip from random starting point
        trimmed = current_clip.subclip(random_start, random_start + actual_duration)
        
        # Apply random transition effects
        transition_styles = [
            'fade',
            'quick_fade',
            'zoom_in',
            'zoom_out',
            'crossfade',
            'spin_right',
            'spin_left', 
            'scale_bounce',
            'smooth_fade',
            'dramatic_fade',
            'zoom_blur',
            'gentle_zoom'
        ]
        
        transition = random.choice(transition_styles)
        print(f"  🎬 Applying '{transition}' transition to clip {clip_idx + 1}")
        
        if transition == 'fade':
            trimmed = trimmed.fx(vfx.fadein, 0.2).fx(vfx.fadeout, 0.2)
        elif transition == 'quick_fade':
            trimmed = trimmed.fx(vfx.fadein, 0.05).fx(vfx.fadeout, 0.05)
        elif transition == 'zoom_in':
            trimmed = trimmed.fx(vfx.resize, lambda t: 1 + 0.2 * t).fx(vfx.fadein, 0.1).fx(vfx.fadeout, 0.1)
        elif transition == 'zoom_out':
            trimmed = trimmed.fx(vfx.resize, lambda t: 1.2 - 0.2 * t).fx(vfx.fadein, 0.1).fx(vfx.fadeout, 0.1)
        elif transition == 'crossfade':
            trimmed = trimmed.fx(vfx.fadein, 0.4).fx(vfx.fadeout, 0.4)
        elif transition == 'spin_right':
            trimmed = trimmed.fx(vfx.rotate, lambda t: 3 * t).fx(vfx.fadein, 0.1).fx(vfx.fadeout, 0.1)
        elif transition == 'spin_left':
            trimmed = trimmed.fx(vfx.rotate, lambda t: -3 * t).fx(vfx.fadein, 0.1).fx(vfx.fadeout, 0.1)
        elif transition == 'scale_bounce':
            trimmed = trimmed.fx(vfx.resize, lambda t: 1 + 0.1 * abs(t - 0.5)).fx(vfx.fadein, 0.1).fx(vfx.fadeout, 0.1)
        elif transition == 'smooth_fade':
            trimmed = trimmed.fx(vfx.fadein, 0.3).fx(vfx.fadeout, 0.3)
        elif transition == 'dramatic_fade':
            trimmed = trimmed.fx(vfx.fadein, 0.1).fx(vfx.fadeout, 0.5)
        elif transition == 'zoom_blur':
            trimmed = trimmed.fx(vfx.resize, lambda t: 1 + 0.15 * t).fx(vfx.fadein, 0.2).fx(vfx.fadeout, 0.2)
        elif transition == 'gentle_zoom':
            trimmed = trimmed.fx(vfx.resize, lambda t: 1 + 0.05 * t).fx(vfx.fadein, 0.15).fx(vfx.fadeout, 0.15)
        
        final_clips.append(trimmed)
        
        current_time += actual_duration
        clip_idx += 1

    if not final_clips:
        print("❌ No usable clips after trimming!")
        return

    final_video = concatenate_videoclips(final_clips, method="compose")
    audio = AudioFileClip(audio_path)
    final_video = final_video.set_audio(audio)

    print(f"💾 Exporting final reel to {output_path}...")
    final_video.write_videofile(output_path, fps=30, codec="libx264", audio_codec="aac", preset="ultrafast")
    print("✅ Reel video editing complete!")

if __name__ == "__main__":
    audio_path = input("Enter path to your audio file: ").strip().strip('"').strip("'")
    videos_folder = input("Enter path to your videos folder: ").strip().strip('"').strip("'")
    beat_synced_reel(audio_path, videos_folder)
