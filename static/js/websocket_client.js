/**
 * WebSocket Client for Real-time Price Updates
 * Handles WebSocket connections and price updates for the investment system
 */

class PriceWebSocketClient {
    constructor(options = {}) {
        this.options = {
            reconnectInterval: 5000,
            maxReconnectAttempts: 10,
            debug: false,
            ...options
        };
        
        this.ws = null;
        this.reconnectAttempts = 0;
        this.isConnecting = false;
        this.callbacks = {
            onConnect: [],
            onDisconnect: [],
            onPriceUpdate: [],
            onError: []
        };
        
        this.priceData = {};
        this.lastUpdate = null;
    }
    
    /**
     * Connect to WebSocket server
     */
    connect() {
        if (this.isConnecting || this.ws?.readyState === WebSocket.OPEN) {
            return;
        }
        
        this.isConnecting = true;
        
        try {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws/price-feeds/`;
            
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = () => {
                this.isConnecting = false;
                this.reconnectAttempts = 0;
                this.log('WebSocket connected');
                this.triggerCallbacks('onConnect');
                
                // Request initial price data
                this.sendMessage({
                    type: 'get_prices'
                });
            };
            
            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleMessage(data);
                } catch (error) {
                    this.log('Error parsing WebSocket message:', error);
                }
            };
            
            this.ws.onclose = (event) => {
                this.isConnecting = false;
                this.log('WebSocket disconnected:', event.code, event.reason);
                this.triggerCallbacks('onDisconnect', event);
                
                // Attempt to reconnect
                if (this.reconnectAttempts < this.options.maxReconnectAttempts) {
                    this.reconnectAttempts++;
                    this.log(`Reconnecting in ${this.options.reconnectInterval}ms (attempt ${this.reconnectAttempts})`);
                    setTimeout(() => this.connect(), this.options.reconnectInterval);
                } else {
                    this.log('Max reconnection attempts reached');
                }
            };
            
            this.ws.onerror = (error) => {
                this.isConnecting = false;
                this.log('WebSocket error:', error);
                this.triggerCallbacks('onError', error);
            };
            
        } catch (error) {
            this.isConnecting = false;
            this.log('Error creating WebSocket connection:', error);
            this.triggerCallbacks('onError', error);
        }
    }
    
    /**
     * Handle incoming WebSocket messages
     */
    handleMessage(data) {
        switch (data.type) {
            case 'price_data':
            case 'price_update':
                this.updatePriceData(data.prices);
                break;
            case 'subscription_confirmed':
                this.log('Subscription confirmed for:', data.asset_type);
                break;
            default:
                this.log('Unknown message type:', data.type);
        }
    }
    
    /**
     * Update price data and trigger callbacks
     */
    updatePriceData(prices) {
        const previousData = { ...this.priceData };
        this.priceData = {};
        
        prices.forEach(price => {
            this.priceData[price.symbol] = price;
            
            // Check if price changed
            const previousPrice = previousData[price.symbol];
            if (previousPrice && previousPrice.current_price !== price.current_price) {
                this.triggerCallbacks('onPriceUpdate', {
                    symbol: price.symbol,
                    name: price.name,
                    oldPrice: previousPrice.current_price,
                    newPrice: price.current_price,
                    change: price.current_price - previousPrice.current_price,
                    changePercent: price.price_change_percentage_24h,
                    data: price
                });
            }
        });
        
        this.lastUpdate = new Date();
    }
    
    /**
     * Send message to WebSocket server
     */
    sendMessage(message) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(message));
        } else {
            this.log('WebSocket not connected, cannot send message');
        }
    }
    
    /**
     * Subscribe to specific asset type
     */
    subscribeToAsset(assetType) {
        this.sendMessage({
            type: 'subscribe_asset',
            asset_type: assetType
        });
    }
    
    /**
     * Request current price data
     */
    requestPrices() {
        this.sendMessage({
            type: 'get_prices'
        });
    }
    
    /**
     * Get current price data
     */
    getPriceData(symbol = null) {
        if (symbol) {
            return this.priceData[symbol] || null;
        }
        return this.priceData;
    }
    
    /**
     * Get last update time
     */
    getLastUpdate() {
        return this.lastUpdate;
    }
    
    /**
     * Check if connected
     */
    isConnected() {
        return this.ws && this.ws.readyState === WebSocket.OPEN;
    }
    
    /**
     * Disconnect WebSocket
     */
    disconnect() {
        if (this.ws) {
            this.ws.close();
        }
    }
    
    /**
     * Add event callback
     */
    on(event, callback) {
        if (this.callbacks[event]) {
            this.callbacks[event].push(callback);
        }
    }
    
    /**
     * Remove event callback
     */
    off(event, callback) {
        if (this.callbacks[event]) {
            const index = this.callbacks[event].indexOf(callback);
            if (index > -1) {
                this.callbacks[event].splice(index, 1);
            }
        }
    }
    
    /**
     * Trigger callbacks for an event
     */
    triggerCallbacks(event, data) {
        if (this.callbacks[event]) {
            this.callbacks[event].forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    this.log('Error in callback:', error);
                }
            });
        }
    }
    
    /**
     * Log message if debug is enabled
     */
    log(...args) {
        if (this.options.debug) {
            console.log('[PriceWebSocket]', ...args);
        }
    }
}

/**
 * Price Update Manager
 * Manages price updates across the application
 */
class PriceUpdateManager {
    constructor() {
        this.client = new PriceWebSocketClient({
            debug: true,
            reconnectInterval: 3000,
            maxReconnectAttempts: 20
        });
        
        this.updateCallbacks = new Map();
        this.elements = new Map();
        this.autoRefresh = true;
        this.refreshInterval = null;
        
        this.init();
    }
    
    init() {
        // Set up event handlers
        this.client.on('onConnect', () => {
            this.updateConnectionStatus(true);
            this.startAutoRefresh();
        });
        
        this.client.on('onDisconnect', () => {
            this.updateConnectionStatus(false);
            this.stopAutoRefresh();
        });
        
        this.client.on('onPriceUpdate', (update) => {
            this.handlePriceUpdate(update);
        });
        
        this.client.on('onError', (error) => {
            console.error('Price WebSocket error:', error);
        });
        
        // Connect to WebSocket
        this.client.connect();
        
        // Set up auto-refresh toggle
        this.setupAutoRefreshToggle();
    }
    
    /**
     * Register an element for price updates
     */
    registerElement(elementId, symbol, options = {}) {
        const element = document.getElementById(elementId);
        if (!element) {
            console.warn(`Element with ID '${elementId}' not found`);
            return;
        }
        
        const config = {
            showChange: true,
            showPercentage: true,
            format: 'currency',
            animate: true,
            ...options
        };
        
        this.elements.set(elementId, {
            element,
            symbol,
            config
        });
        
        // Update immediately if we have data
        const priceData = this.client.getPriceData(symbol);
        if (priceData) {
            this.updateElement(elementId, priceData);
        }
    }
    
    /**
     * Update a specific element
     */
    updateElement(elementId, priceData) {
        const elementInfo = this.elements.get(elementId);
        if (!elementInfo) return;
        
        const { element, config } = elementInfo;
        const price = priceData.current_price;
        const change = priceData.price_change_24h;
        const changePercent = priceData.price_change_percentage_24h;
        
        let content = '';
        
        // Format price
        if (config.format === 'currency') {
            content = `$${price.toFixed(2)}`;
        } else {
            content = price.toString();
        }
        
        // Add change information
        if (config.showChange && change !== 0) {
            const changeText = change >= 0 ? `+$${change.toFixed(2)}` : `-$${Math.abs(change).toFixed(2)}`;
            const changeClass = change >= 0 ? 'text-green-600' : 'text-red-600';
            content += ` <span class="${changeClass} text-sm">(${changeText})</span>`;
        }
        
        if (config.showPercentage && changePercent !== 0) {
            const percentText = changePercent >= 0 ? `+${changePercent.toFixed(2)}%` : `${changePercent.toFixed(2)}%`;
            const percentClass = changePercent >= 0 ? 'text-green-600' : 'text-red-600';
            content += ` <span class="${percentClass} text-sm">${percentText}</span>`;
        }
        
        // Animate if enabled
        if (config.animate) {
            element.style.transition = 'color 0.3s ease';
            element.style.color = change >= 0 ? '#10b981' : '#ef4444';
            setTimeout(() => {
                element.style.color = '';
            }, 1000);
        }
        
        element.innerHTML = content;
    }
    
    /**
     * Handle price update
     */
    handlePriceUpdate(update) {
        // Update registered elements
        this.elements.forEach((elementInfo, elementId) => {
            if (elementInfo.symbol === update.symbol) {
                this.updateElement(elementId, update.data);
            }
        });
        
        // Trigger custom callbacks
        if (this.updateCallbacks.has(update.symbol)) {
            this.updateCallbacks.get(update.symbol).forEach(callback => {
                try {
                    callback(update);
                } catch (error) {
                    console.error('Error in price update callback:', error);
                }
            });
        }
    }
    
    /**
     * Add custom callback for price updates
     */
    onPriceUpdate(symbol, callback) {
        if (!this.updateCallbacks.has(symbol)) {
            this.updateCallbacks.set(symbol, []);
        }
        this.updateCallbacks.get(symbol).push(callback);
    }
    
    /**
     * Update connection status display
     */
    updateConnectionStatus(connected) {
        const statusElements = document.querySelectorAll('.price-connection-status');
        statusElements.forEach(element => {
            if (connected) {
                element.classList.remove('text-red-500');
                element.classList.add('text-green-500');
                element.innerHTML = '<i class="fas fa-circle text-xs"></i> Live';
            } else {
                element.classList.remove('text-green-500');
                element.classList.add('text-red-500');
                element.innerHTML = '<i class="fas fa-circle text-xs"></i> Disconnected';
            }
        });
    }
    
    /**
     * Start auto-refresh
     */
    startAutoRefresh() {
        if (this.autoRefresh && !this.refreshInterval) {
            this.refreshInterval = setInterval(() => {
                this.client.requestPrices();
            }, 30000); // Refresh every 30 seconds
        }
    }
    
    /**
     * Stop auto-refresh
     */
    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }
    
    /**
     * Set up auto-refresh toggle
     */
    setupAutoRefreshToggle() {
        const toggle = document.getElementById('auto-refresh-toggle');
        if (toggle) {
            toggle.addEventListener('change', (e) => {
                this.autoRefresh = e.target.checked;
                if (this.autoRefresh) {
                    this.startAutoRefresh();
                } else {
                    this.stopAutoRefresh();
                }
            });
        }
    }
    
    /**
     * Get client instance
     */
    getClient() {
        return this.client;
    }
}

// Global instance
window.priceManager = new PriceUpdateManager();

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { PriceWebSocketClient, PriceUpdateManager };
}
