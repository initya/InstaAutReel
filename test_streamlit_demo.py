#!/usr/bin/env python3
"""
Quick test script to verify Streamlit app functionality
"""

import streamlit as st
import os
from pathlib import Path

st.set_page_config(
    page_title="🎬 Instagram Reel Creator - Demo",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 Instagram Reel Creator - Demo Mode")

st.info("This is a demo to test the Streamlit interface components.")

# Test the UI components
st.header("📊 Pipeline Status Demo")

col1, col2 = st.columns(2)

with col1:
    st.success("✅ Step 1: AI Voice Generation (Completed)")
    st.info("🔄 Step 2: Stock Video Download (In Progress)")
    st.text("⏳ Step 3: Video Editing")
    st.text("⏳ Step 4: Subtitle Generation")

with col2:
    # Test progress bar
    st.subheader("Live Progress")
    progress = st.progress(0.35)
    st.write("Progress: 35%")
    
    # Test metrics
    st.metric("Videos Downloaded", "5", "2")
    st.metric("Processing Time", "2m 30s", "30s")

# Test sidebar
with st.sidebar:
    st.header("🎛️ Controls")
    
    custom_prompt = st.text_area(
        "Custom Prompt", 
        value="Create a funny video about cats doing yoga",
        height=100
    )
    
    videos_per_keyword = st.slider("Videos per Keyword", 1, 5, 2)
    
    if st.button("🚀 Start Pipeline", type="primary"):
        st.success("Demo: Pipeline would start here!")
    
    if st.button("🔄 Reset"):
        st.info("Demo: Pipeline would reset here!")

# Test file handling
st.header("📁 Output Files Demo")

# Create a demo output directory structure
output_dir = Path("output")
if output_dir.exists():
    files = list(output_dir.glob("*"))
    if files:
        st.write(f"Found {len(files)} files in output directory:")
        for file in files[:5]:  # Show first 5 files
            st.write(f"📄 {file.name}")
    else:
        st.write("📂 Output directory is empty")
else:
    st.write("📂 Output directory doesn't exist yet")

# Test video player placeholder
st.header("🎬 Video Player Demo")

# Check if there are any existing video files to demo
video_files = []
if output_dir.exists():
    video_files = list(output_dir.glob("*.mp4"))

if video_files:
    st.success(f"Found {len(video_files)} video files!")
    selected_video = st.selectbox("Select video to preview:", video_files)
    
    if selected_video and selected_video.exists():
        st.video(str(selected_video))
    else:
        st.info("Selected video file not found")
else:
    st.info("No video files found. Run the pipeline to generate videos!")
    
    # Show a placeholder
    st.markdown("""
    <div style="background: #f0f0f0; padding: 2rem; text-align: center; border-radius: 10px;">
        <h3>🎬 Video Player</h3>
        <p>Your final Instagram reel will appear here!</p>
        <p style="color: #666;">📱 Perfect 1080x1920 portrait format</p>
    </div>
    """, unsafe_allow_html=True)

# Test download functionality
st.header("📥 Download Demo")

if video_files:
    with open(video_files[0], "rb") as file:
        st.download_button(
            label="📥 Download Sample Video",
            data=file.read(),
            file_name="sample_reel.mp4",
            mime="video/mp4"
        )
else:
    st.info("No videos available for download yet")

# System info
st.header("🔧 System Information")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Python Version", f"{os.sys.version_info.major}.{os.sys.version_info.minor}")

with col2:
    st.metric("Streamlit Status", "✅ Running")

with col3:
    st.metric("Output Directory", "✅ Ready" if output_dir.exists() else "⚠️ Missing")

st.markdown("---")
st.success("🎉 Streamlit interface is working perfectly!")
st.info("💡 Ready to run the full pipeline? Use streamlit_app.py")
