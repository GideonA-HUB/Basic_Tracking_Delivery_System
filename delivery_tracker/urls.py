"""
URL configuration for delivery_tracker project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('api/', include('tracking.urls')),
    path('', include('tracking.frontend_urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
