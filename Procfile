web: python manage.py migrate && python manage.py collectstatic --noinput && gunicorn delivery_tracker.wsgi:application --bind 0.0.0.0:$PORT
