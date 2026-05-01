@echo off
REM Quick start script for Windows
REM This script runs the Support Triage Agent

echo.
echo ========================================
echo Multi-Domain Support Triage Agent
echo ========================================
echo.

cd code

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

REM Run the agent
echo Starting agent...
echo.

python agent.py %*

pause
