@echo OFF

ECHO Starting backend server...
start "Backend" cmd /k ".venv\Scripts\activate && python manage.py runserver"

ECHO Starting frontend server...
start "Frontend" cmd /k "cd frontend && npm run dev"
