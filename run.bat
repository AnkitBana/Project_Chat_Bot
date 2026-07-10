@echo off
echo.
echo  Starting Nova AI Agent...
echo.

:: Create .env if missing
if not exist ".env" (
    copy .env.example .env >nul
    echo  No .env found — created one from .env.example
    echo  Open .env, add your API key, then run this again.
    echo.
    start notepad .env
    pause
    exit /b
)

:: Create Windows venv if it doesn't exist
if not exist "venv_win\Scripts\python.exe" (
    echo  Creating Python virtual environment...
    "C:\Users\AnkitGautam\AppData\Local\Programs\Python\Python313\python.exe" -m venv venv_win
)

:: Activate venv and install dependencies
echo  Installing dependencies...
venv_win\Scripts\python.exe -m pip install -r requirements.txt -q

:: Create folders
if not exist "data"   mkdir data
if not exist "logs"   mkdir logs

:: Open browser then start server
start http://localhost:8000
venv_win\Scripts\python.exe server.py

pause
