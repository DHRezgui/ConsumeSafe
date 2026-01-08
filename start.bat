@echo off
REM ConsumeSafe v2.0 - Quick Start Script for Windows

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║         ConsumeSafe v2.0 - Quick Start (Windows)          ║
echo ║              Stand with Palestine 🇵🇸                      ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found. Please install Python 3.11+
    exit /b 1
)

echo ✅ Python found
python --version
echo.

REM Activate virtual environment
if exist .venv (
    echo ✅ Virtual environment found
    call .venv\Scripts\activate.bat
) else (
    echo ⚠️  Virtual environment not found, creating one...
    python -m venv .venv
    call .venv\Scripts\activate.bat
    echo ✅ Virtual environment created and activated
)

echo.
echo 📦 Installing dependencies...
pip install -r requirements.txt -q

echo.
echo ✅ Dependencies installed
echo.

echo 🚀 Starting ConsumeSafe v2.0...
echo.
echo API Server:        http://127.0.0.1:8000
echo Frontend:          http://localhost:8080
echo API Documentation: http://127.0.0.1:8000/api/docs
echo.
echo Ctrl+C to stop
echo.

REM Start API server in background
echo Starting API server...
start cmd /k "python -m uvicorn ConsumeSafe.app.main:app --host 127.0.0.1 --port 8000"

REM Wait for API to start
timeout /t 3 /nobreak

REM Start frontend server in background
echo Starting frontend server...
cd ConsumeSafe\app
start cmd /k "python -m http.server 8080"

REM Return to root directory
cd ..\..

echo.
echo ✅ ConsumeSafe v2.0 is running!
echo.
echo 🌐 Open in your browser:
echo    http://localhost:8080
echo.
echo 📚 API Documentation:
echo    http://127.0.0.1:8000/api/docs
echo.
echo 🔐 Security Features:
echo    - Rate limiting enabled
echo    - Input validation
echo    - Security headers
echo    - CORS protection
echo.

pause
