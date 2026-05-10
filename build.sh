#!/bin/bash
set -e

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Collecting static files..."
cd backend
python manage.py collectstatic --noinput

echo "Running migrations..."
python manage.py migrate

echo "Initializing data..."
python init_data.py

echo "Build complete!"
