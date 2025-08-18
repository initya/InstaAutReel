# 🎬 Video Subtitle Generator

Automatically generate subtitles for your video files using AI-powered speech recognition and add them as either hard-burned or soft subtitle tracks.

## ✨ Features

- **AI Transcription**: Uses faster-whisper for accurate speech-to-text conversion
- **Multiple Output Formats**: 
  - SRT subtitle file
  - Hard-burned subtitles (permanently embedded in video)
  - Soft subtitles (toggleable subtitle track)
- **CPU Optimized**: Works efficiently on laptops without GPUs
- **Auto-detection**: Automatically finds video files in the current directory
- **Cross-platform**: Works on Windows, macOS, and Linux

## 🚀 Quick Start

### Option 1: One-Click (Windows)
1. Double-click `run_subtitle_generator.bat`
2. The script will automatically install dependencies and process your video

### Option 2: Manual Run
1. Install FFmpeg (see requirements below)
2. Run: `python generate_subtitles.py`

## 📋 Requirements

### FFmpeg Installation

**Windows:**
- Download from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
- Extract to a folder and add to PATH, or place `ffmpeg.exe` in the same directory

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt install ffmpeg
```

### Python Dependencies
The script will automatically install these packages:
- `faster-whisper` - AI speech recognition
- `pysubs2` - Subtitle file handling
- `ffmpeg-python` - Video processing

## 🎯 Usage

1. **Place your video file** in the same directory as the script
2. **Run the script** (see Quick Start above)
3. **Wait for processing** - transcription can take several minutes depending on video length
4. **Get your results**:
   - `video_name_subtitles.srt` - Subtitle file
   - `video_name_hardsub.mp4` - Video with burned-in subtitles
   - `video_name_softsub.mp4` - Video with toggleable subtitle track

## ⚙️ Configuration

### Model Size Options
You can modify the script to use different model sizes:

- **`tiny`** - Fastest, lower accuracy (good for quick drafts)
- **`small`** - Good balance of speed and accuracy (default)
- **`medium`** - Higher accuracy, slower processing
- **`large`** - Best accuracy, slowest processing

To change, edit line 189 in `generate_subtitles.py`:
```python
if not transcribe_audio(video_path, model_size="tiny", output_srt=srt_file):
```

### Output Quality
For hard-burned subtitles, you can adjust quality by modifying the CRF value (lower = higher quality, larger file):
```python
crf=23  # Good quality, reasonable file size
# crf=18  # Higher quality, larger file
# crf=28  # Lower quality, smaller file
```

## 📁 Output Files

- **SRT File**: Standard subtitle format, can be used with any video player
- **Hard Subtitles**: Subtitles are permanently part of the video (larger file, always visible)
- **Soft Subtitles**: Subtitles as a separate track (can be toggled on/off in video players)

## 🔧 Troubleshooting

### "FFmpeg not found"
- Install FFmpeg (see Requirements section)
- Make sure it's in your system PATH
- Or place `ffmpeg.exe` in the same directory as the script

### "Import error"
- The script will automatically install required packages
- If it fails, manually run: `pip install -r requirements.txt`

### Transcription is slow
- Use a smaller model size (`tiny` instead of `small`)
- The first run downloads the AI model (subsequent runs are faster)

### Poor transcription quality
- Try a larger model size (`medium` or `large`)
- Ensure your video has clear audio
- Check that the language is supported

## 🎨 Customization

### Subtitle Styling
To customize subtitle appearance, you can modify the FFmpeg subtitle filter options in the `create_hard_subtitles` function:

```python
vf=f"subtitles={srt_path}:force_style='FontSize=24,PrimaryColour=&Hffffff,OutlineColour=&H000000,Bold=1'"
```

### Language Detection
The script auto-detects language, but you can force a specific language by modifying the transcribe call:

```python
segments, info = model.transcribe(
    video_path, 
    beam_size=5,
    language="en"  # Force English instead of "auto"
)
```

## 📚 Technical Details

- **faster-whisper**: Optimized Whisper implementation using CTranslate2
- **CPU Optimization**: Uses `int8_float32` compute type for better CPU performance
- **Beam Search**: Uses beam size 5 for better transcription accuracy
- **Format Support**: Input: MP4, AVI, MOV, MKV | Output: MP4 with H.264 video

## 🤝 Contributing

Feel free to modify the script for your needs! Common customizations:
- Add subtitle styling options
- Support for more video formats
- Batch processing of multiple videos
- Integration with other subtitle formats (VTT, ASS)

## 📄 License

This script is provided as-is for educational and personal use.
