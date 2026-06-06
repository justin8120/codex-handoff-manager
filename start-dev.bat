@echo off
chcp 65001 >nul
setlocal

set "ROOT=%~dp0"

if /I "%~1"=="backend" goto backend
if /I "%~1"=="frontend" goto frontend
if /I "%~1"=="help" goto help
if /I "%~1"=="/?" goto help

echo Starting Smart Diet Recommendation System...
echo Project root: %ROOT%

start "Smart Diet - FastAPI Backend" cmd /k call "%~f0" backend
start "Smart Diet - React Vite Frontend" cmd /k call "%~f0" frontend

timeout /t 3 /nobreak >nul
start "" "http://localhost:5173"

echo Backend and frontend windows opened.
exit /b 0

:backend
cd /d "%ROOT%backend"

if not exist ".venv" (
  echo Creating backend virtual environment...
  py -m venv .venv
)

if not exist ".env" (
  echo backend/.env not found. The system can still use AI_PROVIDER=mock, or you can create backend/.env yourself.
)

call ".venv\Scripts\activate.bat"
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
exit /b 0

:frontend
cd /d "%ROOT%"

if not exist "node_modules" (
  echo Installing frontend dependencies...
  npm install
)

npm run dev
exit /b 0

:help
echo Usage:
echo   start-dev.bat
echo   start-dev.bat backend
echo   start-dev.bat frontend
echo.
echo From Command Prompt:
echo   cd /d "%ROOT%"
echo   start-dev.bat
exit /b 0
