# 🎬 Instagram Reel Creator - Streamlit Frontend

A comprehensive web interface for the Instagram Reel Creation Pipeline with **live updates**, **real-time video playback**, and **one-click operation**.

## ✨ Features

### 🚀 **Complete Pipeline Integration**
- **AI Voice Generation** - Generate engaging scripts with Gemini AI and convert to high-quality TTS
- **Smart Video Download** - Automatically download relevant stock videos from Pexels
- **Beat-Sync Editing** - Create professional reels with beat-synced transitions
- **AI Subtitles** - Generate and burn subtitles using Faster Whisper

### 🎯 **Live User Experience**
- **Real-time Progress Updates** - See exactly what's happening at each step
- **Live Video Playback** - Watch your reel directly in the browser
- **Interactive Controls** - Start, stop, and configure the pipeline easily
- **Instant Downloads** - Download your final video with one click

### 🎨 **Beautiful Interface**
- **Modern UI Design** - Clean, professional interface with gradient styling
- **Responsive Layout** - Works perfectly on desktop and mobile
- **Status Indicators** - Clear visual feedback for each pipeline step
- **Error Handling** - Helpful error messages and recovery suggestions

## 🚀 Quick Start

### **Windows Users**
```bash
# Double-click or run:
run_streamlit.bat
```

### **Linux/Mac Users**
```bash
# Make executable and run:
chmod +x run_streamlit.sh
./run_streamlit.sh
```

### **Manual Start**
```bash
# Install dependencies
pip install -r requirements.txt

# Start the app
streamlit run streamlit_app.py
```

## 🌐 Access the App

Once started, the app will automatically open in your browser at:
**http://localhost:8501**

## 📱 How to Use

### 1. **Configure Your Reel**
- **Custom Prompt**: Enter a specific topic or leave blank for random content
- **Videos per Keyword**: Choose how many stock videos to download (1-5)

### 2. **Start the Pipeline**
- Click **🚀 Start Pipeline** 
- Watch real-time progress updates
- See live status for each step:
  - 🎤 AI Voice Generation
  - 🎬 Stock Video Download  
  - ✂️ Video Editing
  - 📝 Subtitle Generation

### 3. **Monitor Progress**
- **Live Status Updates** - See exactly what's happening
- **Progress Bars** - Visual progress for each step
- **Real-time Results** - View generated script, keywords, and audio

### 4. **Watch & Download**
- **Live Video Player** - Watch your reel directly in the browser
- **Instant Download** - Click to download your final MP4
- **Video Stats** - See file size, resolution, and format info

## 🎯 Interface Sections

### **Sidebar Controls**
- **Pipeline Settings** - Configure prompts and video count
- **Control Buttons** - Start, stop, and reset the pipeline
- **System Status** - Real-time system information

### **Main Display**
- **Pipeline Status** - Live updates and progress tracking
- **Step Overview** - Visual status of all 4 pipeline steps
- **Live Results** - Generated content preview

### **Video Player**
- **Embedded Player** - Watch your reel with full controls
- **Download Button** - One-click download to your device
- **Video Information** - File stats and technical details

## 🔧 Advanced Features

### **Live Status Updates**
The app provides real-time feedback including:
- Current step and overall progress
- Detailed task descriptions
- File counts and sizes
- Processing times
- Error messages with solutions

### **Smart Error Handling**
- **Dependency Checking** - Automatically detects missing packages
- **File Validation** - Ensures all required files exist
- **API Status** - Monitors Pexels and Gemini API responses
- **Recovery Options** - Suggests fixes for common issues

### **Video Processing**
- **Beat-Sync Analysis** - Real-time audio beat detection
- **Dynamic Transitions** - Random transition effects for variety
- **Instagram Format** - Perfect 1080x1920 portrait orientation
- **Quality Optimization** - Balanced file size and quality

## ⚙️ Configuration

### **Environment Variables**
Set these in your environment or in `config.py`:
```bash
GEMINI_API_KEY=your_gemini_api_key
PEXELS_API_KEY=your_pexels_api_key
```

### **Pipeline Settings**
Customize in the sidebar:
- **Script Length**: Auto-optimized for 30-second reels
- **Video Quality**: High-definition 1080p output
- **Subtitle Style**: Professional white text with black outline
- **Transition Effects**: 12 different transition styles

## 🎬 Output Files

Your completed reel includes:
- **Final Video**: `final_reel_transitions_subtitles.mp4`
- **Subtitle File**: `final_reel_transitions_subtitles.srt`
- **Audio File**: `generated_audio_[timestamp].wav`
- **Stock Videos**: Individual downloaded video files

## 🛠️ Technical Details

### **Architecture**
- **Frontend**: Streamlit with custom CSS styling
- **Backend**: Multi-threaded Python pipeline
- **AI Integration**: Gemini AI for script generation and TTS
- **Video Processing**: MoviePy with librosa for beat analysis
- **Subtitles**: Faster Whisper for AI transcription

### **Performance**
- **Threading**: Non-blocking UI with background processing
- **Memory Efficient**: Streams large files to avoid memory issues
- **API Optimization**: Intelligent rate limiting and error handling
- **File Management**: Automatic cleanup and organization

### **Browser Compatibility**
- **Chrome**: ✅ Full support
- **Firefox**: ✅ Full support  
- **Safari**: ✅ Full support
- **Edge**: ✅ Full support

## 🔍 Troubleshooting

### **Common Issues**

#### **App Won't Start**
```bash
# Install missing dependencies
pip install streamlit

# Check Python version (3.8+ required)
python --version
```

#### **Video Won't Play**
- Check browser compatibility
- Ensure video file exists in output folder
- Try refreshing the page

#### **Pipeline Fails**
- Check API keys in config.py
- Verify internet connection
- Check console logs for detailed errors

#### **Dependencies Missing**
```bash
# Install all requirements
pip install -r requirements.txt

# Or use the auto-installer
python install_deps.py
```

### **Performance Tips**
- **Close other video apps** for better performance
- **Use SSD storage** for faster video processing
- **Ensure stable internet** for video downloads
- **Allow firewall access** for Streamlit server

## 📊 System Requirements

### **Minimum Requirements**
- **Python**: 3.8 or higher
- **RAM**: 4GB (8GB recommended)
- **Storage**: 2GB free space
- **Internet**: Stable broadband connection

### **Recommended Setup**
- **Python**: 3.10+
- **RAM**: 8GB+
- **Storage**: 5GB+ free space
- **GPU**: Optional (faster video processing)

## 🎉 Success Tips

1. **Use Descriptive Prompts** - Specific topics create better content
2. **Start Small** - Use 2 videos per keyword initially
3. **Check Preview** - Review generated script before processing
4. **Monitor Progress** - Watch live updates to catch issues early
5. **Download Immediately** - Save your video when processing completes

## 🆘 Support

### **Getting Help**
- **Check Console Logs** - Detailed error information
- **Review Status Messages** - Clear descriptions of current tasks
- **Monitor System Status** - Real-time system information
- **Reset if Stuck** - Use the reset button to start fresh

### **Best Practices**
- Always test with a simple prompt first
- Keep the browser tab active for best performance
- Don't start multiple pipelines simultaneously
- Save your final videos to a safe location

---

## 🎬 **Ready to Create Amazing Instagram Reels?**

**Start the app and watch the magic happen!** 🚀✨

Your AI-powered Instagram reel will be ready in just a few minutes with professional quality and engaging content!
