#!/usr/bin/env python3
"""
Streamlit Frontend for Instagram Reel Creation Pipeline
A comprehensive web interface with live updates and video playback
"""

import streamlit as st
import os
import sys
import time
import json
import subprocess
import shutil
import threading
from pathlib import Path
import queue
import uuid
from datetime import datetime
import base64

# Add project paths for imports
BASE_DIR = Path(__file__).parent
GEMINI_DIR = BASE_DIR / "gemini voice"
CONTENT_DIR = BASE_DIR / "cont"
EDITED_DIR = BASE_DIR / "edited"
OUTPUT_DIR = BASE_DIR / "output"

# Import configurations
sys.path.insert(0, str(BASE_DIR))
from config import *

# Custom CSS for better UI
st.set_page_config(
    page_title="🎬 Instagram Reel Creator",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    .step-container {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .error-box {
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .progress-box {
        background: #cce5ff;
        border: 1px solid #99ccff;
        color: #004080;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 25px;
        font-weight: bold;
    }
    .video-container {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'pipeline_status' not in st.session_state:
    st.session_state.pipeline_status = {
        'step': 0,
        'status': 'ready',
        'message': 'Ready to start',
        'results': {},
        'progress': 0,
        'current_task': '',
        'task_queue': queue.Queue(),
        'pipeline_thread': None,
        'output_files': {}
    }

if 'generated_content' not in st.session_state:
    st.session_state.generated_content = {
        'script': '',
        'keywords': [],
        'audio_file': '',
        'video_files': [],
        'final_video': '',
        'subtitled_video': ''
    }

class StreamlitPipeline:
    def __init__(self, task_queue):
        self.task_queue = task_queue
        self.base_dir = BASE_DIR
        self.gemini_dir = GEMINI_DIR
        self.content_dir = CONTENT_DIR
        self.edited_dir = EDITED_DIR
        self.output_dir = OUTPUT_DIR
        self.output_dir.mkdir(exist_ok=True)
        
        # Pipeline state
        self.current_script = None
        self.current_audio = None
        self.current_keywords = None
        self.current_videos = []
        self.final_video = None

    def update_status(self, step, status, message, progress=0, current_task=''):
        """Update pipeline status for UI"""
        status_update = {
            'step': step,
            'status': status,
            'message': message,
            'progress': progress,
            'current_task': current_task,
            'timestamp': datetime.now().isoformat()
        }
        self.task_queue.put(status_update)
        
    def step1_generate_voice(self, custom_prompt=None):
        """Step 1: Generate TTS script and audio using Gemini"""
        self.update_status(1, 'running', '🎤 Generating AI voice script and audio...', 10, 'Connecting to Gemini AI')
        
        try:
            # Import Gemini app functions
            original_path = sys.path.copy()
            sys.path.insert(0, str(self.gemini_dir))
            
            # Clear any cached app modules to avoid conflicts
            modules_to_clear = [key for key in sys.modules.keys() if key.startswith('app')]
            for module in modules_to_clear:
                if module in sys.modules:
                    del sys.modules[module]
            
            import importlib.util
            spec = importlib.util.spec_from_file_location("gemini_app", self.gemini_dir / "app.py")
            gemini_app = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(gemini_app)
            
            generate_tts_script_and_audio = gemini_app.generate_tts_script_and_audio
            
            self.update_status(1, 'running', '🎤 Generating script with Gemini AI...', 25, 'Creating engaging content')
            
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
                timestamp = int(time.time())
                new_audio_path = self.output_dir / f"generated_audio_{timestamp}.wav"
                shutil.move(self.current_audio, new_audio_path)
                self.current_audio = str(new_audio_path)
            
            self.update_status(1, 'completed', '✅ Voice generation completed!', 100, 
                             f'Generated {len(self.current_script)} character script with {len(self.current_keywords)} keywords')
            
            # Restore original Python path
            sys.path = original_path
            
            return True
            
        except Exception as e:
            self.update_status(1, 'error', f'❌ Voice generation failed: {str(e)}', 0, 'Error in AI generation')
            sys.path = original_path
            return False
    
    def step2_download_content(self, videos_per_keyword=2):
        """Step 2: Download videos based on generated keywords"""
        self.update_status(2, 'running', '🎬 Downloading stock videos from Pexels...', 10, 'Searching for relevant content')
        
        try:
            # Import content app functions
            original_path = sys.path.copy()
            sys.path.insert(0, str(self.content_dir))
            
            # Clear any cached app modules to avoid conflicts
            modules_to_clear = [key for key in sys.modules.keys() if key.startswith('app')]
            for module in modules_to_clear:
                if module in sys.modules:
                    del sys.modules[module]
            
            import importlib.util
            spec = importlib.util.spec_from_file_location("content_app", self.content_dir / "app.py")
            content_app = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(content_app)
            
            search_and_download_videos_direct = content_app.search_and_download_videos_direct
            
            # Create videos directory in output
            videos_dir = self.output_dir / "videos"
            videos_dir.mkdir(exist_ok=True)
            
            total_keywords = len(self.current_keywords)
            
            # Download videos for each keyword
            for idx, keyword in enumerate(self.current_keywords):
                progress = 20 + (60 * idx / total_keywords)
                self.update_status(2, 'running', f'🔍 Searching for videos: "{keyword}"', 
                                 progress, f'Downloading videos for keyword {idx+1}/{total_keywords}')
                
                # Call the direct download function
                success = search_and_download_videos_direct(keyword, per_page=videos_per_keyword)
                if not success:
                    self.update_status(2, 'warning', f'⚠️ Failed to download videos for keyword: {keyword}', 
                                     progress, f'Skipping keyword: {keyword}')
                
                # Wait to avoid API rate limits
                time.sleep(CONTENT_CONFIG['api_delay'])
            
            # Move downloaded videos to output directory
            content_videos_dir = self.content_dir / "videos"
            
            if content_videos_dir.exists():
                video_files = list(content_videos_dir.glob("*.mp4"))
                
                for video_file in video_files:
                    new_path = videos_dir / video_file.name
                    try:
                        shutil.move(str(video_file), str(new_path))
                        self.current_videos.append(str(new_path))
                    except Exception:
                        try:
                            shutil.copy2(str(video_file), str(new_path))
                            self.current_videos.append(str(new_path))
                        except Exception as e:
                            continue
            
            self.update_status(2, 'completed', '✅ Content download completed!', 100, 
                             f'Downloaded {len(self.current_videos)} video files')
            
            # Restore original Python path
            sys.path = original_path
            
            return True
            
        except Exception as e:
            self.update_status(2, 'error', f'❌ Content download failed: {str(e)}', 0, 'Error downloading videos')
            sys.path = original_path
            return False
    
    def step3_edit_video(self):
        """Step 3: Edit video with beat-sync and transitions"""
        self.update_status(3, 'running', '✂️ Creating beat-synced video with transitions...', 10, 'Analyzing audio beats')
        
        try:
            # Import editing functions
            original_path = sys.path.copy()
            sys.path.insert(0, str(self.edited_dir))
            
            # Clear any cached editing modules to avoid conflicts
            modules_to_clear = [key for key in sys.modules.keys() if key.startswith('editing')]
            for module in modules_to_clear:
                if module in sys.modules:
                    del sys.modules[module]
            
            import importlib.util
            spec = importlib.util.spec_from_file_location("editing_module", self.edited_dir / "editing.py")
            editing_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(editing_module)
            
            beat_synced_reel = editing_module.beat_synced_reel
            
            # Prepare paths
            audio_path = self.current_audio
            videos_folder = str(self.output_dir / "videos")
            output_path = str(self.output_dir / "final_reel_transitions.mp4")
            
            # Check if we have the required files
            if not os.path.exists(audio_path):
                raise Exception(f"Audio file not found: {audio_path}")
            
            if not os.path.exists(videos_folder) or not os.listdir(videos_folder):
                raise Exception(f"No videos found in: {videos_folder}")
            
            self.update_status(3, 'running', '🎵 Analyzing audio beats and tempo...', 25, 'Processing audio')
            time.sleep(1)  # Simulate processing time for UI
            
            self.update_status(3, 'running', '✂️ Cutting and arranging video clips...', 50, 'Applying transitions')
            
            # Run video editing
            beat_synced_reel(audio_path, videos_folder, output_path)
            
            if os.path.exists(output_path):
                self.final_video = output_path
                self.update_status(3, 'completed', '✅ Video editing completed!', 100, 
                                 f'Created {os.path.getsize(output_path) / (1024*1024):.2f} MB video')
                
                # Restore original Python path
                sys.path = original_path
                
                return True
            else:
                raise Exception("Video editing failed - no output file generated")
                
        except Exception as e:
            self.update_status(3, 'error', f'❌ Video editing failed: {str(e)}', 0, 'Error in video processing')
            sys.path = original_path
            return False
    
    def step4_generate_subtitles(self):
        """Step 4: Generate subtitles for the final video"""
        self.update_status(4, 'running', '📝 Generating AI subtitles...', 10, 'Initializing speech recognition')
        
        try:
            # Import subtitle functions
            original_path = sys.path.copy()
            sys.path.insert(0, str(self.edited_dir))
            
            # Clear any cached subtitle modules to avoid conflicts
            modules_to_clear = [key for key in sys.modules.keys() if key.startswith('generate_subtitles')]
            for module in modules_to_clear:
                if module in sys.modules:
                    del sys.modules[module]
            
            import importlib.util
            spec = importlib.util.spec_from_file_location("subtitle_module", self.edited_dir / "generate_subtitles.py")
            subtitle_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(subtitle_module)
            
            transcribe_audio = subtitle_module.transcribe_audio
            create_hard_subtitles = subtitle_module.create_hard_subtitles
            
            # Prepare paths
            video_path = self.final_video
            srt_path = str(self.output_dir / "final_reel_transitions_subtitles.srt")
            hard_sub_path = str(self.output_dir / "final_reel_transitions_subtitles.mp4")
            
            # Generate SRT subtitles
            self.update_status(4, 'running', '🎯 Transcribing audio with AI...', 30, 'Processing speech-to-text')
            
            if not transcribe_audio(self.current_audio, model_size=SUBTITLE_CONFIG['model_size'], output_srt=srt_path):
                raise Exception("Failed to generate SRT subtitles")
            
            # Create hard-burned subtitles
            self.update_status(4, 'running', '🔥 Burning subtitles into video...', 70, 'Rendering final video')
            
            if not create_hard_subtitles(video_path, srt_path, hard_sub_path):
                raise Exception("Failed to create hard-burned subtitles")
            
            self.update_status(4, 'completed', '✅ Subtitles generated successfully!', 100, 
                             f'Final video ready: {os.path.getsize(hard_sub_path) / (1024*1024):.2f} MB')
            
            # Restore original Python path
            sys.path = original_path
            
            return True
            
        except Exception as e:
            self.update_status(4, 'error', f'❌ Subtitle generation failed: {str(e)}', 0, 'Error in subtitle processing')
            sys.path = original_path
            return False
    
    def run_full_pipeline(self, custom_prompt=None, videos_per_keyword=2):
        """Run the complete pipeline"""
        self.update_status(0, 'running', '🚀 Starting Instagram Reel Creation Pipeline...', 0, 'Initializing')
        
        start_time = time.time()
        
        # Step 1: Generate voice
        if not self.step1_generate_voice(custom_prompt):
            return False
        
        # Step 2: Download content
        if not self.step2_download_content(videos_per_keyword):
            return False
        
        # Step 3: Edit video
        if not self.step3_edit_video():
            return False
        
        # Step 4: Generate subtitles
        if not self.step4_generate_subtitles():
            return False
        
        # Pipeline completed successfully
        total_time = time.time() - start_time
        self.update_status(5, 'completed', '🎉 PIPELINE COMPLETED SUCCESSFULLY!', 100, 
                         f'Total time: {total_time:.2f} seconds')
        
        return True

def run_pipeline_thread(custom_prompt, videos_per_keyword, task_queue):
    """Run pipeline in background thread"""
    pipeline = StreamlitPipeline(task_queue)
    success = pipeline.run_full_pipeline(custom_prompt, videos_per_keyword)
    
    # Store results in task queue for main thread to process
    if success:
        results = {
            'type': 'results',
            'script': pipeline.current_script,
            'keywords': pipeline.current_keywords,
            'audio_file': pipeline.current_audio,
            'video_files': pipeline.current_videos,
            'final_video': pipeline.final_video,
            'subtitled_video': str(OUTPUT_DIR / "final_reel_transitions_subtitles.mp4")
        }
        task_queue.put(results)

def get_video_player(video_path):
    """Get video player for Streamlit"""
    if not os.path.exists(video_path):
        return None
    
    # Check file size - if too large, use Streamlit's built-in video player
    file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
    
    if file_size > 50:  # If larger than 50MB, use file path
        return {'type': 'file', 'path': video_path}
    else:
        # For smaller files, use base64 encoding
        try:
            with open(video_path, "rb") as video_file:
                video_bytes = video_file.read()
                video_base64 = base64.b64encode(video_bytes).decode()
            return {'type': 'base64', 'data': video_base64}
        except Exception as e:
            print(f"Error encoding video: {e}")
            return {'type': 'file', 'path': video_path}

def main():
    # Main header
    st.markdown("""
    <div class="main-header">
        <h1 style="color: white; margin: 0;">🎬 Instagram Reel Creator</h1>
        <p style="color: white; margin: 0.5rem 0 0 0;">AI-Powered Video Creation Pipeline with Live Updates</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for controls
    with st.sidebar:
        st.header("🎛️ Controls")
        
        # Pipeline configuration
        st.subheader("Pipeline Settings")
        
        custom_prompt = st.text_area(
            "Custom Prompt (Optional)", 
            placeholder="Enter a custom prompt for AI script generation, or leave empty for random content...",
            height=100
        )
        
        videos_per_keyword = st.slider(
            "Videos per Keyword", 
            min_value=1, 
            max_value=5, 
            value=2,
            help="Number of stock videos to download for each keyword"
        )
        
        # Pipeline control buttons
        st.subheader("Pipeline Control")
        
        col1, col2 = st.columns(2)
        
        with col1:
            start_pipeline = st.button("🚀 Start Pipeline", type="primary")
        
        with col2:
            stop_pipeline = st.button("⏹️ Stop", type="secondary")
            
        # Handle stop pipeline
        if stop_pipeline:
            if st.session_state.pipeline_status['status'] == 'running':
                st.session_state.pipeline_status['status'] = 'stopped'
                st.session_state.pipeline_status['message'] = 'Pipeline stopped by user'
                st.warning("Pipeline stop requested. Current operations will finish gracefully.")
                st.rerun()
            else:
                st.info("No active pipeline to stop.")
        
        # Reset button
        if st.button("🔄 Reset"):
            st.session_state.pipeline_status = {
                'step': 0,
                'status': 'ready',
                'message': 'Ready to start',
                'results': {},
                'progress': 0,
                'current_task': '',
                'task_queue': queue.Queue(),
                'pipeline_thread': None,
                'output_files': {}
            }
            st.session_state.generated_content = {
                'script': '',
                'keywords': [],
                'audio_file': '',
                'video_files': [],
                'final_video': '',
                'subtitled_video': ''
            }
            st.rerun()
        
        # System status
        st.subheader("System Status")
        st.info(f"📊 Status: {st.session_state.pipeline_status['status'].title()}")
        st.info(f"📍 Step: {st.session_state.pipeline_status['step']}/4")
        
        # Output directory info
        if OUTPUT_DIR.exists():
            output_files = list(OUTPUT_DIR.glob("*"))
            st.info(f"📁 Output Files: {len(output_files)}")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Pipeline Status Section
        st.header("📊 Pipeline Status")
        
        # Check for status updates
        if not st.session_state.pipeline_status['task_queue'].empty():
            try:
                while not st.session_state.pipeline_status['task_queue'].empty():
                    status_update = st.session_state.pipeline_status['task_queue'].get_nowait()
                    
                    # Handle different types of updates
                    if isinstance(status_update, dict) and status_update.get('type') == 'results':
                        # Update generated content with results
                        st.session_state.generated_content.update({
                            'script': status_update.get('script', ''),
                            'keywords': status_update.get('keywords', []),
                            'audio_file': status_update.get('audio_file', ''),
                            'video_files': status_update.get('video_files', []),
                            'final_video': status_update.get('final_video', ''),
                            'subtitled_video': status_update.get('subtitled_video', '')
                        })
                    else:
                        # Regular status update
                        st.session_state.pipeline_status.update(status_update)
            except queue.Empty:
                pass
        
        # Display current status
        status = st.session_state.pipeline_status['status']
        message = st.session_state.pipeline_status['message']
        progress = st.session_state.pipeline_status['progress']
        current_task = st.session_state.pipeline_status['current_task']
        
        if status == 'running':
            st.markdown(f'<div class="progress-box"><strong>{message}</strong><br>🔄 {current_task}</div>', 
                       unsafe_allow_html=True)
            st.progress(progress / 100)
        elif status == 'completed':
            st.markdown(f'<div class="success-box"><strong>{message}</strong><br>✅ {current_task}</div>', 
                       unsafe_allow_html=True)
            if progress > 0:
                st.progress(progress / 100)
        elif status == 'error':
            st.markdown(f'<div class="error-box"><strong>{message}</strong><br>❌ {current_task}</div>', 
                       unsafe_allow_html=True)
        else:
            st.info(f"💡 {message}")
        
        # Pipeline Steps Overview
        st.subheader("🔄 Pipeline Steps")
        
        steps = [
            ("🎤 AI Voice Generation", "Generate script and TTS audio using Gemini AI"),
            ("🎬 Stock Video Download", "Download relevant videos from Pexels API"),
            ("✂️ Video Editing", "Create beat-synced reel with transitions"),
            ("📝 Subtitle Generation", "Add AI-generated subtitles to final video")
        ]
        
        current_step = st.session_state.pipeline_status['step']
        
        for i, (title, description) in enumerate(steps, 1):
            if i < current_step:
                st.success(f"✅ Step {i}: {title}")
            elif i == current_step and status == 'running':
                st.info(f"🔄 Step {i}: {title} (In Progress)")
            elif i == current_step and status == 'completed':
                st.success(f"✅ Step {i}: {title} (Completed)")
            elif i == current_step and status == 'error':
                st.error(f"❌ Step {i}: {title} (Failed)")
            else:
                st.text(f"⏳ Step {i}: {title}")
    
    with col2:
        # Live Results Section
        st.header("📋 Live Results")
        
        # Display generated content
        if st.session_state.generated_content['script']:
            with st.expander("📝 Generated Script", expanded=True):
                st.text_area("Script Content", st.session_state.generated_content['script'], height=150, disabled=True)
        
        if st.session_state.generated_content['keywords']:
            with st.expander("🔑 Extracted Keywords", expanded=True):
                st.write(", ".join(st.session_state.generated_content['keywords']))
        
        if st.session_state.generated_content['audio_file'] and os.path.exists(st.session_state.generated_content['audio_file']):
            with st.expander("🎵 Generated Audio", expanded=True):
                st.audio(st.session_state.generated_content['audio_file'])
        
        if st.session_state.generated_content['video_files']:
            with st.expander("🎬 Downloaded Videos", expanded=True):
                st.write(f"✅ {len(st.session_state.generated_content['video_files'])} videos downloaded")
                for video_file in st.session_state.generated_content['video_files'][:3]:  # Show first 3
                    if os.path.exists(video_file):
                        st.write(f"📹 {os.path.basename(video_file)}")
    
    # Final Video Display Section
    if st.session_state.generated_content['subtitled_video'] and os.path.exists(st.session_state.generated_content['subtitled_video']):
        st.header("🎬 Final Instagram Reel")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            # Display video player
            video_data = get_video_player(st.session_state.generated_content['subtitled_video'])
            
            if video_data:
                if video_data['type'] == 'file':
                    # Use Streamlit's built-in video player for large files
                    st.video(video_data['path'])
                else:
                    # Use HTML5 video player for smaller files with custom styling
                    video_html = f"""
                    <div class="video-container">
                        <video width="100%" height="auto" controls style="border-radius: 10px;">
                            <source src="data:video/mp4;base64,{video_data['data']}" type="video/mp4">
                            Your browser does not support the video tag.
                        </video>
                    </div>
                    """
                    st.markdown(video_html, unsafe_allow_html=True)
            else:
                st.error("Video file not found or corrupted")
            
            # Download button
            with open(st.session_state.generated_content['subtitled_video'], "rb") as file:
                st.download_button(
                    label="📥 Download Final Video",
                    data=file.read(),
                    file_name="instagram_reel_final.mp4",
                    mime="video/mp4",
                    type="primary"
                )
        
        # Video information
        st.subheader("📊 Video Information")
        video_path = st.session_state.generated_content['subtitled_video']
        file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("File Size", f"{file_size:.2f} MB")
        with col2:
            st.metric("Resolution", "1080x1920")
        with col3:
            st.metric("Format", "MP4")
        with col4:
            st.metric("Subtitles", "Hard-burned")
    
    # Start pipeline
    if start_pipeline:
        # Check if API keys are configured
        if not GEMINI_API_KEY or GEMINI_API_KEY == "your_api_key_here":
            st.error("❌ Gemini API key not configured! Please set GEMINI_API_KEY in config.py")
        elif not PEXELS_API_KEY or PEXELS_API_KEY == "your_api_key_here":
            st.error("❌ Pexels API key not configured! Please set PEXELS_API_KEY in config.py")
        elif st.session_state.pipeline_status['status'] == 'running':
            st.warning("Pipeline is already running!")
        else:
            # Check if previous thread is still alive
            prev_thread = st.session_state.pipeline_status.get('pipeline_thread')
            if prev_thread and prev_thread.is_alive():
                st.warning("Previous pipeline is still finishing. Please wait or reset.")
            else:
                st.session_state.pipeline_status = {
                    'step': 0,
                    'status': 'running',
                    'message': 'Starting pipeline...',
                    'results': {},
                    'progress': 0,
                    'current_task': 'Initializing',
                    'task_queue': queue.Queue(),
                    'pipeline_thread': None,
                    'output_files': {}
                }
                
                # Start pipeline in background thread
                pipeline_thread = threading.Thread(
                    target=run_pipeline_thread, 
                    args=(custom_prompt or None, videos_per_keyword, st.session_state.pipeline_status['task_queue']),
                    daemon=True
                )
                pipeline_thread.start()
                st.session_state.pipeline_status['pipeline_thread'] = pipeline_thread
                
                st.success("🚀 Pipeline started! Watch the progress above.")
                st.rerun()
    
    # Auto-refresh while pipeline is running
    if st.session_state.pipeline_status['status'] == 'running':
        time.sleep(2)
        st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; margin-top: 2rem;">
        <p>🎬 Instagram Reel Creator | Powered by Gemini AI, Pexels API, and Streamlit</p>
        <p>📧 Need help? Check the console for detailed logs</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
