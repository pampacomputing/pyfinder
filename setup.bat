:: setup.bat - Robust initialization script for Windows
@echo off
setlocal

set "BASE_DIR=%~dp0"
set "BACKEND_DIR=%BASE_DIR%backend"
set "VENV_DIR=%BACKEND_DIR%\.venv"

echo --- PyFinder Setup ---
echo.
echo Base directory: %BASE_DIR%
echo Backend directory: %BACKEND_DIR%
echo Virtual env directory: %VENV_DIR%
echo.

:: 1. Clean up old virtual environment to ensure a fresh start
if exist "%VENV_DIR%" (
    echo Removing existing virtual environment...
    rmdir /s /q "%VENV_DIR%"
)

:: 2. Create virtual environment
echo Creating new virtual environment...
python -m venv "%VENV_DIR%"
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment.
    exit /b 1
)

:: 3. Install Python dependencies into the new venv
echo Installing Python dependencies from requirements.txt...
call "%VENV_DIR%\Scripts\activate.bat"
pip install -r "%BACKEND_DIR%\requirements.txt"
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Python dependencies.
    exit /b 1
)

:: 4. Copy and configure .env file
if not exist "%BASE_DIR%.env" (
    echo Creating .env file from .env.example...
    copy "%BASE_DIR%.env.example" "%BASE_DIR%.env"
) else (
    echo .env file already exists.
)

:: 5. Install frontend dependencies
echo Installing frontend dependencies...
pushd "%BASE_DIR%frontend"
npm install
if %errorlevel% neq 0 (
    echo ERROR: Failed to install frontend dependencies.
    popd
    exit /b 1
)
popd

echo.
echo --- Setup Complete ---
echo You can now run start.bat to launch the application.
echo.

endlocal
