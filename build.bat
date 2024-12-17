@echo off

echo Checking Python version and building Koala...

:: Python version check
python -c "import sys; ver = sys.version_info; exit(1) if ver.major != 3 or ver.minor < 11 else exit(0)" >nul 2>&1
if errorlevel 1 (
    echo Error: Python 3.11 or higher is required.
    echo Current Python version:
    python --version
    echo.
    echo Please install Python 3.11 or higher and try again.
    pause
    exit /b 1
)

:: Clean previous build
echo Cleaning previous build...
rd /s /q "build" 2>nul
rd /s /q "dist" 2>nul
rd /s /q "venv" 2>nul

:: Create venv
echo Creating virtual environment...
python -m venv venv

:: Activate venv
echo Activating virtual environment...
call venv\Scripts\activate.bat

:: Install dependencies
echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

:: Build with PyInstaller
echo Building executable...
python -m PyInstaller Koala.spec

:: Deactivate venv
deactivate

echo Build complete!
echo Executable is located in the dist folder

pause
