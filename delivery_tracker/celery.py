import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings_production')

app = Celery('delivery_tracker')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Celery Configuration
app.conf.update(
    # Broker settings
    broker_url=os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
    
    # Result backend
    result_backend=os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
    
    # Task serialization
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    
    # Timezone
    timezone='UTC',
    enable_utc=True,
    
    # Task routing
    task_routes={
        'investments.tasks.*': {'queue': 'investments'},
    },
    
    # Worker settings
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    
    # Beat schedule for periodic tasks
    beat_schedule={
        'update-real-time-prices': {
            'task': 'investments.tasks.update_real_time_prices',
            'schedule': 60.0,  # Every 60 seconds
        },
        'update-investment-prices': {
            'task': 'investments.tasks.update_investment_item_prices',
            'schedule': 120.0,  # Every 2 minutes
        },
    },
)

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
