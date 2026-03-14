@echo off
setlocal EnableExtensions
cd /d "%~dp0"

where py >nul 2>&1
if errorlevel 1 (
  where python >nul 2>&1
  if errorlevel 1 (
    echo Python is required. Install it from https://www.python.org/downloads/
    pause
    exit /b 1
  )
  set "PY=python"
) else (
  set "PY=py"
)

if not exist "venv\\Scripts\\python.exe" (
  %PY% -m venv venv
)

call "venv\\Scripts\\activate.bat"
python -m pip install --upgrade pip

if exist requirements.txt (
  python -m pip install -r requirements.txt
)

python app.py

set "RC=%ERRORLEVEL%"
echo.
echo App closed with code %RC%.
pause
exit /b %RC%
