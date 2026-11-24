@echo off
echo =====================================================
echo  KRISHI INTELLIGENCE - Setup and Start
echo =====================================================
echo.

echo [1/4] Installing Python backend dependencies...
pip install -r backend/requirements.txt -q
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Python dependencies.
    echo Make sure Python 3.11+ is installed.
    pause
    exit /b 1
)

echo [2/4] Training price prediction model...
python ml/train_price_model.py
if %errorlevel% neq 0 (
    echo WARNING: Model training failed. Price predictions will be unavailable.
    echo You can train manually later with: python ml/train_price_model.py
)

echo [3/4] Installing frontend dependencies...
cd frontend
call npm install --silent
if %errorlevel% neq 0 (
    echo ERROR: Failed to install frontend dependencies.
    echo Make sure Node.js 18+ is installed.
    cd ..
    pause
    exit /b 1
)
cd ..

echo [4/4] Starting servers...
echo.
echo  Backend:  http://localhost:8000
echo  Frontend: http://localhost:3000
echo  API Docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop.
echo.

set "PY_CMD=python"
python -c "import uvicorn" >nul 2>&1
if %errorlevel% neq 0 (
    if exist "%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe" (
        set "PY_CMD=%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe"
    )
)
start "KRISHI Backend" cmd /k "%PY_CMD% -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload"
timeout /t 3 /nobreak > nul
start "KRISHI Frontend" cmd /k "cd frontend && npm run dev"
timeout /t 3 /nobreak > nul

echo Opening KRISHI Landing Page in your web browser...
start http://localhost:3000

echo Both servers started. Open http://localhost:3000 in your browser.
pause
