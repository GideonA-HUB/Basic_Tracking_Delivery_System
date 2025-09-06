from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/track/(?P<tracking_number>[^/]+)/(?P<tracking_secret>[^/]+)/$', 
            consumers.DeliveryTrackingConsumer.as_asgi()),
    re_path(r'ws/admin/delivery-monitoring/$', 
            consumers.AdminDeliveryConsumer.as_asgi()),
]
