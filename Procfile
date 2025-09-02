web: python manage.py migrate --settings=delivery_tracker.settings_production && python manage.py collectstatic --noinput --settings=delivery_tracker.settings_production && gunicorn delivery_tracker.wsgi:application --bind 0.0.0.0:$PORT --env DJANGO_SETTINGS_MODULE=delivery_tracker.settings_production
worker: celery -A delivery_tracker worker --loglevel=info --settings=delivery_tracker.settings_production
beat: celery -A delivery_tracker beat --loglevel=info --settings=delivery_tracker.settings_production
