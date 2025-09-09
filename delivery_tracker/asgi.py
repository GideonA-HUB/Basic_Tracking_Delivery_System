"""
ASGI config for delivery_tracker project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
import django
from django.core.asgi import get_asgi_application

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')

# Initialize Django
django.setup()

# Import WebSocket routing after Django is initialized
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from investments.routing import websocket_urlpatterns as investment_websocket_urlpatterns
from tracking.routing import websocket_urlpatterns as tracking_websocket_urlpatterns

# Combine all WebSocket URL patterns
all_websocket_urlpatterns = investment_websocket_urlpatterns + tracking_websocket_urlpatterns

# Debug: Print WebSocket patterns
print("🔌 WebSocket URL patterns configured:")
for pattern in all_websocket_urlpatterns:
    print(f"  - {pattern.pattern}")

print("🔌 ASGI application configured for WebSocket support")
print("🔌 Redis channel layer configured for message handling")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            all_websocket_urlpatterns
        )
    ),
})
