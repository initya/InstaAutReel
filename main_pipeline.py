#!/usr/bin/env python3
"""
Main Pipeline for Instagram Reel Creation
Streamlines the workflow: Gemini Voice → Content Download → Video Editing → Subtitles
"""

import os
import sys
import json
import time
import shutil
import requests
from pathlib import Path
import subprocess

# Import configuration
from config import *

# Project directories (used for dynamic imports)
# Note: Python path is managed dynamically in each step to avoid conflicts

class ReelPipeline:
    def __init__(self):
        self.base_dir = BASE_DIR
        self.gemini_dir = GEMINI_DIR
        self.content_dir = CONTENT_DIR
        self.edited_dir = EDITED_DIR
        
        # Create output directories
        self.output_dir = OUTPUT_DIR
        self.output_dir.mkdir(exist_ok=True)
        
        # Pipeline state
        self.current_script = None
        self.current_audio = None
        self.current_keywords = None
        self.current_videos = []
        self.final_video = None
        
        # Check dependencies
        self.check_dependencies()
    
    def check_dependencies(self):
        """Check if required packages are installed"""
        print("🔍 Checking dependencies...")
        
        missing_packages = []
        
        # Check core packages
        try:
            import flask
            print("✅ Flask installed")
        except ImportError:
            missing_packages.append("flask")
        
        try:
            import requests
            print("✅ Requests installed")
        except ImportError:
            missing_packages.append("requests")
        
        # Check video processing packages
        try:
            import moviepy
            print("✅ MoviePy installed")
        except ImportError:
            missing_packages.append("moviepy")
            print("❌ MoviePy not installed - video editing will fail")
        
        try:
            import librosa
            print("✅ Librosa installed")
        except ImportError:
            missing_packages.append("librosa")
            print("❌ Librosa not installed - audio processing will fail")
        
        # Check AI packages
        try:
            import google.generativeai
            print("✅ Google Generative AI installed")
        except ImportError:
            missing_packages.append("google-generativeai")
            print("❌ Google Generative AI not installed - voice generation will fail")
        
        try:
            import faster_whisper
            print("✅ Faster Whisper installed")
        except ImportError:
            missing_packages.append("faster-whisper")
            print("❌ Faster Whisper not installed - subtitle generation will fail")
        
        if missing_packages:
            print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
            print("💡 Install with: pip install -r requirements.txt")
            print("💡 Or use: run_pipeline.bat (Windows)")
        else:
            print("✅ All required packages are installed!")
        
        print()
        
    def step1_generate_voice(self, custom_prompt=None):
        """Step 1: Generate TTS script and audio using Gemini"""
        print("🎤 Step 1: Generating Voice with Gemini...")
        print("=" * 50)
        
        try:
            # Import Gemini app functions
            # Reset Python path to avoid conflicts
            original_path = sys.path.copy()
            sys.path = [str(self.gemini_dir)] + original_path
            
            # Clear any cached imports to avoid conflicts
            if 'app' in sys.modules:
                del sys.modules['app']
            
            print(f"🔍 Importing from: {self.gemini_dir}")
            print(f"🔍 Python path: {sys.path[:3]}...")  # Show first 3 paths
            
            from app import generate_tts_script_and_audio
            
            # Generate TTS
            result = generate_tts_script_and_audio(custom_prompt=custom_prompt)
            
            if not result.get('success'):
                raise Exception(f"Voice generation failed: {result.get('error')}")
            
            # Store results
            self.current_script = result['script']
            self.current_keywords = result['keywords']
            self.current_audio = result['filename']
            
            # Move audio to output directory
            if os.path.exists(self.current_audio):
                new_audio_path = self.output_dir / f"generated_audio_{int(time.time())}.wav"
                shutil.move(self.current_audio, new_audio_path)
                self.current_audio = str(new_audio_path)
            
            print(f"✅ Voice generated successfully!")
            print(f"📝 Script: {len(self.current_script)} characters")
            print(f"🎵 Audio: {self.current_audio}")
            print(f"🔑 Keywords: {', '.join(self.current_keywords[:5])}...")
            
            # Restore original Python path
            sys.path = original_path
            
            return True
            
        except Exception as e:
            print(f"❌ Voice generation failed: {e}")
            # Restore original Python path even on error
            sys.path = original_path
            return False
    
    def step2_download_content(self, videos_per_keyword=None):
        if videos_per_keyword is None:
            videos_per_keyword = CONTENT_CONFIG['videos_per_keyword']
        """Step 2: Download videos based on generated keywords"""
        print("\n🎬 Step 2: Downloading Content Videos...")
        print("=" * 50)
        
        try:
            # Import content app functions
            # Reset Python path to avoid conflicts
            original_path = sys.path.copy()
            sys.path = [str(self.content_dir)] + original_path
            
            # Clear any cached imports to avoid conflicts
            if 'app' in sys.modules:
                del sys.modules['app']
            
            print(f"🔍 Importing from: {self.content_dir}")
            print(f"🔍 Python path: {sys.path[:3]}...")  # Show first 3 paths
            
            from app import search_and_download_videos_direct
            
            # Create videos directory in output
            videos_dir = self.output_dir / "videos"
            videos_dir.mkdir(exist_ok=True)
            
            # Download videos for each keyword
            for keyword in self.current_keywords:
                print(f"🔍 Searching for videos: '{keyword}'")
                
                # Call the direct download function
                success = search_and_download_videos_direct(keyword, per_page=videos_per_keyword)
                if not success:
                    print(f"⚠️  Failed to download videos for keyword: {keyword}")
                
                # Wait a bit to avoid API rate limits
                time.sleep(CONTENT_CONFIG['api_delay'])
            
            # Move downloaded videos to output directory
            content_videos_dir = self.content_dir / "videos"
            print(f"🔍 Checking for videos in: {content_videos_dir}")
            
            if content_videos_dir.exists():
                video_files = list(content_videos_dir.glob("*.mp4"))
                print(f"🔍 Found {len(video_files)} video files in content directory")
                
                for video_file in video_files:
                    print(f"🔍 Moving video: {video_file.name}")
                    new_path = videos_dir / video_file.name
                    try:
                        shutil.move(str(video_file), str(new_path))
                        self.current_videos.append(str(new_path))
                        print(f"✅ Moved: {video_file.name}")
                    except Exception as move_error:
                        print(f"⚠️  Failed to move {video_file.name}: {move_error}")
                        # Try copying instead of moving
                        try:
                            shutil.copy2(str(video_file), str(new_path))
                            self.current_videos.append(str(new_path))
                            print(f"✅ Copied: {video_file.name}")
                        except Exception as copy_error:
                            print(f"❌ Failed to copy {video_file.name}: {copy_error}")
            else:
                print(f"⚠️  Content videos directory does not exist: {content_videos_dir}")
            
            print(f"✅ Content downloaded successfully!")
            print(f"📹 Videos: {len(self.current_videos)} files")
            
            # Restore original Python path
            sys.path = original_path
            
            return True
            
        except Exception as e:
            print(f"❌ Content download failed: {e}")
            import traceback
            print(f"🔍 Full error details:")
            traceback.print_exc()
            # Restore original Python path even on error
            sys.path = original_path
            return False
    
    def step3_edit_video(self):
        """Step 3: Edit video with beat-sync and transitions"""
        print("\n✂️ Step 3: Editing Video with Beat-Sync...")
        print("=" * 50)
        
        try:
            # Import editing functions
            # Reset Python path to avoid conflicts
            original_path = sys.path.copy()
            sys.path = [str(self.edited_dir)] + original_path
            
            # Clear any cached imports to avoid conflicts
            if 'editing' in sys.modules:
                del sys.modules['editing']
            
            from editing import beat_synced_reel
            
            # Prepare paths
            audio_path = self.current_audio
            videos_folder = str(self.output_dir / "videos")
            output_path = str(self.output_dir / "final_reel_transitions.mp4")
            
            # Check if we have the required files
            if not os.path.exists(audio_path):
                raise Exception(f"Audio file not found: {audio_path}")
            
            if not os.path.exists(videos_folder) or not os.listdir(videos_folder):
                raise Exception(f"No videos found in: {videos_folder}")
            
            # Run video editing
            beat_synced_reel(audio_path, videos_folder, output_path)
            
            if os.path.exists(output_path):
                self.final_video = output_path
                print(f"✅ Video editing completed!")
                print(f"🎬 Final video: {self.final_video}")
                
                # Restore original Python path
                sys.path = original_path
                
                return True
            else:
                raise Exception("Video editing failed - no output file generated")
                
        except Exception as e:
            print(f"❌ Video editing failed: {e}")
            # Restore original Python path even on error
            sys.path = original_path
            return False
    
    def step4_generate_subtitles(self):
        """Step 4: Generate subtitles for the final video"""
        print("\n📝 Step 4: Generating Subtitles...")
        print("=" * 50)
        
        try:
            # Import subtitle functions
            # Reset Python path to avoid conflicts
            original_path = sys.path.copy()
            sys.path = [str(self.edited_dir)] + original_path
            
            # Clear any cached imports to avoid conflicts
            if 'generate_subtitles' in sys.modules:
                del sys.modules['generate_subtitles']
            
            from generate_subtitles import transcribe_audio, create_hard_subtitles
            
            # Prepare paths
            video_path = self.final_video
            srt_path = str(self.output_dir / "final_reel_transitions_subtitles.srt")
            hard_sub_path = str(self.output_dir / "final_reel_transitions_subtitles.mp4")
            
            # Generate SRT subtitles
            print("🎯 Transcribing audio...")
            if not transcribe_audio(self.current_audio, model_size=SUBTITLE_CONFIG['model_size'], output_srt=srt_path):
                raise Exception("Failed to generate SRT subtitles")
            
            # Create hard-burned subtitles
            print("🔥 Creating hard-burned subtitles...")
            if not create_hard_subtitles(video_path, srt_path, hard_sub_path):
                raise Exception("Failed to create hard-burned subtitles")
            
            print(f"✅ Subtitles generated successfully!")
            print(f"📝 SRT file: {srt_path}")
            print(f"🎬 Final video with subtitles: {hard_sub_path}")
            
            # Restore original Python path
            sys.path = original_path
            
            return True
            
        except Exception as e:
            print(f"❌ Subtitle generation failed: {e}")
            import traceback
            print(f"🔍 Full error details:")
            traceback.print_exc()
            # Restore original Python path even on error
            sys.path = original_path
            return False
    
    def run_full_pipeline(self, custom_prompt=None, videos_per_keyword=2):
        """Run the complete pipeline"""
        print("🚀 Starting Instagram Reel Creation Pipeline")
        print("=" * 60)
        print(f"📁 Output directory: {self.output_dir}")
        print(f"🎬 Videos per keyword: {videos_per_keyword}")
        print("=" * 60)
        
        start_time = time.time()
        
        # Step 1: Generate voice
        if not self.step1_generate_voice(custom_prompt):
            print("❌ Pipeline failed at Step 1")
            return False
        
        # Step 2: Download content
        if not self.step2_download_content(videos_per_keyword):
            print("❌ Pipeline failed at Step 2")
            return False
        
        # Step 3: Edit video
        if not self.step3_edit_video():
            print("❌ Pipeline failed at Step 3")
            return False
        
        # Step 4: Generate subtitles
        if not self.step4_generate_subtitles():
            print("❌ Pipeline failed at Step 4")
            return False
        
        # Pipeline completed successfully
        total_time = time.time() - start_time
        print("\n" + "=" * 60)
        print("🎉 PIPELINE COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"⏱️  Total time: {total_time:.2f} seconds")
        print(f"📁 Output directory: {self.output_dir}")
        print(f"🎬 Final video with subtitles: {self.output_dir}/final_reel_transitions_subtitles.mp4")
        print(f"📝 SRT subtitles: {self.output_dir}/final_reel_transitions_subtitles.srt")
        print("=" * 60)
        
        return True
    
    def cleanup(self):
        """Clean up temporary files"""
        print("\n🧹 Cleaning up temporary files...")
        
        # Remove temporary audio file
        if self.current_audio and os.path.exists(self.current_audio):
            try:
                os.remove(self.current_audio)
                print("✅ Cleaned up temporary audio")
            except:
                pass
        
        # Remove intermediate video files (only if we have successfully created the final video with subtitles)
        final_video_with_subs = str(self.output_dir / "final_reel_transitions_subtitles.mp4")
        if os.path.exists(final_video_with_subs) and self.final_video and os.path.exists(self.final_video):
            try:
                # Check file size to ensure the subtitled video is valid
                sub_file_size = os.path.getsize(final_video_with_subs)
                if sub_file_size > 1024:  # At least 1KB
                    os.remove(self.final_video)
                    print("✅ Cleaned up intermediate video")
                else:
                    print("⚠️  Keeping intermediate video (subtitled version appears invalid)")
            except:
                pass

def main():
    """Main function with interactive interface"""
    print("🎬 Instagram Reel Creation Pipeline")
    print("=" * 50)
    
    # Initialize pipeline
    pipeline = ReelPipeline()
    
    # Get user input
    print("\nOptions:")
    print("1. Use default prompt (random facts/story)")
    print("2. Use custom prompt")
    print("3. Exit")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        custom_prompt = None
    elif choice == "2":
        custom_prompt = input("Enter your custom prompt: ").strip()
        if not custom_prompt:
            print("❌ No prompt provided, using default")
            custom_prompt = None
    elif choice == "3":
        print("👋 Goodbye!")
        return
    else:
        print("❌ Invalid choice, using default")
        custom_prompt = None
    
    # Get videos per keyword
    try:
        default_videos = CONTENT_CONFIG['videos_per_keyword']
        videos_per_keyword = int(input(f"Videos per keyword (default: {default_videos}): ").strip() or str(default_videos))
    except ValueError:
        videos_per_keyword = CONTENT_CONFIG['videos_per_keyword']
    
    # Run pipeline
    try:
        success = pipeline.run_full_pipeline(custom_prompt, videos_per_keyword)
        if success:
            print("\n🎉 Your Instagram reel is ready!")
        else:
            print("\n❌ Pipeline failed. Check the logs above.")
    except KeyboardInterrupt:
        print("\n\n⏹️  Pipeline interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    finally:
        # Cleanup
        pipeline.cleanup()

if __name__ == "__main__":
    main()
