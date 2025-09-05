from celery.schedules import crontab

# Celery Beat schedule for automated price updates
CELERY_BEAT_SCHEDULE = {
    # Update prices every 5 minutes
    'update-real-time-prices': {
        'task': 'investments.tasks.update_real_time_prices',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
    },
    
    # Update user portfolio values every 10 minutes
    'update-user-portfolio-values': {
        'task': 'investments.tasks.update_user_portfolio_values',
        'schedule': crontab(minute='*/10'),  # Every 10 minutes
    },
    
    # Health check every hour
    'health-check-price-feeds': {
        'task': 'investments.tasks.health_check_price_feeds',
        'schedule': crontab(minute=0),  # Every hour
    },
    
    # Generate price alerts every 15 minutes
    'generate-price-alerts': {
        'task': 'investments.tasks.generate_price_alerts',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
    },
    
    # Update price statistics every hour
    'update-price-statistics': {
        'task': 'investments.tasks.update_price_statistics',
        'schedule': crontab(minute=30),  # Every hour at 30 minutes
    },
    
    # Clean up old price history daily at midnight
    'cleanup-old-price-history': {
        'task': 'investments.tasks.cleanup_old_price_history',
        'schedule': crontab(hour=0, minute=0),  # Daily at midnight
    },
    
    # Update investment item prices every 2 minutes
    'update-investment-item-prices': {
        'task': 'investments.tasks.update_investment_item_prices',
        'schedule': crontab(minute='*/2'),  # Every 2 minutes
    },
}

# Timezone for Celery Beat
CELERY_TIMEZONE = 'UTC'
