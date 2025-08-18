"""
Configuration file for the Instagram Reel Creation Pipeline
Centralizes all settings and parameters for easy customization
"""

import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent
GEMINI_DIR = BASE_DIR / "gemini voice"
CONTENT_DIR = BASE_DIR / "cont"
EDITED_DIR = BASE_DIR / "edited"
OUTPUT_DIR = BASE_DIR / "output"

# API Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', "AIzaSyBMi7RqQdtvSjqGJFKePfEuAmbojFksIcc")
PEXELS_API_KEY = os.getenv('PEXELS_API_KEY', "TOv7wzLAVTXwkt00DMN5vqcqjuwtH2iv5oMQFVWfX2vNc9IvlihKDQiV")

# Voice Generation Settings
VOICE_CONFIG = {
    'model': 'gemini-2.5-flash',
    'tts_model': 'gemini-2.5-flash-preview-tts',
    'voice_name': 'Kore',
    'script_length': '30-second',
    'include_emotions': True,
    'include_sound_effects': True
}

# Content Download Settings
CONTENT_CONFIG = {
    'videos_per_keyword': 2,
    'max_resolution': '1080p',
    'api_delay': 1.0,  # seconds between API calls
    'download_timeout': 300,  # 5 minutes
    'supported_formats': ['.mp4', '.mov', '.avi']
}

# Video Editing Settings
EDITING_CONFIG = {
    'target_resolution': (1080, 1920),  # Instagram Reels format
    'fps': 30,
    'clip_duration': 2.0,  # seconds per clip
    'transition_duration': 0.2,  # seconds
    'beat_sync': True,
    'random_start_points': True,
    'transition_effects': [
        'fade', 'quick_fade', 'zoom_in', 'zoom_out', 'crossfade',
        'spin_right', 'spin_left', 'scale_bounce', 'smooth_fade',
        'dramatic_fade', 'zoom_blur', 'gentle_zoom'
    ]
}

# Subtitle Settings
SUBTITLE_CONFIG = {
    'model_size': 'small',  # tiny, small, medium, large
    'language': 'auto',  # auto-detect
    'max_words_per_segment': 5,
    'font_size': 24,
    'font_color': 'white',
    'outline_color': 'black',
    'outline_width': 2,
    'margin_bottom': 200,
    'alignment': 'center'
}

# Output Settings
OUTPUT_CONFIG = {
    'video_codec': 'libx264',
    'audio_codec': 'aac',
    'video_quality': 'crf=23',  # 0-51, lower is better
    'preset': 'ultrafast',  # ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow
    'cleanup_temp_files': True,
    'keep_intermediate_files': False
}

# Performance Settings
PERFORMANCE_CONFIG = {
    'max_concurrent_downloads': 1,
    'memory_limit_gb': 4,
    'use_gpu': False,  # Set to True if you have CUDA GPU
    'batch_size': 1
}

# Default Prompts
DEFAULT_PROMPTS = {
    'random_facts': """
Generate a short, creative, and funny 30-second reel script in a curious tone for speech generation for a fast-paced Instagram reel. 
add "Speech speed should be 5x" in every output.
The script must ONLY be about ONE of the following topics:
1. A list of random, surprising, or weird facts (could be historical, science-based, or internet trends).
2. A short, humorous and quirky fictional mini-story.
3. A light, curious, and slightly funny take on a recent geopolitical event or news trend (must be non-offensive and friendly).

The script should be formatted for a VOICEOVER with stage directions in parentheses (e.g., (soft laugh), (pause), (playful chuckle)) to indicate emotions, pauses, and tone shifts. 
Include SOUND EFFECT suggestions in ALL CAPS inside square brackets [e.g., [BEEP], [WAVES], [DRUM ROLL]] wherever relevant for comedic or dramatic effect.

Style rules:
- Humor should be light, friendly, and relatable—similar to casual Instagram reel background audio.
- Can reference recent internet memes, viral trends, or pop culture moments if relevant to the topic.
- Maintain natural pauses, laughter cues, and changes in tone.
- Keep it around 80–120 words so it fits in ~30 seconds.
- Always open with a hook that makes people curious.
""",
    
    'custom_topic': """
Generate a short, creative, and funny 30-second reel script in a curious tone for speech generation for a fast-paced Instagram reel.
add "Speech speed should be 5x" in every output.

The script should be formatted for a VOICEOVER with stage directions in parentheses (e.g., (soft laugh), (pause), (playful chuckle)) to indicate emotions, pauses, and tone shifts. 
Include SOUND EFFECT suggestions in ALL CAPS inside square brackets [e.g., [BEEP], [WAVES], [DRUM ROLL]] wherever relevant for comedic or dramatic effect.

Style rules:
- Humor should be light, friendly, and relatable—similar to casual Instagram reel background audio.
- Can reference recent internet memes, viral trends, or pop culture moments if relevant to the topic.
- Maintain natural pauses, laughter cues, and changes in tone.
- Keep it around 80–120 words so it fits in ~30 seconds.
- Always open with a hook that makes people curious.
"""
}

# File Naming Patterns
FILE_PATTERNS = {
    'audio': 'generated_audio_{timestamp}_{uuid}.wav',
    'video': 'final_reel_transitions.mp4',
    'subtitles': 'final_reel_transitions_subtitles.srt',
    'final_video': 'final_reel_transitions_subtitles.mp4'
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    'format': '%(asctime)s - %(levelname)s - %(message)s',
    'file_logging': True,
    'console_logging': True
}
