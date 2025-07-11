#!/bin/bash

echo "Starting backend server..."
gnome-terminal --working-directory=backend -- /bin/sh -c 'source .venv/bin/activate; python manage.py runserver 0.0.0.0:8000; exec bash'

echo "Starting frontend server..."
gnome-terminal --working-directory=frontend -- /bin/sh -c 'npm run dev; exec bash'
