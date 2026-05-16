@echo off
REM English Learning App - Setup Script for Windows

echo ===============================================
echo English Learning Assistant - Setup Script
echo ===============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org
    pause
    exit /b 1
)

echo [1/4] Python found!
echo.

REM Create virtual environment
echo [2/4] Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

REM Activate virtual environment
echo [3/4] Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo [4/4] Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ===============================================
echo Setup completed successfully!
echo ===============================================
echo.
echo NEXT STEPS:
echo 1. Create a .env file with your API keys:
echo    - Copy .env.example to .env
echo    - Add your GEMINI_API_KEY and GROQ_API_KEY
echo.
echo 2. Run the app:
echo    streamlit run app.py
echo.
echo 3. The app will open in your browser
echo.
echo ===============================================
echo.
pause
