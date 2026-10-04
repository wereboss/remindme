@echo off
REM ==============================================================================
REM Cross-Platform Launcher for Windows Command Prompt
REM Notes & Reminders PWA (RemindMe)
REM ==============================================================================

setlocal enabledelayedexpansion
title RemindMe PWA Launcher

echo ==========================================
echo  Starting Notes & Reminders PWA Service
echo  Platform: Windows
echo ==========================================

REM Locate Python
where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    set PY_CMD=python
) else (
    where py >nul 2>nul
    if %ERRORLEVEL% EQU 0 (
        set PY_CMD=py -3
    ) else (
        echo Error: Python was not found in your PATH.
        echo Please install Python 3.10+ from https://www.python.org/ (ensure "Add Python to PATH" is checked).
        pause
        exit /b 1
    )
)

REM Setup virtual environment
if not exist ".venv" (
    echo Creating virtual environment in .venv...
    %PY_CMD% -m venv .venv
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to create virtual environment.
        pause
        exit /b 1
    )
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

echo Verifying dependencies...
pip install --quiet -r requirements.txt

set PORT=9031

echo.
echo RemindMe PWA is running on:
echo  -^> Local:   http://localhost:%PORT%
echo  -^> Network: http://0.0.0.0:%PORT%
echo.
echo Press Ctrl+C to stop the server.
echo.

REM Open default browser
start http://localhost:%PORT%

python run.py

pause
