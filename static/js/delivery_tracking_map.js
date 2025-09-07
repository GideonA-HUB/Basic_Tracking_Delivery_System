// Delivery Tracking Map JavaScript
let map = null;
let currentMarker = null;
let pickupMarker = null;
let deliveryMarker = null;
let deliveryPath = null;
let websocket = null;

// Google Maps initialization
function initMap() {
    console.log('🗺️ Initializing Google Maps...');
    
    // Default center (will be updated with actual data)
    const defaultCenter = { lat: 40.7128, lng: -74.0060 }; // New York City
    
    map = new google.maps.Map(document.getElementById('delivery-map'), {
        zoom: 12,
        center: defaultCenter,
        mapTypeId: google.maps.MapTypeId.ROADMAP,
        styles: [
            {
                featureType: 'poi',
                elementType: 'labels',
                stylers: [{ visibility: 'off' }]
            }
        ]
    });
    
    console.log('✅ Google Maps initialized');
}

// WebSocket connection for real-time updates
function initWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/track/${TRACKING_NUMBER}/${TRACKING_SECRET}/`;
    
    console.log('🔌 Connecting to WebSocket:', wsUrl);
    
    websocket = new WebSocket(wsUrl);
    
    websocket.onopen = function() {
        console.log('✅ WebSocket connected');
        updateConnectionStatus(true);
        
        // Request initial data
        websocket.send(JSON.stringify({
            type: 'get_tracking_data'
        }));
    };
    
    websocket.onmessage = function(event) {
        try {
            const data = JSON.parse(event.data);
            console.log('📨 WebSocket message received:', data);
            
            switch (data.type) {
                case 'tracking_data':
                    handleTrackingData(data.data);
                    break;
                case 'location_update':
                    handleLocationUpdate(data);
                    break;
                case 'status_update':
                    handleStatusUpdate(data);
                    break;
                case 'error':
                    console.error('❌ WebSocket error:', data.message);
                    break;
                default:
                    console.log('❓ Unknown message type:', data.type);
            }
        } catch (error) {
            console.error('❌ Error parsing WebSocket message:', error);
        }
    };
    
    websocket.onclose = function() {
        console.log('❌ WebSocket disconnected');
        updateConnectionStatus(false);
        
        // Attempt to reconnect after 5 seconds
        setTimeout(initWebSocket, 5000);
    };
    
    websocket.onerror = function(error) {
        console.error('❌ WebSocket error:', error);
        updateConnectionStatus(false);
    };
}

// Handle tracking data from WebSocket
function handleTrackingData(data) {
    console.log('📊 Handling tracking data:', data);
    window.trackingData = data;
    
    // Update timeline
    if (typeof updateTimeline === 'function') {
        updateTimeline();
    }
    
    // Update status badge
    if (typeof updateStatusBadge === 'function') {
        updateStatusBadge();
    }
    
    // Update map
    updateMap();
    
    // Update location details
    updateLocationDetails();
    
    // Update courier information
    updateCourierInfo();
    
    // Update GPS status
    updateGPSStatus();
}

// Handle location updates from WebSocket
function handleLocationUpdate(data) {
    console.log('📍 Location update received:', data);
    
    // Update current location marker
    if (data.latitude && data.longitude) {
        updateCurrentLocationMarker(data.latitude, data.longitude, data.location_name);
        updateLocationDetails(data);
    }
}

// Handle status updates from WebSocket
function handleStatusUpdate(data) {
    console.log('📋 Status update received:', data);
    
    // Refresh tracking data
    if (websocket && websocket.readyState === WebSocket.OPEN) {
        websocket.send(JSON.stringify({
            type: 'get_tracking_data'
        }));
    }
}

// Update map with delivery locations
function updateMap() {
    if (!map || !window.trackingData) return;
    
    const delivery = window.trackingData.delivery;
    
    // Clear existing markers and path
    if (currentMarker) currentMarker.setMap(null);
    if (pickupMarker) pickupMarker.setMap(null);
    if (deliveryMarker) deliveryMarker.setMap(null);
    if (deliveryPath) deliveryPath.setMap(null);
    
    const bounds = new google.maps.LatLngBounds();
    let hasLocations = false;
    
    // Add pickup marker
    if (delivery.pickup_location) {
        const pickupPos = new google.maps.LatLng(
            delivery.pickup_location.latitude,
            delivery.pickup_location.longitude
        );
        
        pickupMarker = new google.maps.Marker({
            position: pickupPos,
            map: map,
            title: 'Pickup Location',
            icon: {
                url: 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(`
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <circle cx="12" cy="12" r="10" fill="#10B981" stroke="white" stroke-width="2"/>
                        <path d="M12 6v6l4 2" stroke="white" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                `),
                scaledSize: new google.maps.Size(24, 24),
                anchor: new google.maps.Point(12, 12)
            }
        });
        
        bounds.extend(pickupPos);
        hasLocations = true;
    }
    
    // Add delivery marker
    if (delivery.delivery_location) {
        const deliveryPos = new google.maps.LatLng(
            delivery.delivery_location.latitude,
            delivery.delivery_location.longitude
        );
        
        deliveryMarker = new google.maps.Marker({
            position: deliveryPos,
            map: map,
            title: 'Delivery Location',
            icon: {
                url: 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(`
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <circle cx="12" cy="12" r="10" fill="#EF4444" stroke="white" stroke-width="2"/>
                        <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" fill="white"/>
                    </svg>
                `),
                scaledSize: new google.maps.Size(24, 24),
                anchor: new google.maps.Point(12, 12)
            }
        });
        
        bounds.extend(deliveryPos);
        hasLocations = true;
    }
    
    // Add current location marker
    if (delivery.current_location) {
        updateCurrentLocationMarker(
            delivery.current_location.latitude,
            delivery.current_location.longitude,
            delivery.current_location.location_name
        );
        
        const currentPos = new google.maps.LatLng(
            delivery.current_location.latitude,
            delivery.current_location.longitude
        );
        bounds.extend(currentPos);
        hasLocations = true;
    }
    
    // Fit map to show all markers
    if (hasLocations) {
        map.fitBounds(bounds);
        
        // Ensure minimum zoom level
        google.maps.event.addListenerOnce(map, 'bounds_changed', function() {
            if (map.getZoom() > 15) {
                map.setZoom(15);
            }
        });
    }
    
    // Draw delivery path
    drawDeliveryPath();
}

// Update current location marker
function updateCurrentLocationMarker(latitude, longitude, locationName) {
    if (!map) return;
    
    const position = new google.maps.LatLng(latitude, longitude);
    
    // Remove existing current marker
    if (currentMarker) {
        currentMarker.setMap(null);
    }
    
    // Create new current marker with animation
    currentMarker = new google.maps.Marker({
        position: position,
        map: map,
        title: locationName || 'Current Location',
        icon: {
            url: 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(`
                <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="16" cy="16" r="12" fill="#3B82F6" stroke="white" stroke-width="3"/>
                    <circle cx="16" cy="16" r="6" fill="white"/>
                    <circle cx="16" cy="16" r="2" fill="#3B82F6"/>
                </svg>
            `),
            scaledSize: new google.maps.Size(32, 32),
            anchor: new google.maps.Point(16, 16)
        },
        animation: google.maps.Animation.BOUNCE
    });
    
    // Stop animation after 2 seconds
    setTimeout(() => {
        if (currentMarker) {
            currentMarker.setAnimation(null);
        }
    }, 2000);
    
    // Center map on current location
    map.panTo(position);
}

// Draw delivery path
function drawDeliveryPath() {
    if (!map || !window.trackingData) return;
    
    const delivery = window.trackingData.delivery;
    const pathCoordinates = [];
    
    // Add pickup location
    if (delivery.pickup_location) {
        pathCoordinates.push(new google.maps.LatLng(
            delivery.pickup_location.latitude,
            delivery.pickup_location.longitude
        ));
    }
    
    // Add current location
    if (delivery.current_location) {
        pathCoordinates.push(new google.maps.LatLng(
            delivery.current_location.latitude,
            delivery.current_location.longitude
        ));
    }
    
    // Add delivery location
    if (delivery.delivery_location) {
        pathCoordinates.push(new google.maps.LatLng(
            delivery.delivery_location.latitude,
            delivery.delivery_location.longitude
        ));
    }
    
    // Create polyline
    if (pathCoordinates.length > 1) {
        deliveryPath = new google.maps.Polyline({
            path: pathCoordinates,
            geodesic: true,
            strokeColor: '#3B82F6',
            strokeOpacity: 0.8,
            strokeWeight: 4,
            map: map
        });
    }
}

// Update location details
function updateLocationDetails(locationData = null) {
    const delivery = window.trackingData?.delivery;
    if (!delivery) return;
    
    const currentLocation = locationData || delivery.current_location;
    
    if (currentLocation) {
        document.getElementById('current-location-name').textContent = 
            currentLocation.location_name || 'GPS Location';
        document.getElementById('current-location-coords').textContent = 
            `${currentLocation.latitude.toFixed(6)}, ${currentLocation.longitude.toFixed(6)}`;
        
        // Update last location update time
        const updateTime = locationData?.timestamp || delivery.current_location?.last_update;
        if (updateTime) {
            const date = new Date(updateTime);
            document.getElementById('last-location-update').textContent = 
                `Last update: ${date.toLocaleTimeString()}`;
        }
        
        // Calculate ETA and distance
        calculateETA(currentLocation);
    } else {
        document.getElementById('current-location-name').textContent = 'Location not available';
        document.getElementById('current-location-coords').textContent = '--';
    }
}

// Calculate ETA and distance
function calculateETA(currentLocation) {
    const delivery = window.trackingData?.delivery;
    if (!delivery || !delivery.delivery_location) return;
    
    const currentPos = new google.maps.LatLng(
        currentLocation.latitude,
        currentLocation.longitude
    );
    
    const deliveryPos = new google.maps.LatLng(
        delivery.delivery_location.latitude,
        delivery.delivery_location.longitude
    );
    
    // Calculate distance
    const distance = google.maps.geometry.spherical.computeDistanceBetween(currentPos, deliveryPos);
    const distanceKm = (distance / 1000).toFixed(1);
    
    document.getElementById('distance-display').textContent = `${distanceKm} km remaining`;
    
    // Estimate ETA (assuming average speed of 30 km/h in city)
    const estimatedHours = distance / 1000 / 30;
    const estimatedMinutes = Math.round(estimatedHours * 60);
    
    if (estimatedMinutes < 60) {
        document.getElementById('eta-display').textContent = `~${estimatedMinutes} minutes`;
    } else {
        const hours = Math.floor(estimatedMinutes / 60);
        const minutes = estimatedMinutes % 60;
        document.getElementById('eta-display').textContent = `~${hours}h ${minutes}m`;
    }
}

// Update courier information
function updateCourierInfo() {
    const delivery = window.trackingData?.delivery;
    const courierInfoElement = document.getElementById('courier-info');
    
    if (!courierInfoElement || !delivery) return;
    
    const courierInfo = delivery.courier_info;
    
    if (courierInfo && courierInfo.name) {
        courierInfoElement.innerHTML = `
            <p class="text-gray-700"><strong>Name:</strong> ${courierInfo.name}</p>
            ${courierInfo.phone ? `<p class="text-gray-700"><strong>Phone:</strong> ${courierInfo.phone}</p>` : ''}
            ${courierInfo.vehicle_type ? `<p class="text-gray-700"><strong>Vehicle:</strong> ${courierInfo.vehicle_type}</p>` : ''}
            ${courierInfo.vehicle_number ? `<p class="text-gray-700"><strong>Vehicle Number:</strong> ${courierInfo.vehicle_number}</p>` : ''}
        `;
    } else {
        courierInfoElement.innerHTML = '<p class="text-gray-700">No courier assigned yet</p>';
    }
}

// Update GPS status
function updateGPSStatus() {
    const delivery = window.trackingData?.delivery;
    const gpsStatusElement = document.getElementById('gps-status');
    
    if (!gpsStatusElement || !delivery) return;
    
    const isGPSActive = delivery.is_gps_active;
    const gpsTrackingEnabled = delivery.gps_tracking_enabled;
    
    if (isGPSActive) {
        gpsStatusElement.innerHTML = `
            <div class="flex items-center">
                <div class="w-3 h-3 bg-green-500 rounded-full animate-pulse mr-2"></div>
                <span class="text-green-700 font-semibold">Live GPS Active</span>
            </div>
            <p class="text-sm text-gray-600 mt-1">Real-time location tracking is active</p>
        `;
    } else if (gpsTrackingEnabled) {
        gpsStatusElement.innerHTML = `
            <div class="flex items-center">
                <div class="w-3 h-3 bg-yellow-500 rounded-full mr-2"></div>
                <span class="text-yellow-700 font-semibold">GPS Enabled</span>
            </div>
            <p class="text-sm text-gray-600 mt-1">GPS tracking is enabled but not currently active</p>
        `;
    } else {
        gpsStatusElement.innerHTML = `
            <div class="flex items-center">
                <div class="w-3 h-3 bg-red-500 rounded-full mr-2"></div>
                <span class="text-red-700 font-semibold">GPS Disabled</span>
            </div>
            <p class="text-sm text-gray-600 mt-1">GPS tracking is not enabled for this delivery</p>
        `;
    }
}

// Update connection status
function updateConnectionStatus(isConnected) {
    const indicator = document.getElementById('live-indicator');
    const statusText = document.getElementById('live-status-text');
    const connectionStatus = document.getElementById('connection-status');
    
    if (isConnected) {
        indicator.className = 'w-3 h-3 bg-green-500 rounded-full animate-pulse';
        statusText.textContent = 'Live Tracking Active';
        connectionStatus.textContent = 'WebSocket: Connected';
    } else {
        indicator.className = 'w-3 h-3 bg-red-500 rounded-full animate-pulse';
        statusText.textContent = 'Connecting...';
        connectionStatus.textContent = 'WebSocket: Disconnected';
    }
}
