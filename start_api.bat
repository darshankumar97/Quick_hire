@echo off
REM Time Series Forecasting System - Startup Script
REM Usage: Run this script to start the API server

echo.
echo ============================================================================
echo Time Series Forecasting System - API Server Startup
echo ============================================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please ensure Python 3.14+ is installed
    pause
    exit /b 1
)

echo [1/3] Checking dependencies...
python -c "import fastapi; import uvicorn; print('OK')" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Required packages not installed
    echo Please run: pip install -r requirements.txt
    pause
    exit /b 1
)
echo ✓ Dependencies verified

echo.
echo [2/3] Loading forecasting data...
python -c "from pathlib import Path; files = list(Path('.').glob('*.xlsx')); print(f'✓ Found Excel file: {files[0]}' if files else 'WARNING: No Excel file found')" 2>&1
if errorlevel 1 (
    echo WARNING: Excel file not found in project root
    echo Forecasts will be loaded from outputs/forecasts.csv
)

echo.
echo [3/3] Starting API server...
echo.
echo ============================================================================
echo API Server Starting...
echo ============================================================================
echo.
echo Base URL: http://localhost:8000
echo Documentation: http://localhost:8000/docs
echo Alternative Docs: http://localhost:8000/redoc
echo.
echo Press Ctrl+C to stop the server
echo.
echo ============================================================================
echo.

REM Start the API server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

if errorlevel 1 (
    echo.
    echo ERROR: Failed to start API server
    pause
    exit /b 1
)

pause
