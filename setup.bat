:: setup.bat - Initialization script for Windows
@echo off
setlocal enabledelayedexpansion

:: 1. Create virtual environment
python -m venv .venv

:: 2. Activate virtual environment
call .\.venv\Scripts\activate.bat

:: 3. Install Python dependencies
pip install -r requirements.txt

:: 4. Copy and configure .env file
copy .env.example .env

:: 5. Install frontend dependencies
pushd frontend
npm install
popd

:: 6. Start the project
call start.bat
endlocal