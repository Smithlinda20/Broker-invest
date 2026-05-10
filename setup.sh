#!/bin/bash

echo "======================================="
echo "Broker Invest - Setup Script"
echo "======================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    exit 1
fi

echo "[1/5] Creating virtual environment..."
cd backend
python3 -m venv venv

echo "[2/5] Activating virtual environment..."
source venv/bin/activate

echo "[3/5] Installing dependencies..."
pip install --default-timeout=1000 -r requirements.txt

echo "[4/5] Running migrations..."
python manage.py makemigrations
python manage.py migrate

echo "[5/5] Initializing data..."
python init_data.py

echo ""
echo "======================================="
echo "✅ Setup Complete!"
echo "======================================="
echo ""
echo "Next steps:"
echo "1. Create superuser: python manage.py createsuperuser"
echo "2. Start server: python manage.py runserver"
echo "3. Access: http://localhost:8000"
echo ""
echo "Admin Panel: http://localhost:8000/backend/admin/"
echo "API: http://localhost:8000/api/"
echo ""
