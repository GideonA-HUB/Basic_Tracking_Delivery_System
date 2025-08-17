from django.middleware.csrf import CsrfViewMiddleware
from django.conf import settings


class CustomCsrfViewMiddleware(CsrfViewMiddleware):
    """
    Custom CSRF middleware that handles external access and port forwarding.
    """
    
    def process_request(self, request):
        # Handle CSRF for both development and production
        if 'HTTP_REFERER' not in request.META and 'HTTP_HOST' in request.META:
            scheme = request.scheme
            host = request.META['HTTP_HOST']
            request.META['HTTP_REFERER'] = f"{scheme}://{host}/"
        
        return super().process_request(request)
