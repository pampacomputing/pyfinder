@echo OFF
set "BASE_DIR=%~dp0"

ECHO Starting backend server...
rem The 'start' command opens a new window. We must change the directory within that new window.
start "Backend" cmd /k "cd /d "%BASE_DIR%backend" && call .venv\Scripts\activate.bat && python manage.py runserver"

ECHO Starting frontend server...
start "Frontend" cmd /k "cd /d "%BASE_DIR%frontend" && npm run dev"
