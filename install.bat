@echo off
title VoxCPM2 Voice Cloner - Installing...
cd /d "%~dp0"

echo ============================================
echo   VoxCPM2 Voice Cloner - Auto Installer
echo ============================================
echo.
echo Requirements:
echo   - Python 3.10~3.12 (automatically installed using uv if missing)
echo   - ~5GB disk space (for model weights)
echo   - Microphone
echo.

:: ========== Check Python ==========
where python >nul 2>&1
if errorlevel 1 (
    echo [Error] Python not found. Please install Python 3.10~3.12.
    echo Download: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo Python is ready, starting installation...
echo.

:: ========== Run install script ==========
powershell.exe -ExecutionPolicy Bypass -File "install.ps1"

if errorlevel 1 (
    echo.
    echo [Error] Installation failed. Please check errors above.
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================
echo   Installation Completed!
echo   Close this window, double click start.bat to use.
echo ============================================
echo.
pause