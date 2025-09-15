"""
Production settings for delivery_tracker project.
"""

import os
import logging
from pathlib import Path
from decouple import config
import dj_database_url

logger = logging.getLogger(__name__)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default=os.environ.get('SECRET_KEY'))

# Generate a secure SECRET_KEY if none is provided
if not SECRET_KEY or SECRET_KEY.startswith('django-insecure-'):
    import secrets
    import string
    SECRET_KEY = ''.join(secrets.choice(string.ascii_letters + string.digits + '!@#$%^&*(-_=+)') for _ in range(50))
    logger.warning("Generated a new SECRET_KEY for production. Please set SECRET_KEY environment variable.")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

# Force DEBUG to False in production
if not DEBUG:
    DEBUG = False

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='meridian-asset-logistics.up.railway.app,healthcheck.railway.app,*.railway.app', cast=lambda v: [s.strip() for s in v.split(',')])

# Use X-Forwarded headers for external access
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'channels',  # Add channels for WebSocket support
    'tracking',
    'accounts',
    'investments',
    'chat.apps.ChatConfig',  # Live chat system
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add whitenoise for static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',  # Add CSRF middleware
    'tracking.middleware.CustomCsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'delivery_tracker.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'delivery_tracker.wsgi.application'

# Django Channels Configuration for WebSocket support
ASGI_APPLICATION = 'delivery_tracker.asgi.application'

# Channel Layers for WebSocket support (using Redis or in-memory fallback)
REDIS_URL = os.environ.get('REDIS_URL')
if REDIS_URL:
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                "hosts": [REDIS_URL],
            },
        },
    }
else:
    # Fallback to in-memory channel layer for development/testing
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels.layers.InMemoryChannelLayer',
        },
    }

# Celery Configuration
CELERY_BROKER_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_ENABLE_UTC = True

# Celery Beat Schedule
CELERY_BEAT_SCHEDULE = {
    'update-real-time-prices': {
        'task': 'investments.tasks.update_real_time_prices',
        'schedule': 60.0,  # Every 60 seconds
    },
    'update-investment-prices': {
        'task': 'investments.tasks.update_investment_item_prices',
        'schedule': 120.0,  # Every 2 minutes
    },
}

# Database
# Railway provides DATABASE_URL environment variable
# Use DATABASE_URL if available, otherwise fall back to local SQLite
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    # Production database (Railway)
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # Development database (SQLite)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# WhiteNoise configuration for static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
}

# CORS settings for production
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='https://meridian-asset-logistics.up.railway.app,https://web-production-9c4aa.up.railway.app', cast=lambda v: [s.strip() for s in v.split(',') if s.strip()])
CORS_ALLOW_CREDENTIALS = True

# CSRF settings for production
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', default='https://meridian-asset-logistics.up.railway.app,https://web-production-9c4aa.up.railway.app', cast=lambda v: [s.strip() for s in v.split(',') if s.strip()])
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_USE_SESSIONS = True
CSRF_COOKIE_DOMAIN = None
CSRF_COOKIE_HTTPONLY = False

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = False  # Disabled to prevent redirect loop on Railway

# Session settings
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# Tracking link settings
TRACKING_LINK_EXPIRY_DAYS = 30
TRACKING_LINK_SECRET_LENGTH = 32

# Authentication settings
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

# Investment System Settings
SITE_URL = config('SITE_URL', default='https://meridian-asset-logistics.up.railway.app')

# Google Maps API Key for live tracking
GOOGLE_MAPS_API_KEY = config('GOOGLE_MAPS_API_KEY', default='')

# NOWPayments Configuration
NOWPAYMENTS_API_KEY = config('NOWPAYMENTS_API_KEY', default='')
NOWPAYMENTS_IPN_SECRET = config('NOWPAYMENTS_IPN_SECRET', default='')
NOWPAYMENTS_IPN_URL = config('NOWPAYMENTS_IPN_URL', default='https://meridian-asset-logistics.up.railway.app/investments/api/payments/ipn/')

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
