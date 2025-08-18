# Video Downloader - Flask Frontend

A modern web application built with Flask that allows users to download high-quality videos from Pexels based on keywords. The application provides both manual keyword input and file upload capabilities.

## Features

- 🎯 **Keyword-based Search**: Enter keywords manually or upload a text file
- 📁 **File Upload Support**: Drag & drop or browse for keywords files
- 📥 **Batch Downloads**: Download multiple videos per keyword
- 📊 **Real-time Progress**: Live progress tracking with status updates
- 🎬 **Video Management**: View, play, and manage downloaded videos
- 🎨 **Modern UI**: Beautiful, responsive design with Bootstrap 5
- ⚡ **Background Processing**: Non-blocking downloads with threading

## Prerequisites

- Python 3.7 or higher
- Pexels API key (free at [pexels.com/api](https://www.pexels.com/api/))

## Installation

1. **Clone or download the project files**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your Pexels API key**:
   - Get your free API key from [Pexels API](https://www.pexels.com/api/)
   - Open `app.py` and replace the `PEXELS_API_KEY` value with your key

4. **Run the application**:
   ```bash
   python app.py
   ```

5. **Open your browser** and navigate to `http://localhost:5000`

## Usage

### Manual Keyword Input
1. Enter keywords in the text area (one per line)
2. Select the number of videos per keyword
3. Click "Start Download"

### File Upload
1. Create a text file with keywords (one per line)
2. Drag & drop the file or click to browse
3. Upload the file to load keywords
4. Click "Download Videos for These Keywords"

### Viewing Downloads
- Click "View Downloads" to see all downloaded videos
- Click the "Play" button to preview videos in a modal
- Videos are stored in the `videos/` directory

## File Structure

```
cont/
├── app.py                 # Main Flask application
├── content.py            # Original video download script
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── templates/           # HTML templates
│   ├── index.html      # Main page
│   └── downloads.html  # Downloads page
├── videos/             # Downloaded video storage
└── uploads/            # Temporary file upload storage
```

## API Endpoints

- `GET /` - Main page with keyword input and file upload
- `POST /upload` - Handle file uploads
- `POST /download` - Start video downloads
- `GET /status/<task_id>` - Get download progress
- `GET /downloads` - View downloaded videos

## Configuration

### Environment Variables
- `PEXELS_API_KEY`: Your Pexels API key
- `SAVE_DIR`: Directory to save downloaded videos (default: `videos/`)
- `UPLOAD_FOLDER`: Directory for temporary file uploads (default: `uploads/`)

### Download Settings
- **Videos per keyword**: 1-5 videos per search term
- **Video quality**: Automatically selects highest available resolution
- **Rate limiting**: Built-in delays to respect API limits

## Troubleshooting

### Common Issues

1. **API Key Error**: Ensure your Pexels API key is valid and has sufficient quota
2. **No Videos Found**: Some keywords may not return results - try alternative terms
3. **Download Failures**: Check your internet connection and disk space
4. **Port Already in Use**: Change the port in `app.py` or stop other services

### Performance Tips

- Use specific, relevant keywords for better results
- Limit videos per keyword to avoid long download times
- Ensure adequate disk space for video storage
- Close other bandwidth-heavy applications during downloads

## Security Notes

- Change the `secret_key` in production
- The API key is visible in the code - consider using environment variables
- File uploads are restricted to `.txt` files only
- Downloaded videos are stored locally

## License

This project is for educational and personal use. Please respect Pexels' terms of service and API usage limits.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify your API key and internet connection
3. Review the Flask and Pexels API documentation

---

**Note**: This application uses the Pexels API which has rate limits. Please be respectful of their service and don't exceed reasonable usage patterns.
