#!/bin/bash

echo "Starting backend server..."
gnome-terminal -- /bin/sh -c 'source .venv/bin/activate; python manage.py runserver; exec bash'

echo "Starting frontend server..."
gnome-terminal --working-directory=frontend -- /bin/sh -c 'npm run dev; exec bash'
