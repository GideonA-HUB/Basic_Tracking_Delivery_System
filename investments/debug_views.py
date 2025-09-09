from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.utils import timezone
import os

@csrf_exempt
def debug_database(request):
    """Debug endpoint to check database configuration"""
    try:
        # Get all environment variables
        env_vars = dict(os.environ)
        
        # Filter database-related variables
        db_vars = {}
        for key, value in env_vars.items():
            if any(db_key in key.upper() for db_key in ['DATABASE', 'PG', 'DB_']):
                db_vars[key] = value[:50] + "..." if len(str(value)) > 50 else value
        
        # Get Django database settings
        django_db_config = {}
        if hasattr(settings, 'DATABASES'):
            db_config = settings.DATABASES.get('default', {})
            django_db_config = {
                'ENGINE': db_config.get('ENGINE', 'Not set'),
                'NAME': db_config.get('NAME', 'Not set'),
                'USER': db_config.get('USER', 'Not set'),
                'HOST': db_config.get('HOST', 'Not set'),
                'PORT': db_config.get('PORT', 'Not set'),
                'PASSWORD': 'SET' if db_config.get('PASSWORD') else 'NOT_SET'
            }
        
        return JsonResponse({
            'status': 'success',
            'message': 'Database debug information',
            'timestamp': str(timezone.now()),
            'environment_variables': db_vars,
            'django_database_config': django_db_config,
            'all_env_vars_count': len(env_vars)
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
