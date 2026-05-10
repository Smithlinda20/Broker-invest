web: cd backend && gunicorn broker_core.wsgi:application --bind 0.0.0.0:$PORT
release: cd backend && python manage.py migrate && python init_data.py
