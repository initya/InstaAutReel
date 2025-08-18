from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import os
import re
import requests
import threading
import time
from werkzeug.utils import secure_filename
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# Configuration
PEXELS_API_KEY = os.getenv('PEXELS_API_KEY', "TOv7wzLAVTXwkt00DMN5vqcqjuwtH2iv5oMQFVWfX2vNc9IvlihKDQiV")
SEARCH_URL = "https://api.pexels.com/videos/search"
SAVE_DIR = "videos"
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {'txt'}

# Validate API key
if not PEXELS_API_KEY:
    print("⚠️  WARNING: No Pexels API key found!")
    print("   Please set a valid PEXELS_API_KEY environment variable or update the key in app.py")
    print("   Get your free API key at: https://www.pexels.com/api/")
elif PEXELS_API_KEY == "TOv7wzLAVTXwkt00DMN5vqcqjuwtH2iv5oMQFVWfX2vNc9IvlihKDQiV":
    print("✅ Pexels API key is set and ready to use!")
else:
    print("✅ Pexels API key is set and ready to use!")

# Create directories
os.makedirs(SAVE_DIR, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Global variable to store download status
download_status = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_keywords_from_file(file_path):
    """Reads keywords from a text file and removes numbering."""
    keywords = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                cleaned = re.sub(r"^\s*\d+\.\s*", "", line).strip()
                if cleaned:
                    keywords.append(cleaned)
    except Exception as e:
        print(f"Error reading file: {e}")
    return keywords

def download_video(video_url, filename):
    """Download a single video file."""
    try:
        video_response = requests.get(video_url, stream=True)
        with open(filename, "wb") as f:
            for chunk in video_response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        return True
    except Exception as e:
        print(f"Error downloading {filename}: {e}")
        return False

def search_and_download_videos_direct(query, per_page=2):
    """Direct version of search_and_download_videos for pipeline use"""
    print(f"🔍 Searching for videos: '{query}' (direct mode)")
    
    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": query, "per_page": per_page}
    
    try:
        response = requests.get(SEARCH_URL, headers=headers, params=params)
        if response.status_code != 200:
            error_message = f"API Error: {response.status_code}"
            if response.status_code == 401:
                error_message = "API Error: 401 Unauthorized - Please check your Pexels API key"
            elif response.status_code == 429:
                error_message = "API Error: 429 Rate Limited - Please wait before trying again"
            elif response.status_code == 403:
                error_message = "API Error: 403 Forbidden - API key may be invalid or expired"
            
            print(f"❌ {error_message}")
            return False
        
        data = response.json()
        videos = data.get("videos", [])
        
        if not videos:
            print(f"⚠️  No videos found for '{query}'")
            return False
        
        print(f"📹 Found {len(videos)} videos for '{query}'")
        
        downloaded_count = 0
        for idx, video in enumerate(videos, start=1):
            print(f"  📥 Downloading video {idx}/{len(videos)}...")
            
            # Pick highest resolution
            best_video_file = max(video["video_files"], key=lambda v: v["width"])
            video_url = best_video_file["link"]
            
            filename = os.path.join(SAVE_DIR, f"{query.replace(' ', '_')}_{idx}.mp4")
            
            if download_video(video_url, filename):
                downloaded_count += 1
                print(f"    ✅ Downloaded: {filename}")
            else:
                print(f"    ❌ Failed to download video {idx}")
            
            # Small delay to avoid overwhelming the API
            time.sleep(0.5)
        
        print(f"✅ Downloaded {downloaded_count}/{len(videos)} videos for '{query}'")
        return downloaded_count > 0
        
    except Exception as e:
        print(f"❌ Error downloading videos for '{query}': {str(e)}")
        return False

def search_and_download_videos(query, per_page=2, task_id=None):
    """Search and download videos for a given query."""
    if task_id:
        download_status[task_id]['status'] = 'searching'
        download_status[task_id]['message'] = f'Searching for videos with keyword: {query}'
    
    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": query, "per_page": per_page}
    
    try:
        response = requests.get(SEARCH_URL, headers=headers, params=params)
        if response.status_code != 200:
            error_message = f"API Error: {response.status_code}"
            if response.status_code == 401:
                error_message = "API Error: 401 Unauthorized - Please check your Pexels API key"
            elif response.status_code == 429:
                error_message = "API Error: 429 Rate Limited - Please wait before trying again"
            elif response.status_code == 403:
                error_message = "API Error: 403 Forbidden - API key may be invalid or expired"
            
            if task_id:
                download_status[task_id]['status'] = 'error'
                download_status[task_id]['message'] = error_message
            return
        
        data = response.json()
        videos = data.get("videos", [])
        
        if not videos:
            if task_id:
                download_status[task_id]['status'] = 'completed'
                download_status[task_id]['message'] = f"No videos found for '{query}'"
            return
        
        if task_id:
            download_status[task_id]['total_videos'] = len(videos)
            download_status[task_id]['downloaded'] = 0
            download_status[task_id]['status'] = 'downloading'
        
        for idx, video in enumerate(videos, start=1):
            if task_id:
                download_status[task_id]['current_video'] = idx
                download_status[task_id]['message'] = f'Downloading video {idx}/{len(videos)} for "{query}"'
            
            # Pick highest resolution
            best_video_file = max(video["video_files"], key=lambda v: v["width"])
            video_url = best_video_file["link"]
            
            filename = os.path.join(SAVE_DIR, f"{query.replace(' ', '_')}_{idx}.mp4")
            
            if download_video(video_url, filename):
                if task_id:
                    download_status[task_id]['downloaded'] += 1
                    download_status[task_id]['files'].append(filename)
            
            # Small delay to avoid overwhelming the API
            time.sleep(0.5)
        
        if task_id:
            download_status[task_id]['status'] = 'completed'
            download_status[task_id]['message'] = f'Successfully downloaded {len(videos)} videos for "{query}"'
            
    except Exception as e:
        if task_id:
            download_status[task_id]['status'] = 'error'
            download_status[task_id]['message'] = f'Error: {str(e)}'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file selected')
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected')
        return redirect(url_for('index'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        keywords = load_keywords_from_file(filepath)
        if keywords:
            flash(f'Successfully loaded {len(keywords)} keywords from file')
            return render_template('index.html', keywords=keywords)
        else:
            flash('No valid keywords found in file')
            return redirect(url_for('index'))
    
    flash('Invalid file type. Please upload a .txt file')
    return redirect(url_for('index'))

@app.route('/download', methods=['POST'])
def start_download():
    data = request.get_json()
    keywords = data.get('keywords', [])
    per_page = data.get('per_page', 1)
    
    if not keywords:
        return jsonify({'error': 'No keywords provided'}), 400
    
    # Create a unique task ID
    task_id = f"task_{int(time.time())}"
    
    # Initialize download status
    download_status[task_id] = {
        'status': 'pending',
        'message': 'Starting download...',
        'keywords': keywords,
        'total_videos': 0,
        'downloaded': 0,
        'current_video': 0,
        'files': [],
        'start_time': time.time()
    }
    
    # Start download in background thread
    def download_all():
        for keyword in keywords:
            search_and_download_videos(keyword, per_page, task_id)
    
    thread = threading.Thread(target=download_all)
    thread.daemon = True
    thread.start()
    
    return jsonify({'task_id': task_id, 'message': 'Download started'})

@app.route('/status/<task_id>')
def get_status(task_id):
    if task_id in download_status:
        return jsonify(download_status[task_id])
    return jsonify({'error': 'Task not found'}), 404

@app.route('/downloads')
def list_downloads():
    files = []
    if os.path.exists(SAVE_DIR):
        for filename in os.listdir(SAVE_DIR):
            if filename.endswith('.mp4'):
                filepath = os.path.join(SAVE_DIR, filename)
                files.append({
                    'name': filename,
                    'size': os.path.getsize(filepath),
                    'modified': os.path.getmtime(filepath)
                })
    
    # Sort by modification time (newest first)
    files.sort(key=lambda x: x['modified'], reverse=True)
    return render_template('downloads.html', files=files)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
