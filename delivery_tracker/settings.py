"""
Django settings for delivery_tracker project.
"""

import os
from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-your-secret-key-here')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1,*', cast=lambda v: [s.strip() for s in v.split(',')])

# Use X-Forwarded headers for external access (port forwarding)
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
    'channels',
    'tracking',
    'accounts',
    'investments',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'tracking.middleware.CustomCsrfViewMiddleware',  # Custom CSRF middleware
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'delivery_tracker.static_middleware.EmergencyStaticMiddleware',  # Emergency static files
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

# Django Channels Configuration
ASGI_APPLICATION = 'delivery_tracker.asgi.application'

# Channel Layers for WebSocket support
# Channels Configuration
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379')],
        },
    },
}

# Debug Redis configuration
redis_url = os.environ.get('REDIS_URL', 'Not set')
print(f"🔍 Redis URL: {redis_url}")
print(f"🔍 Using Redis for WebSocket channels: {redis_url != 'Not set'}")

# Database Configuration for Railway
# Railway provides database variables in different formats
import dj_database_url

# Try multiple Railway database variable formats
DATABASE_URL = (
    os.environ.get('DATABASE_URL') or  # Most common Railway format
    os.environ.get('PGDATABASE_URL') or  # Alternative Railway format
    os.environ.get('POSTGRES_URL') or  # Another Railway format
    None
)

if DATABASE_URL:
    # Railway provides DATABASE_URL
    try:
        DATABASES = {
            'default': dj_database_url.parse(DATABASE_URL)
        }
        print(f"✅ Using DATABASE_URL: {DATABASE_URL[:50]}...")
    except Exception as e:
        print(f"❌ Error parsing DATABASE_URL: {e}")
        DATABASE_URL = None

if not DATABASE_URL:
    # Try individual PostgreSQL environment variables (Railway format)
    db_name = (
        os.environ.get('PGDATABASE') or
        os.environ.get('DB_NAME') or
        'tracking_db'
    )
    
    db_user = (
        os.environ.get('PGUSER') or
        os.environ.get('DB_USER') or
        'tracking_app'
    )
    
    db_password = (
        os.environ.get('PGPASSWORD') or
        os.environ.get('DB_PASSWORD') or
        'gN9zM5pQ#W4vY2@r!C8tL6xD'
    )
    
    db_host = (
        os.environ.get('PGHOST') or
        os.environ.get('DB_HOST') or
        'localhost'
    )
    
    db_port = (
        os.environ.get('PGPORT') or
        os.environ.get('DB_PORT') or
        '5432'
    )
    
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': db_name,
            'USER': db_user,
            'PASSWORD': db_password,
            'HOST': db_host,
            'PORT': db_port,
        }
    }
    
    print(f"✅ Using individual DB vars - HOST: {db_host}, PORT: {db_port}, NAME: {db_name}, USER: {db_user}")

# Debug: Print all database-related environment variables
print("🔍 Database environment variables:")
for key, value in os.environ.items():
    if any(db_key in key.upper() for db_key in ['DATABASE', 'PG', 'DB_']):
        print(f"  {key}: {value[:20]}..." if len(str(value)) > 20 else f"  {key}: {value}")

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

# Static files finders
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Static files storage - Force simple storage to avoid manifest issues
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Disable static files manifest completely
STATICFILES_USE_HASHING = False

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

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# CSRF settings for external access
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', default='http://localhost:8000,http://127.0.0.1:8000,https://meridianassetlogistics.com', cast=lambda v: [s.strip() for s in v.split(',')])
CSRF_COOKIE_SECURE = not DEBUG  # True in production, False in development
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_USE_SESSIONS = True

# For development, disable CSRF origin checking (remove in production)
if DEBUG:
    CSRF_COOKIE_SECURE = False
    CSRF_COOKIE_SAMESITE = None

# Tracking link settings
TRACKING_LINK_EXPIRY_DAYS = 30
TRACKING_LINK_SECRET_LENGTH = 32

# Authentication settings
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

# Investment System Settings
SITE_URL = config('SITE_URL', default='https://meridianassetlogistics.com')

# Google Maps API Key for live tracking
GOOGLE_MAPS_API_KEY = config('GOOGLE_MAPS_API_KEY', default='')

# NOWPayments Configuration
NOWPAYMENTS_API_KEY = config('NOWPAYMENTS_API_KEY', default='')
NOWPAYMENTS_IPN_SECRET = config('NOWPAYMENTS_IPN_SECRET', default='')
NOWPAYMENTS_IPN_URL = config('NOWPAYMENTS_IPN_URL', default='https://meridianassetlogistics.com/investments/api/payments/ipn/')

# News API Configuration
NEWSAPI_KEY = config('NEWSAPI_KEY', default='')
FINNHUB_API_KEY = config('FINNHUB_API_KEY', default='')
CRYPTOPANIC_API_KEY = config('CRYPTOPANIC_API_KEY', default='')
COINDESK_API_KEY = config('COINDESK_API_KEY', default='')
NEWS_REFRESH_TOKEN = config('NEWS_REFRESH_TOKEN', default='meridian-news-refresh-2025')

# Email Configuration for Google Workspace (Gmail for Business)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Email Configuration - Multiple fallback strategies for Railway
# Strategy 1: Direct environment variable access
EMAIL_HOST = os.environ.get('EMAIL_HOST') or os.environ.get('SMTP_HOST') or 'smtp.gmail.com'
EMAIL_PORT = int(os.environ.get('EMAIL_PORT') or os.environ.get('SMTP_PORT') or '587')
EMAIL_USE_TLS = (os.environ.get('EMAIL_USE_TLS') or 'True').lower() == 'true'
EMAIL_USE_SSL = (os.environ.get('EMAIL_USE_SSL') or 'False').lower() == 'true'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER') or os.environ.get('SMTP_USER') or 'meridian@meridianassetlogistics.com'
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD') or os.environ.get('SMTP_PASSWORD') or ''
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL') or 'meridian@meridianassetlogistics.com'
SERVER_EMAIL = os.environ.get('SERVER_EMAIL') or 'meridian@meridianassetlogistics.com'

# Debug logging for email configuration
import logging
logger = logging.getLogger(__name__)
logger.info(f"Email configuration loaded - HOST: {EMAIL_HOST}, PORT: {EMAIL_PORT}, USER: {EMAIL_HOST_USER}, TLS: {EMAIL_USE_TLS}")

# Email settings for notifications
ADMINS = [
    ('Meridian Admin', 'meridian@meridianassetlogistics.com'),
]
MANAGERS = ADMINS