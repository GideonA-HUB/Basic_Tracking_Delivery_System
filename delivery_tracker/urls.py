"""
URL configuration for delivery_tracker project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('api/', include('tracking.urls')),
    path('investments/', include('investments.urls', namespace='investments')),
    path('', include('tracking.frontend_urls')),
    path('test-static/', serve, {'document_root': 'static', 'path': 'test.html'}),
]

# ALWAYS serve static files - both development and production
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Additional static files serving for production
if not settings.DEBUG:
    urlpatterns += [
        path('static/<path:path>', serve, {'document_root': settings.STATIC_ROOT}),
    ]
