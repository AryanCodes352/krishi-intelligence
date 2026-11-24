@echo off
title KRISHI Intelligence Launcher
echo ===================================================
echo   Starting KRISHI Intelligence Full-Stack Platform
echo ===================================================
echo.

REM Resolve Python interpreter with uvicorn
set "PY_CMD=python"
python -c "import uvicorn" >nul 2>&1
if %errorlevel% neq 0 (
    if exist "%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe" (
        set "PY_CMD=%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe"
    )
)

echo [1/3] Launching FastAPI Backend on http://localhost:8000 ...
start "KRISHI Backend (FastAPI)" cmd /k "%PY_CMD% -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload"

echo [2/3] Launching Next.js Frontend on http://localhost:3000 ...
start "KRISHI Frontend (Next.js)" cmd /k "cd frontend && npm run dev"

echo [3/3] Waiting 3 seconds for servers to initialize...
timeout /t 3 /nobreak > nul

echo Opening KRISHI Landing Page in your web browser...
start http://localhost:3000

echo.
echo ===================================================
echo   KRISHI is now RUNNING!
echo   - Web App (Home): http://localhost:3000
echo   - Farm Setup:     http://localhost:3000/onboard
echo   - Backend API:    http://localhost:8000
echo   - API Docs:       http://localhost:8000/docs
echo ===================================================
echo (Keep the two terminal windows open while using the app)
pause
