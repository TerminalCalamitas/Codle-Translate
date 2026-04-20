@echo off
setlocal EnableDelayedExpansion

echo Beginning installation

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not on PATH. Please install Python 3.13
    pause
    exit /b 1
)

for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set PY_VERSION=%%v
for /f "tokens=1,2 delims=." %%a in ("%PY_VERSION%") do (
  set PY_MAJOR=%%a
  set PY_MINOR=%%b
)

if !PY_MAJOR! LSS 3 (
  echo [ERROR] Python 3.13+ is required. Found: %PY_VERSION%
  pause
  exit /b 1
)

if !PY_MAJOR! EQU 3 if !PY_MINOR! LSS 13 (
  echo [ERROR] Python 3.13+ is required. Found: %PY_VERSION%
  pause
  exit /b 1
)

echo [OK] Python %PY_VERSION% found.


python -m pip --version >nul 2>&1
if errorlevel 1 (
  echo [ERROR] pip not found. Please reinstall Python with pip included.
  pause
  exit /b 1
)

echo [OK] pip found.



poetry --version >nul 2>&1
if errorlevel 1 (
      echo [INFO] Poetry not found. Installing Poetry...
 
    :: Try the official installer via PowerShell first
    powershell -NoProfile -Command "(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -" >nul 2>&1
    if errorlevel 1 (
        echo [INFO] Official installer failed, falling back to pip...
        python -m pip install poetry
        if errorlevel 1 (
            echo [ERROR] Failed to install Poetry.
            pause
            exit /b 1
        )
    )
 
    :: Add Poetry's bin dir to PATH for the rest of this session
    set "PATH=%APPDATA%\Python\Scripts;%PATH%"
 
    poetry --version >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Poetry installed but not found on PATH.
        echo You may need to add its install directory to PATH.
        pause
        exit /b 1
    )
    echo [OK] Poetry installed.

) else (
  echo [OK] Poetry found.
)

echo.
echo [INFO] Installing project dependencies via Poetry...
poetry install

echo.
echo Installation complete!
echo Run the app with: poetry run gui

pause
