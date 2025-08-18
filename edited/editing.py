import os
from moviepy.editor import *
import librosa

# Fix for PIL.Image ANTIALIAS deprecation
try:
    from PIL import Image
    if not hasattr(Image, 'ANTIALIAS'):
        Image.ANTIALIAS = Image.LANCZOS
except ImportError:
    pass

def beat_synced_reel(audio_path, videos_folder, output_path="final_reel.mp4"):
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
