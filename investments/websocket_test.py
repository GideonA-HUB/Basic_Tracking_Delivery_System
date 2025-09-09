from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import os

@csrf_exempt
def websocket_test(request):
    """Test WebSocket configuration"""
    try:
        # Check channel layers configuration
        channel_layers = getattr(settings, 'CHANNEL_LAYERS', {})
        default_layer = channel_layers.get('default', {})
        
        # Check Redis URL
        redis_url = os.environ.get('REDIS_URL', 'Not set')
        
        # Check ASGI application
        asgi_app = getattr(settings, 'ASGI_APPLICATION', 'Not set')
        
        return JsonResponse({
            'status': 'success',
            'message': 'WebSocket configuration test',
            'channel_layers': {
                'backend': default_layer.get('BACKEND', 'Not configured'),
                'config': default_layer.get('CONFIG', {}),
                'redis_url': redis_url
            },
            'asgi_application': asgi_app,
            'redis_available': redis_url != 'Not set',
            'websocket_support': 'channels_redis' in str(default_layer.get('BACKEND', '')),
            'expected_websocket_url': f"wss://{request.get_host()}/ws/price-feeds/"
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
