@echo off
title VoxCPM2 Voice Cloner - Starting...
cd /d "%~dp0"

:: ========== Check if installed ==========
if not exist ".venv\Scripts\python.exe" (
    echo ========================================
    echo   Not installed yet! Please double click install.bat first.
    echo ========================================
    echo.
    pause
    exit /b 1
)

:: ========== Check voices ==========
if not exist "voices" (
    mkdir voices
)
set HAS_VOICE=0
for /d %%d in (voices\*) do (
    if exist "%%d\ref_voice.wav" set HAS_VOICE=1
)
if %HAS_VOICE%==0 (
    echo ========================================
    echo   No voices recorded yet!
    echo   Please record your reference voice in the WebUI.
    echo ========================================
    echo.
)

:: ========== Close old server ==========
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :7860') do (
    taskkill /f /pid %%a 2>nul
)

:: ========== Start server ==========
echo Starting VoxCPM2 Voice Cloner...
start "VoxCPM2 Server" ".venv\Scripts\python.exe" app.py

:: ========== Wait for server ==========
echo Waiting for server to start...
:wait
ping 127.0.0.1 -n 2 >nul
curl -s http://127.0.0.1:7860 >nul 2>&1
if errorlevel 1 goto wait

:: ========== Open browser ==========
echo Done! Opening browser...
start http://127.0.0.1:7860

echo.
echo You can close this window. The server will run in the background.
echo To stop, press Ctrl+C or close the "VoxCPM2 Server" window.
ping 127.0.0.1 -n 6 >nul