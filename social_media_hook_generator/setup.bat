@echo off
REM Quick Setup Script for Social Media Hook Generator (Windows)

echo Setting up Social Media Hook Generator...
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed. Please install Python 3.8+ first.
    pause
    exit /b 1
)

echo Python found:
python --version
echo.

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements.txt

if not exist ".env" (
    echo Creating .env file from template...
    copy .env.example .env >nul
    echo IMPORTANT: Edit .env and add your API keys.
) else (
    echo .env file already exists.
)

findstr /C:"SECRET_KEY=your-secret-key-here" .env >nul
if %errorlevel% equ 0 (
    echo Generating new secret key...
    python -c "import secrets; from pathlib import Path; env_path = Path('.env'); content = env_path.read_text(); content = content.replace('SECRET_KEY=your-secret-key-here', f'SECRET_KEY={secrets.token_hex(32)}'); env_path.write_text(content); print('Secret key generated and saved')"
) else (
    echo Secret key already configured.
)

echo.
echo Setup complete.
echo 1. Edit .env with your API keys
echo 2. Run: python app.py
echo 3. Open http://localhost:5000 in your browser
echo.
pause
