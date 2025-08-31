/**
 * WebSocket Client for Real-time Investment Updates
 * Handles connections to Django Channels WebSocket consumers
 */

class InvestmentWebSocket {
    constructor(userId = null) {
        this.userId = userId;
        this.connections = {};
        this.reconnectAttempts = {};
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
    }
    
    /**
     * Connect to price feeds WebSocket
     */
    connectToPriceFeeds() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/price-feeds/`;
        
        try {
            const ws = new WebSocket(wsUrl);
            
            ws.onopen = () => {
                console.log('Connected to price feeds WebSocket');
                this.connections.priceFeeds = ws;
                
                // Request initial price data
                ws.send(JSON.stringify({ type: 'get_prices' }));
            };
            
            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handlePriceFeedMessage(data);
            };
            
            ws.onclose = () => {
                console.log('Price feeds WebSocket disconnected');
                this.connections.priceFeeds = null;
                this.scheduleReconnect('priceFeeds');
            };
            
            ws.onerror = (error) => {
                console.error('Price feeds WebSocket error:', error);
            };
            
        } catch (error) {
            console.error('Failed to connect to price feeds WebSocket:', error);
        }
    }
    
    /**
     * Connect to user's investment WebSocket
     */
    connectToInvestments() {
        if (!this.userId) {
            console.warn('User ID required for investment WebSocket');
            return;
        }
        
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/investments/${this.userId}/`;
        
        try {
            const ws = new WebSocket(wsUrl);
            
            ws.onopen = () => {
                console.log('Connected to investments WebSocket');
                this.connections.investments = ws;
                
                // Request initial investment data
                ws.send(JSON.stringify({ type: 'get_investments' }));
            };
            
            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleInvestmentMessage(data);
            };
            
            ws.onclose = () => {
                console.log('Investments WebSocket disconnected');
                this.connections.investments = null;
                this.scheduleReconnect('investments');
            };
            
            ws.onerror = (error) => {
                console.error('Investments WebSocket error:', error);
            };
            
        } catch (error) {
            console.error('Failed to connect to investments WebSocket:', error);
        }
    }
    
    /**
     * Connect to user's portfolio WebSocket
     */
    connectToPortfolio() {
        if (!this.userId) {
            console.warn('User ID required for portfolio WebSocket');
            return;
        }
        
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/portfolio/${this.userId}/`;
        
        try {
            const ws = new WebSocket(wsUrl);
            
            ws.onopen = () => {
                console.log('Connected to portfolio WebSocket');
                this.connections.portfolio = ws;
                
                // Request initial portfolio data
                ws.send(JSON.stringify({ type: 'get_portfolio' }));
            };
            
            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handlePortfolioMessage(data);
            };
            
            ws.onclose = () => {
                console.log('Portfolio WebSocket disconnected');
                this.connections.portfolio = null;
                this.scheduleReconnect('portfolio');
            };
            
            ws.onerror = (error) => {
                console.error('Portfolio WebSocket error:', error);
            };
            
        } catch (error) {
            console.error('Failed to connect to portfolio WebSocket:', error);
        }
    }
    
    /**
     * Handle price feed messages
     */
    handlePriceFeedMessage(data) {
        switch (data.type) {
            case 'price_data':
                this.updatePriceDisplay(data.prices);
                break;
            case 'price_update':
                this.updatePriceDisplay([data.price_data]);
                this.showPriceUpdateNotification(data.price_data);
                break;
            case 'subscription_confirmed':
                console.log(`Subscribed to ${data.asset_type} updates`);
                break;
            default:
                console.log('Unknown price feed message type:', data.type);
        }
    }
    
    /**
     * Handle investment messages
     */
    handleInvestmentMessage(data) {
        switch (data.type) {
            case 'investment_data':
                this.updateInvestmentDisplay(data.investments);
                break;
            case 'portfolio_data':
                this.updatePortfolioDisplay(data.portfolio);
                break;
            default:
                console.log('Unknown investment message type:', data.type);
        }
    }
    
    /**
     * Handle portfolio messages
     */
    handlePortfolioMessage(data) {
        switch (data.type) {
            case 'portfolio_data':
                this.updatePortfolioDisplay(data.portfolio);
                break;
            case 'investments_data':
                this.updateInvestmentDisplay(data.investments);
                break;
            default:
                console.log('Unknown portfolio message type:', data.type);
        }
    }
    
    /**
     * Update price display on the page
     */
    updatePriceDisplay(prices) {
        prices.forEach(price => {
            const priceElement = document.querySelector(`[data-price-id="${price.id}"]`);
            if (priceElement) {
                // Update current price
                const currentPriceEl = priceElement.querySelector('.current-price');
                if (currentPriceEl) {
                    currentPriceEl.textContent = `$${parseFloat(price.current_price).toLocaleString()}`;
                }
                
                // Update price change
                const changeEl = priceElement.querySelector('.price-change');
                if (changeEl) {
                    const changeValue = parseFloat(price.price_change_percentage_24h);
                    const changeText = `${changeValue >= 0 ? '+' : ''}${changeValue.toFixed(2)}%`;
                    changeEl.textContent = changeText;
                    changeEl.className = `price-change ${changeValue >= 0 ? 'positive' : 'negative'}`;
                }
                
                // Update last updated time
                const timeEl = priceElement.querySelector('.last-updated');
                if (timeEl) {
                    timeEl.textContent = 'Just now';
                }
            }
        });
    }
    
    /**
     * Update investment display on the page
     */
    updateInvestmentDisplay(investments) {
        // This would update investment cards/lists on the page
        console.log('Investment data updated:', investments);
        
        // Trigger custom event for other components to listen to
        window.dispatchEvent(new CustomEvent('investmentsUpdated', {
            detail: { investments }
        }));
    }
    
    /**
     * Update portfolio display on the page
     */
    updatePortfolioDisplay(portfolio) {
        // This would update portfolio summary on the page
        console.log('Portfolio data updated:', portfolio);
        
        // Trigger custom event for other components to listen to
        window.dispatchEvent(new CustomEvent('portfolioUpdated', {
            detail: { portfolio }
        }));
    }
    
    /**
     * Show price update notification
     */
    showPriceUpdateNotification(priceData) {
        // Create toast notification for price updates
        const notification = document.createElement('div');
        notification.className = 'price-update-notification';
        notification.innerHTML = `
            <div class="notification-content">
                <strong>${priceData.name}</strong> updated to $${parseFloat(priceData.current_price).toLocaleString()}
                <span class="change ${parseFloat(priceData.price_change_percentage_24h) >= 0 ? 'positive' : 'negative'}">
                    ${parseFloat(priceData.price_change_percentage_24h) >= 0 ? '+' : ''}${parseFloat(priceData.price_change_percentage_24h).toFixed(2)}%
                </span>
            </div>
        `;
        
        // Add to page
        document.body.appendChild(notification);
        
        // Remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
    }
    
    /**
     * Schedule reconnection attempt
     */
    scheduleReconnect(connectionType) {
        if (!this.reconnectAttempts[connectionType]) {
            this.reconnectAttempts[connectionType] = 0;
        }
        
        if (this.reconnectAttempts[connectionType] < this.maxReconnectAttempts) {
            this.reconnectAttempts[connectionType]++;
            
            setTimeout(() => {
                console.log(`Attempting to reconnect to ${connectionType}...`);
                if (connectionType === 'priceFeeds') {
                    this.connectToPriceFeeds();
                } else if (connectionType === 'investments') {
                    this.connectToInvestments();
                } else if (connectionType === 'portfolio') {
                    this.connectToPortfolio();
                }
            }, this.reconnectDelay * this.reconnectAttempts[connectionType]);
        } else {
            console.error(`Max reconnection attempts reached for ${connectionType}`);
        }
    }
    
    /**
     * Disconnect all WebSocket connections
     */
    disconnect() {
        Object.keys(this.connections).forEach(key => {
            if (this.connections[key]) {
                this.connections[key].close();
                this.connections[key] = null;
            }
        });
        
        // Clear reconnection attempts
        this.reconnectAttempts = {};
    }
    
    /**
     * Subscribe to specific asset type updates
     */
    subscribeToAsset(assetType) {
        if (this.connections.priceFeeds) {
            this.connections.priceFeeds.send(JSON.stringify({
                type: 'subscribe_asset',
                asset_type: assetType
            }));
        }
    }
}

// Initialize WebSocket client when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Get user ID from page data if available
    const userId = document.body.dataset.userId || null;
    
    // Create WebSocket instance
    window.investmentWebSocket = new InvestmentWebSocket(userId);
    
    // Connect to price feeds (always available)
    window.investmentWebSocket.connectToPriceFeeds();
    
    // Connect to user-specific WebSockets if user is authenticated
    if (userId) {
        window.investmentWebSocket.connectToInvestments();
        window.investmentWebSocket.connectToPortfolio();
    }
    
    // Add CSS for notifications
    const style = document.createElement('style');
    style.textContent = `
        .price-update-notification {
            position: fixed;
            top: 20px;
            right: 20px;
            background: #fff;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 1000;
            max-width: 300px;
            animation: slideIn 0.3s ease-out;
        }
        
        .price-update-notification .change.positive {
            color: #10b981;
        }
        
        .price-update-notification .change.negative {
            color: #ef4444;
        }
        
        @keyframes slideIn {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        .price-change.positive {
            color: #10b981;
        }
        
        .price-change.negative {
            color: #ef4444;
        }
    `;
    document.head.appendChild(style);
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = InvestmentWebSocket;
}
