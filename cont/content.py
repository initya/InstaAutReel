import requests
import os
import re


PEXELS_API_KEY = "TOv7wzLAVTXwkt00DMN5vqcqjuwtH2iv5oMQFVWfX2vNc9IvlihKDQiV"


SEARCH_URL = "https://api.pexels.com/videos/search"


SAVE_DIR = "videos"
os.makedirs(SAVE_DIR, exist_ok=True)

def load_keywords(file_path):
    """Reads keywords from a text file and removes numbering."""
    keywords = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            cleaned = re.sub(r"^\s*\d+\.\s*", "", line).strip()
            if cleaned:
                keywords.append(cleaned)
    return keywords

def search_and_download_videos(query, per_page=2):
    headers = {
        "Authorization": PEXELS_API_KEY
    }
    params = {
        "query": query,
        "per_page": per_page
    }

    response = requests.get(SEARCH_URL, headers=headers, params=params)
    if response.status_code != 200:
        print(f"Error for '{query}':", response.status_code, response.text)
        return
    
    data = response.json()
    videos = data.get("videos", [])

    if not videos:
        print(f"No videos found for '{query}'")
        return

    for idx, video in enumerate(videos, start=1):
        # Pick highest resolution
        best_video_file = max(video["video_files"], key=lambda v: v["width"])
        video_url = best_video_file["link"]

        video_response = requests.get(video_url, stream=True)
        filename = os.path.join(SAVE_DIR, f"{query.replace(' ', '_')}_{idx}.mp4")

        with open(filename, "wb") as f:
            for chunk in video_response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        
        print(f"Downloaded: {filename}")

if __name__ == "__main__":
    # Use your full path here
    keywords = load_keywords(r"C:\Users\cnity\OneDrive\Desktop\gemini voice\keywords.txt")
    for word in keywords:
        search_and_download_videos(word, per_page=1)  # 1 video per keyword
