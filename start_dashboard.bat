@echo off
setlocal
title Philippine Statistics Authority - Census Dashboard Launcher

echo ======================================================================
echo   Philippine Statistics Authority - 2020 CPH Dashboard Launcher
echo ======================================================================
echo.

cd /d "%~dp0"

:: Check if port 8050 is already listening
netstat -ano | findstr :8050 >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] Dashboard server is already active on http://127.0.0.1:8050/
) else (
    echo [..] Starting dashboard server in the background...
    if exist ".venv\Scripts\python.exe" (
        start "" /B ".venv\Scripts\python.exe" app.py
    ) else (
        start "" /B python app.py
    )
    :: Give the server 3 seconds to initialize
    timeout /t 3 /nobreak >nul
)

echo [OK] Triggering webpage in your default browser...
start "" "http://127.0.0.1:8050/"

echo.
echo ======================================================================
echo   Dashboard opened successfully!
echo   You can close this window at any time.
echo ======================================================================
timeout /t 2 >nul
exit
