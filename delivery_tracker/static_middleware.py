"""
Emergency static files middleware to serve static files when collectstatic fails
"""
import os
from django.http import HttpResponse, Http404
from django.conf import settings
import mimetypes

class EmergencyStaticMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if this is a static file request
        if request.path.startswith('/static/'):
            return self.serve_static_file(request)
        
        response = self.get_response(request)
        return response

    def serve_static_file(self, request):
        # Get the file path
        static_path = request.path[8:]  # Remove '/static/' prefix
        
        # Try multiple locations
        possible_paths = [
            os.path.join(settings.STATIC_ROOT, static_path),
            os.path.join(settings.BASE_DIR, 'static', static_path),
            os.path.join(settings.BASE_DIR, 'staticfiles', static_path),
        ]
        
        for file_path in possible_paths:
            if os.path.exists(file_path) and os.path.isfile(file_path):
                try:
                    with open(file_path, 'rb') as f:
                        content = f.read()
                    
                    # Get content type
                    content_type, _ = mimetypes.guess_type(file_path)
                    if not content_type:
                        if file_path.endswith('.js'):
                            content_type = 'application/javascript'
                        elif file_path.endswith('.css'):
                            content_type = 'text/css'
                        else:
                            content_type = 'application/octet-stream'
                    
                    response = HttpResponse(content, content_type=content_type)
                    response['Cache-Control'] = 'public, max-age=3600'
                    return response
                    
                except Exception as e:
                    print(f"Error serving static file {file_path}: {e}")
                    continue
        
        # If file not found, return 404
        raise Http404("Static file not found")
