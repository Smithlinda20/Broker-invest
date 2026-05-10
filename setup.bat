@echo off
echo =======================================
echo Broker Invest - Setup Script
echo =======================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo [1/5] Creating virtual environment...
cd backend
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo [2/5] Activating virtual environment...
call venv\Scripts\activate

echo [3/5] Installing dependencies...
pip install --default-timeout=1000 -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo [4/5] Running migrations...
python manage.py makemigrations
python manage.py migrate
if errorlevel 1 (
    echo ERROR: Migrations failed
    pause
    exit /b 1
)

echo [5/5] Initializing data...
python init_data.py
if errorlevel 1 (
    echo ERROR: Data initialization failed
    pause
    exit /b 1
)

echo.
echo =======================================
echo ✅ Setup Complete!
echo =======================================
echo.
echo Next steps:
echo 1. Create superuser: python manage.py createsuperuser
echo 2. Start server: python manage.py runserver
echo 3. Access: http://localhost:8000
echo.
echo Admin Panel: http://localhost:8000/backend/admin/
echo API: http://localhost:8000/api/
echo.
pause
