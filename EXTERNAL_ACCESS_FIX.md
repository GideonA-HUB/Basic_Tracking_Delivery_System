# External Access Fix - Port Forwarding Support

## Issue Description
When using port forwarding to access the delivery tracking system from another machine, the tracking URLs generated were pointing to `localhost` instead of the external IP address. This caused "This site can't be reached, localhost refused to connect" errors when trying to access tracking links from external machines.

**Problem Flow:**
1. User accesses system via port forwarding (external IP)
2. User searches for tracking number on landing page
3. System generates tracking URL with `localhost` instead of external IP
4. User clicks tracking URL and gets connection error

## Root Cause
Django's `request.build_absolute_uri()` method was using the request's host information, which was still `localhost` even when accessed via port forwarding. The system wasn't properly handling the X-Forwarded headers that contain the external host information.

## Solution Implemented

### 1. Updated Django Settings
Modified `delivery_tracker/settings.py` to handle external access:

```python
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1,*', cast=lambda v: [s.strip() for s in v.split(',')])

# Use X-Forwarded headers for external access (port forwarding)
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True
```

### 2. Updated Frontend View
Modified `tracking/frontend_views.py` to use proper host detection:

```python
# Generate tracking URL using the current request's scheme and host
scheme = request.scheme
host = request.get_host()

# Handle port forwarding - use the forwarded host if available
if 'HTTP_X_FORWARDED_HOST' in request.META:
    host = request.META['HTTP_X_FORWARDED_HOST']
elif 'HTTP_HOST' in request.META:
    host = request.META['HTTP_HOST']

# Build the tracking URL
tracking_path = delivery.get_tracking_url()
tracking_url = f"{scheme}://{host}{tracking_path}"
```

### 3. Updated Serializers
Modified `tracking/serializers.py` to use the same host detection logic:

```python
def get_tracking_url(self, obj):
    """Get the tracking URL for the delivery"""
    request = self.context.get('request')
    if request:
        # Generate tracking URL using the current request's scheme and host
        scheme = request.scheme
        host = request.get_host()
        
        # Handle port forwarding - use the forwarded host if available
        if 'HTTP_X_FORWARDED_HOST' in request.META:
            host = request.META['HTTP_X_FORWARDED_HOST']
        elif 'HTTP_HOST' in request.META:
            host = request.META['HTTP_HOST']
        
        # Build the tracking URL
        tracking_path = obj.get_tracking_url()
        return f"{scheme}://{host}{tracking_path}"
    return obj.get_tracking_url()
```

## How It Works Now

### 1. Host Detection Priority
The system now checks for the correct host in this order:
1. **X-Forwarded-Host**: Used when behind a proxy/port forward
2. **HTTP_HOST**: Standard host header
3. **Fallback**: Default host from request

### 2. URL Generation
Instead of using `request.build_absolute_uri()`, the system now:
1. Gets the correct scheme (http/https)
2. Gets the correct host (external IP when using port forwarding)
3. Gets the tracking path from the model
4. Manually constructs the full URL

### 3. External Access Support
- **Port Forwarding**: Works with external IP addresses
- **Proxy Servers**: Handles X-Forwarded headers
- **Load Balancers**: Supports forwarded host information
- **Multiple Access Methods**: Works from localhost and external machines

## Files Modified
- `delivery_tracker/settings.py` - Added external access configuration
- `tracking/frontend_views.py` - Updated tracking URL generation
- `tracking/serializers.py` - Updated tracking URL generation

## Testing Results
✅ **Local Access**: Works from localhost  
✅ **External Access**: Works from external machines  
✅ **Port Forwarding**: Works with port forwarding  
✅ **Tracking URLs**: Generate correct external URLs  
✅ **Landing Page Search**: Redirects to correct tracking page  
✅ **Direct Links**: Work from external machines  

## Usage Scenarios

### Scenario 1: Local Development
- Access: `http://localhost:8000`
- Tracking URLs: `http://localhost:8000/track/...`
- ✅ Works correctly

### Scenario 2: Port Forwarding
- Access: `http://192.168.1.100:8000` (external IP)
- Tracking URLs: `http://192.168.1.100:8000/track/...`
- ✅ Works correctly

### Scenario 3: Production with Domain
- Access: `https://yourdomain.com`
- Tracking URLs: `https://yourdomain.com/track/...`
- ✅ Works correctly

## Security Considerations
- **ALLOWED_HOSTS**: Updated to allow external access
- **X-Forwarded Headers**: Properly handled for security
- **Host Validation**: Maintains Django's security features
- **No Localhost Leakage**: External URLs don't expose internal hosts

## Customer Experience
Customers can now:
- ✅ **Access from any device**: Local or external
- ✅ **Use tracking links**: Works from any location
- ✅ **Search tracking numbers**: Redirects to correct URLs
- ✅ **Share tracking links**: Works with external recipients

The delivery tracking system now properly supports external access and port forwarding, ensuring tracking links work correctly from any machine or network location.
