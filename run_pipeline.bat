@echo off
echo 🎬 Instagram Reel Creation Pipeline
echo ====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo ✅ Python found
echo.

REM Check if virtual environment exists, create if not
if not exist "pipeline_env" (
    echo 🔧 Creating virtual environment...
    python -m venv pipeline_env
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call pipeline_env\Scripts\activate.bat

REM Install requirements
echo 📦 Installing requirements...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install requirements
    pause
    exit /b 1
)

echo.
echo 🚀 Starting pipeline...
echo.

REM Run the main pipeline
python main_pipeline.py

echo.
echo 🏁 Pipeline completed
pause
