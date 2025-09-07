from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'deliveries', views.DeliveryViewSet)
router.register(r'status-updates', views.DeliveryStatusViewSet)

app_name = 'tracking'

urlpatterns = [
    # API endpoints
    path('', include(router.urls)),
    
    # Public tracking endpoint
    path('track/<str:tracking_number>/<str:tracking_secret>/', 
         views.TrackingAPIView.as_view(), name='track_delivery'),
    
    # Search and stats endpoints
    path('search/', views.DeliverySearchAPIView.as_view(), name='search_deliveries'),
    path('stats/', views.DeliveryStatsAPIView.as_view(), name='delivery_stats'),
    
    # Email test endpoint (for production testing)
    path('test-email/', views.test_email_endpoint, name='test_email'),
]
