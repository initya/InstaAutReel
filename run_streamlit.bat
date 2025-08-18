@echo off
echo 🎬 Instagram Reel Creator - Streamlit Frontend
echo ================================================

echo 📦 Installing dependencies...
pip install -r requirements.txt

echo 🚀 Starting Streamlit application...
echo.
echo 💡 The app will open in your browser automatically
echo 🌐 Access URL: http://localhost:8501
echo ⏹️  Press Ctrl+C to stop the server
echo.

streamlit run streamlit_app.py --server.port=8501 --server.address=localhost

pause
