from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import os
import re
import requests
import threading
import time
from werkzeug.utils import secure_filename
import json
from datetime import datetime
import sqlite3

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# Configuration
PEXELS_API_KEY = os.getenv('PEXELS_API_KEY', "TOv7wzLAVTXwkt00DMN5vqcqjuwtH2iv5oMQFVWfX2vNc9IvlihKDQiV")
SEARCH_URL = "https://api.pexels.com/videos/search"
SAVE_DIR = "videos"
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {'txt'}

# Cloud deployment settings
IS_CLOUD_DEPLOYMENT = os.getenv('IS_CLOUD_DEPLOYMENT', 'false').lower() == 'true'
MAX_STORAGE_MB = int(os.getenv('MAX_STORAGE_MB', '100'))  # 100MB default
ENABLE_DOWNLOADS = os.getenv('ENABLE_DOWNLOADS', 'true').lower() == 'true'

# Create directories
os.makedirs(SAVE_DIR, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize database
def init_database():
    """Initialize SQLite database for video metadata"""
    conn = sqlite3.connect('videos.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword TEXT NOT NULL,
            title TEXT,
            pexels_id INTEGER,
            pexels_url TEXT,
            file_path TEXT,
            file_size INTEGER,
            cloud_url TEXT,
            downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'pending'
        )
    ''')
    conn.commit()
    conn.close()

init_database()

# Global variable to store download status
download_status = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_storage_usage():
    """Get current storage usage in MB"""
    total_size = 0
    if os.path.exists(SAVE_DIR):
        for filename in os.listdir(SAVE_DIR):
            filepath = os.path.join(SAVE_DIR, filename)
            if os.path.isfile(filepath):
                total_size += os.path.getsize(filepath)
    return total_size / (1024 * 1024)  # Convert to MB

def can_download_file(file_size_mb):
    """Check if we can download a file without exceeding storage limit"""
    current_usage = get_storage_usage()
    return (current_usage + file_size_mb) <= MAX_STORAGE_MB

def cleanup_old_files():
    """Remove old files to free up space"""
    if not os.path.exists(SAVE_DIR):
        return
    
    files = []
    for filename in os.listdir(SAVE_DIR):
        if filename.endswith('.mp4'):
            filepath = os.path.join(SAVE_DIR, filename)
            files.append({
                'name': filename,
                'path': filepath,
                'modified': os.path.getmtime(filepath),
                'size': os.path.getsize(filepath)
            })
    
    # Sort by modification time (oldest first)
    files.sort(key=lambda x: x['modified'])
    
    current_usage = get_storage_usage()
    for file_info in files:
        if current_usage <= MAX_STORAGE_MB * 0.8:  # Keep 20% buffer
            break
        
        try:
            os.remove(file_info['path'])
            current_usage -= file_info['size'] / (1024 * 1024)
            print(f"Cleaned up old file: {file_info['name']}")
        except Exception as e:
            print(f"Error cleaning up file {file_info['name']}: {e}")

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

def download_video(video_url, filename, video_info):
    """Download a single video file with storage management"""
    if IS_CLOUD_DEPLOYMENT and not ENABLE_DOWNLOADS:
        # In cloud mode, just store metadata
        store_video_metadata(video_info, None)
        return True
    
    try:
        # Check storage before downloading
        if IS_CLOUD_DEPLOYMENT:
            # Estimate file size (rough approximation)
            estimated_size_mb = 50  # Conservative estimate
            if not can_download_file(estimated_size_mb):
                cleanup_old_files()
                if not can_download_file(estimated_size_mb):
                    print(f"Storage limit reached, cannot download {filename}")
                    return False
        
        video_response = requests.get(video_url, stream=True)
        with open(filename, "wb") as f:
            for chunk in video_response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        
        # Store metadata
        store_video_metadata(video_info, filename)
        return True
        
    except Exception as e:
        print(f"Error downloading {filename}: {e}")
        return False

def store_video_metadata(video_info, file_path):
    """Store video metadata in database"""
    try:
        conn = sqlite3.connect('videos.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO videos (keyword, title, pexels_id, pexels_url, file_path, file_size, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            video_info.get('keyword', ''),
            video_info.get('title', ''),
            video_info.get('pexels_id', 0),
            video_info.get('pexels_url', ''),
            file_path,
            video_info.get('file_size', 0),
            'downloaded' if file_path else 'metadata_only'
        ))
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error storing metadata: {e}")

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
                download_status[task_id]['message'] = f'Processing video {idx}/{len(videos)} for "{query}"'
            
            # Pick highest resolution
            best_video_file = max(video["video_files"], key=lambda v: v["width"])
            video_url = best_video_file["link"]
            
            filename = os.path.join(SAVE_DIR, f"{query.replace(' ', '_')}_{idx}.mp4")
            
            # Prepare video info for metadata
            video_info = {
                'keyword': query,
                'title': video.get('url', '').split('/')[-1],
                'pexels_id': video.get('id', 0),
                'pexels_url': video.get('url', ''),
                'file_size': best_video_file.get('width', 0) * best_video_file.get('height', 0) * 0.0001  # Rough estimate
            }
            
            if download_video(video_url, filename, video_info):
                if task_id:
                    download_status[task_id]['downloaded'] += 1
                    if filename and os.path.exists(filename):
                        download_status[task_id]['files'].append(filename)
            
            # Small delay to avoid overwhelming the API
            time.sleep(0.5)
        
        if task_id:
            download_status[task_id]['status'] = 'completed'
            mode = "metadata only" if IS_CLOUD_DEPLOYMENT and not ENABLE_DOWNLOADS else "downloaded"
            download_status[task_id]['message'] = f'Successfully processed {len(videos)} videos for "{query}" ({mode})'
            
    except Exception as e:
        if task_id:
            download_status[task_id]['status'] = 'error'
            download_status[task_id]['message'] = f'Error: {str(e)}'

@app.route('/')
def index():
    storage_info = {
        'current_usage': round(get_storage_usage(), 2),
        'max_storage': MAX_STORAGE_MB,
        'is_cloud': IS_CLOUD_DEPLOYMENT,
        'downloads_enabled': ENABLE_DOWNLOADS
    }
    return render_template('index.html', storage_info=storage_info)

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
    # Get videos from database
    conn = sqlite3.connect('videos.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM videos ORDER BY downloaded_at DESC')
    db_videos = cursor.fetchall()
    conn.close()
    
    # Get local files if downloads are enabled
    local_files = []
    if ENABLE_DOWNLOADS and os.path.exists(SAVE_DIR):
        for filename in os.listdir(SAVE_DIR):
            if filename.endswith('.mp4'):
                filepath = os.path.join(SAVE_DIR, filename)
                local_files.append({
                    'name': filename,
                    'size': os.path.getsize(filepath),
                    'modified': os.path.getmtime(filepath),
                    'path': filepath
                })
    
    # Sort by modification time (newest first)
    local_files.sort(key=lambda x: x['modified'], reverse=True)
    
    return render_template('downloads.html', 
                         db_videos=db_videos, 
                         local_files=local_files,
                         is_cloud=IS_CLOUD_DEPLOYMENT,
                         downloads_enabled=ENABLE_DOWNLOADS)

@app.route('/storage')
def storage_info():
    """Get storage information"""
    current_usage = get_storage_usage()
    return jsonify({
        'current_usage_mb': round(current_usage, 2),
        'max_storage_mb': MAX_STORAGE_MB,
        'usage_percentage': round((current_usage / MAX_STORAGE_MB) * 100, 2),
        'is_cloud': IS_CLOUD_DEPLOYMENT,
        'downloads_enabled': ENABLE_DOWNLOADS
    })

if __name__ == '__main__':
    # Validate API key
    if not PEXELS_API_KEY:
        print("⚠️  WARNING: No Pexels API key found!")
        print("   Please set a valid PEXELS_API_KEY environment variable or update the key in app.py")
        print("   Get your free API key at: https://www.pexels.com/api/")
    elif PEXELS_API_KEY == "TOv7wzLAVTXwkt00DMN5vqcqjuwtH2iv5oMQFVWfX2vNc9IvlihKDQiV":
        print("✅ Pexels API key is set and ready to use!")
    else:
        print("✅ Pexels API key is set and ready to use!")
    
    if IS_CLOUD_DEPLOYMENT:
        print(f"🌐 Cloud deployment mode: Storage limit {MAX_STORAGE_MB}MB")
        if not ENABLE_DOWNLOADS:
            print("📝 Metadata-only mode: Videos will not be downloaded locally")
        else:
            print("💾 Download mode: Videos will be stored locally (within storage limits)")
    
    print(f"💾 Current storage usage: {get_storage_usage():.2f}MB")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
