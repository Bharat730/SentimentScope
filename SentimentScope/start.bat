@echo off
title SentimentScope — Server
echo.
echo  =========================================
echo    SentimentScope - Starting up...
echo  =========================================
echo.

:: Activate virtual environment
call "%~dp0venv\Scripts\activate.bat"

:: Find local IP address
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4 Address"') do (
    set LOCAL_IP=%%a
    goto :found
)
:found
set LOCAL_IP=%LOCAL_IP: =%

echo  [1/2] Virtual environment activated.
echo  [2/2] Starting backend server...
echo.
echo  =========================================
echo   App is running! Open in browser:
echo.
echo   Your device  : http://localhost:8000
echo   Other devices: http://%LOCAL_IP%:8000
echo  =========================================
echo.
echo   Press CTRL+C to stop the server.
echo.

cd "%~dp0backend"
uvicorn main:app --host 0.0.0.0 --port 8000

pause
