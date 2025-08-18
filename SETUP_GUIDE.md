# 🎬 Instagram Reel Creator - Complete Setup Guide

## 🚀 **Quick Start (Recommended)**

### **Windows Users**
1. **Double-click** `run_streamlit.bat`
2. **Wait for browser** to open automatically
3. **Start creating reels!** 🎉

### **Linux/Mac Users**
```bash
chmod +x run_streamlit.sh
./run_streamlit.sh
```

---

## 📋 **Manual Installation**

### **Step 1: Install Python Dependencies**
```bash
# Install all required packages
pip install -r requirements.txt

# Or install individual packages:
pip install streamlit>=1.28.0
pip install google-generativeai>=0.3.0
pip install moviepy>=1.0.0
pip install librosa>=0.10.0
pip install faster-whisper>=0.10.0
pip install requests>=2.31.0
pip install flask>=2.3.0
```

### **Step 2: Configure API Keys**

#### **Get Your API Keys**
1. **Gemini AI API Key**:
   - Visit: https://makersuite.google.com/app/apikey
   - Create new API key
   - Copy the key

2. **Pexels API Key**:
   - Visit: https://www.pexels.com/api/
   - Sign up for free account
   - Get your API key

#### **Set API Keys in Config**
Edit `config.py` and update:
```python
GEMINI_API_KEY = "your_actual_gemini_api_key_here"
PEXELS_API_KEY = "your_actual_pexels_api_key_here"
```

**OR** set environment variables:
```bash
# Windows
set GEMINI_API_KEY=your_key_here
set PEXELS_API_KEY=your_key_here

# Linux/Mac
export GEMINI_API_KEY=your_key_here
export PEXELS_API_KEY=your_key_here
```

### **Step 3: Install FFmpeg (Required for Video Processing)**

#### **Windows**
1. Download from: https://ffmpeg.org/download.html
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to your PATH

#### **macOS**
```bash
brew install ffmpeg
```

#### **Ubuntu/Debian**
```bash
sudo apt update
sudo apt install ffmpeg
```

### **Step 4: Start the Application**
```bash
streamlit run streamlit_app.py
```

---

## 🎯 **Using the Application**

### **1. Access the Interface**
- **URL**: http://localhost:8501
- **Auto-opens** in your default browser

### **2. Configure Your Reel**
- **Custom Prompt**: Enter specific topic or leave blank for random
- **Videos per Keyword**: Choose 1-5 videos per keyword (2 recommended)

### **3. Start the Pipeline**
- Click **🚀 Start Pipeline**
- Watch **real-time progress** updates
- Monitor each step:
  - 🎤 AI Voice Generation
  - 🎬 Stock Video Download
  - ✂️ Beat-Sync Video Editing
  - 📝 AI Subtitle Generation

### **4. Watch & Download**
- **Live video player** shows your reel when ready
- **Download button** saves MP4 to your device
- **Perfect format** for Instagram Reels (1080x1920)

---

## 🔧 **Troubleshooting**

### **Common Issues & Solutions**

#### **"Module not found" Error**
```bash
# Install missing dependencies
pip install -r requirements.txt
```

#### **"API key not configured" Error**
- Check API keys in `config.py`
- Verify keys are valid and active
- Try setting environment variables

#### **"FFmpeg not found" Error**
- Install FFmpeg (see Step 3 above)
- Ensure FFmpeg is in your PATH
- Restart terminal after installation

#### **Video Won't Play**
- Check if video file exists in `output/` folder
- Try refreshing the page
- For large files, use download button instead

#### **Pipeline Fails at Step 2 (Video Download)**
- Check internet connection
- Verify Pexels API key is valid
- Try reducing "Videos per Keyword" to 1

#### **Pipeline Fails at Step 3 (Video Editing)**
- Ensure MoviePy is installed: `pip install moviepy`
- Check if FFmpeg is properly installed
- Verify downloaded videos exist

#### **Pipeline Fails at Step 4 (Subtitles)**
- Install Faster Whisper: `pip install faster-whisper`
- Ensure sufficient disk space
- Try smaller model size in config

#### **Streamlit Won't Start**
- Check if port 8501 is available
- Try different port: `streamlit run streamlit_app.py --server.port=8502`
- Check Python version (3.8+ required)

#### **Pipeline Stops Unexpectedly**
- Check console logs for detailed errors
- Ensure stable internet connection
- Try resetting and starting again

### **Performance Optimization**

#### **For Faster Processing**
- **Use SSD storage** for better I/O performance
- **Close other video applications** to free up resources
- **Ensure stable internet** for smooth downloads
- **Use smaller model size** for subtitles if needed

#### **For Better Quality**
- **Increase "Videos per Keyword"** for more variety
- **Use specific prompts** for targeted content
- **Check downloaded videos** quality before processing

---

## 🎬 **Expected Output**

### **Files Created**
- `output/final_reel_transitions_subtitles.mp4` - **Final video with subtitles**
- `output/final_reel_transitions_subtitles.srt` - **Subtitle file**
- `output/generated_audio_[timestamp].wav` - **Generated audio**
- `output/videos/` - **Downloaded stock videos**

### **Video Specifications**
- **Resolution**: 1080x1920 (Instagram Reels format)
- **Format**: MP4 with H.264 video and AAC audio
- **Duration**: ~30 seconds (optimized for social media)
- **Subtitles**: Hard-burned white text with black outline
- **Quality**: High-definition, ready for posting

---

## 🔍 **System Requirements**

### **Minimum Requirements**
- **Python**: 3.8 or higher
- **RAM**: 4GB (8GB recommended)
- **Storage**: 2GB free space
- **Internet**: Stable broadband connection
- **OS**: Windows 10+, macOS 10.14+, or Linux

### **Recommended Setup**
- **Python**: 3.10+
- **RAM**: 8GB+ 
- **Storage**: 5GB+ free space
- **GPU**: Optional (speeds up video processing)
- **SSD**: Recommended for faster file operations

---

## 📱 **Mobile Access**

The Streamlit app works on mobile browsers:
- **Access**: http://[your-ip]:8501 from phone
- **Features**: All functionality available
- **Best Experience**: Use tablet or landscape mode

---

## 🆘 **Getting Help**

### **Debug Steps**
1. **Check console logs** - Detailed error information
2. **Verify API keys** - Ensure they're valid and properly set
3. **Test internet connection** - Required for AI and video downloads
4. **Check disk space** - Video processing needs temporary storage
5. **Restart application** - Fresh start often fixes issues

### **Support Resources**
- **Check `output/` folder** for generated files
- **Review error messages** in the Streamlit interface
- **Test with simple prompt first** before complex requests
- **Use reset button** if pipeline gets stuck

---

## 🎉 **Success Tips**

1. **Start Simple** - Use default settings first
2. **Be Specific** - Detailed prompts create better content
3. **Monitor Progress** - Watch live updates for issues
4. **Check Results** - Preview before final processing
5. **Save Immediately** - Download videos when ready

---

## 🔄 **Updating**

To update the application:
```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

---

## 🎬 **Ready to Create Amazing Reels!**

Your Instagram Reel Creator is now ready! Simply follow the quick start guide above and watch as AI creates professional, engaging Instagram Reels automatically with live updates and instant playback! 🚀✨

**Pro Tip**: Test with a simple prompt like "funny cat facts" first to see the magic in action!
