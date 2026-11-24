@echo off
title KRISHI Intelligence - Cloudflare Tunnel Public Sharing
color 0A
cls

echo ===============================================================================
echo                KRISHI INTELLIGENCE - PUBLIC TUNNEL LAUNCHER
echo ===============================================================================
echo.
echo [1/3] Checking FastAPI Backend (Port 8000)...
curl.exe -s http://127.0.0.1:8000/docs >nul 2>&1
if %errorlevel% neq 0 (
    echo [*] Starting FastAPI Backend on port 8000...
    start /B "" "C:\Users\aryan\AppData\Local\Python\pythoncore-3.14-64\python.exe" -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
    timeout /t 3 /nobreak >nul
) else (
    echo [OK] Backend is already running on port 8000.
)

echo.
echo [2/3] Checking Next.js Frontend (Port 3000)...
curl.exe -s -I http://127.0.0.1:3000 >nul 2>&1
if %errorlevel% neq 0 (
    echo [*] Starting Next.js Production Server on port 3000...
    start /B "" node "C:\Users\aryan\Desktop\KRISHI\frontend\node_modules\next\dist\bin\next" start "C:\Users\aryan\Desktop\KRISHI\frontend" -p 3000
    timeout /t 3 /nobreak >nul
) else (
    echo [OK] Frontend is already running on port 3000.
)

echo.
echo [3/3] Launching Cloudflare Tunnel (High-Speed Edge Routing)...
echo [*] Your public HTTPS link will appear below (look for *.trycloudflare.com):
echo [*] Keep this command prompt window open to keep the link active!
echo ===============================================================================
echo.

tools\cloudflared.exe tunnel --url http://127.0.0.1:3000
pause
