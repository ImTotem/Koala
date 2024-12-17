@echo off
echo Checking Python version and building Koala...

:: Python 버전 확인
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

:: 기존 빌드 폴더 삭제
echo Cleaning previous build...
rd /s /q "build" 2>nul
rd /s /q "dist" 2>nul
rd /s /q "venv" 2>nul

:: venv 생성
echo Creating virtual environment...
python -m venv venv

:: venv 활성화
echo Activating virtual environment...
call venv\Scripts\activate

:: 의존성 설치
echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

:: PyInstaller로 빌드
echo Building executable...
python -m PyInstaller Koala.spec

:: venv 비활성화
deactivate

echo Build complete!
echo Executable is located in the dist folder

pause
