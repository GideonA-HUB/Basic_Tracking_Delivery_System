from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os

@csrf_exempt
def debug_environment(request):
    """Debug endpoint to check all environment variables"""
    try:
        # Get all environment variables
        env_vars = dict(os.environ)
        
        # Filter important variables
        important_vars = {}
        for key, value in env_vars.items():
            if any(important_key in key.upper() for important_key in ['REDIS', 'PORT', 'DATABASE', 'PG', 'DB_']):
                important_vars[key] = value[:100] + "..." if len(str(value)) > 100 else value
        
        return JsonResponse({
            'status': 'success',
            'message': 'Environment variables debug',
            'important_variables': important_vars,
            'total_variables': len(env_vars),
            'redis_url': os.environ.get('REDIS_URL', 'Not set'),
            'port': os.environ.get('PORT', 'Not set'),
            'database_url': os.environ.get('DATABASE_URL', 'Not set')
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
