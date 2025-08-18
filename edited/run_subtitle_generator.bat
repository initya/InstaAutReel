@echo off
echo 🎬 Video Subtitle Generator
echo ================================
echo.
echo This script will generate subtitles for your video files.
echo Make sure you have FFmpeg installed on your system.
echo.
echo Press any key to continue...
pause >nul

echo.
echo Installing Python packages...
python -m pip install -r requirements.txt

echo.
echo Running subtitle generator...
python generate_subtitles.py

echo.
echo Press any key to exit...
pause >nul
