/**
 * Live Price Dashboard JavaScript
 * Handles real-time price updates, charts, and statistics
 */

class LivePriceDashboard {
    constructor() {
        this.charts = {};
        this.websocket = null;
        this.autoRefreshInterval = null;
        this.priceUpdateCount = 0;
        this.lastUpdateTime = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 5000; // 5 seconds
        
        this.init();
    }
    
    init() {
        this.initializeCharts();
        this.setupEventListeners();
        this.connectWebSocket();
        this.startAutoRefresh();
        this.loadInitialData();
    }
    
    initializeCharts() {
        // Performance Chart
        const performanceCtx = document.getElementById('performanceChart');
        if (performanceCtx) {
            this.charts.performance = new Chart(performanceCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Portfolio Value',
                        data: [],
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        tension: 0.4,
                        fill: true,
                        pointBackgroundColor: '#3b82f6',
                        pointBorderColor: '#ffffff',
                        pointBorderWidth: 2,
                        pointRadius: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            mode: 'index',
                            intersect: false,
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            titleColor: '#ffffff',
                            bodyColor: '#ffffff',
                            borderColor: '#3b82f6',
                            borderWidth: 1
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: false,
                            grid: { color: 'rgba(156, 163, 175, 0.1)' },
                            ticks: {
                                callback: function(value) {
                                    return '$' + value.toLocaleString();
                                }
                            }
                        },
                        x: {
                            grid: { color: 'rgba(156, 163, 175, 0.1)' }
                        }
                    },
                    interaction: {
                        mode: 'nearest',
                        axis: 'x',
                        intersect: false
                    }
                }
            });
        }
        
        // Distribution Chart
        const distributionCtx = document.getElementById('distributionChart');
        if (distributionCtx) {
            this.charts.distribution = new Chart(distributionCtx, {
                type: 'doughnut',
                data: {
                    labels: [],
                    datasets: [{
                        data: [],
                        backgroundColor: [
                            '#3b82f6', '#f59e0b', '#10b981', '#ef4444', '#8b5cf6', '#06b6d4'
                        ],
                        borderColor: '#ffffff',
                        borderWidth: 2,
                        hoverOffset: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                padding: 20,
                                usePointStyle: true
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const label = context.label || '';
                                    const value = context.parsed;
                                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                    const percentage = ((value / total) * 100).toFixed(1);
                                    return `${label}: $${value.toLocaleString()} (${percentage}%)`;
                                }
                            }
                        }
                    },
                    cutout: '60%'
                }
            });
        }
    }
    
    setupEventListeners() {
        // Auto-refresh toggle
        const autoRefreshToggle = document.getElementById('autoRefreshToggle');
        if (autoRefreshToggle) {
            autoRefreshToggle.addEventListener('change', (e) => {
                if (e.target.checked) {
                    this.startAutoRefresh();
                } else {
                    this.stopAutoRefresh();
                }
            });
        }
    }
    
    connectWebSocket() {
        try {
            // Determine WebSocket URL
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const host = window.location.host;
            const wsUrl = `${protocol}//${host}/ws/price-feeds/`;
            
            console.log('Connecting to WebSocket:', wsUrl);
            
            this.websocket = new WebSocket(wsUrl);
            
            this.websocket.onopen = (event) => {
                console.log('WebSocket connected');
                this.isConnected = true;
                this.reconnectAttempts = 0;
                this.updateConnectionStatus(true);
            };
            
            this.websocket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleWebSocketMessage(data);
                } catch (error) {
                    console.error('Error parsing WebSocket message:', error);
                }
            };
            
            this.websocket.onclose = (event) => {
                console.log('WebSocket disconnected');
                this.isConnected = false;
                this.updateConnectionStatus(false);
                this.attemptReconnect();
            };
            
            this.websocket.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.isConnected = false;
                this.updateConnectionStatus(false);
            };
            
        } catch (error) {
            console.error('Error connecting to WebSocket:', error);
            this.isConnected = false;
            this.updateConnectionStatus(false);
        }
    }
    
    handleWebSocketMessage(data) {
        console.log('Received WebSocket message:', data);
        
        switch (data.type) {
            case 'price_update':
                this.updateLivePriceFeed(data.price_data || []);
                this.updatePriceCounters(data.price_data || []);
                this.priceUpdateCount++;
                this.lastUpdateTime = new Date();
                this.updateLastUpdateTime();
                break;
                
            case 'portfolio_update':
                this.updatePortfolioData(data.portfolio_data);
                break;
                
            case 'error':
                console.error('WebSocket error message:', data.message);
                break;
                
            default:
                console.log('Unknown WebSocket message type:', data.type);
        }
    }
    
    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
            
            setTimeout(() => {
                this.connectWebSocket();
            }, this.reconnectDelay);
        } else {
            console.error('Max reconnection attempts reached');
        }
    }
    
    updateConnectionStatus(connected) {
        const statusElement = document.querySelector('.connection-status');
        if (statusElement) {
            if (connected) {
                statusElement.innerHTML = '<div class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div><span class="text-sm text-green-600 dark:text-green-400">Live</span>';
            } else {
                statusElement.innerHTML = '<div class="w-2 h-2 bg-red-500 rounded-full"></div><span class="text-sm text-red-600 dark:text-red-400">Disconnected</span>';
            }
        }
    }
    
    startAutoRefresh() {
        this.stopAutoRefresh();
        this.autoRefreshInterval = setInterval(() => {
            this.fetchLivePrices();
            this.fetchPriceStatistics();
        }, 30000); // 30 seconds
    }
    
    stopAutoRefresh() {
        if (this.autoRefreshInterval) {
            clearInterval(this.autoRefreshInterval);
            this.autoRefreshInterval = null;
        }
    }
    
    loadInitialData() {
        this.fetchPortfolioData();
        this.fetchPriceStatistics();
        this.fetchLivePrices();
    }
    
    async fetchPortfolioData() {
        try {
            const response = await fetch('/investments/api/investments/performance_chart/');
            const data = await response.json();
            this.updateCharts(data);
        } catch (error) {
            console.error('Error fetching portfolio data:', error);
            this.createDefaultCharts();
        }
    }
    
    async fetchPriceStatistics() {
        try {
            const response = await fetch('/investments/api/price-statistics/');
            const data = await response.json();
            this.updatePriceStatistics(data);
        } catch (error) {
            console.error('Error fetching price statistics:', error);
        }
    }
    
    async fetchLivePrices() {
        try {
            const response = await fetch('/investments/api/live-prices/');
            const data = await response.json();
            this.updateLivePriceFeed(data.prices || []);
            this.updatePriceCounters(data.prices || []);
        } catch (error) {
            console.error('Error fetching live prices:', error);
        }
    }
    
    updateCharts(data) {
        // Update performance chart
        if (this.charts.performance) {
            this.charts.performance.data.labels = data.labels || [];
            this.charts.performance.data.datasets[0].data = data.values || [];
            this.charts.performance.update('none');
        }
        
        // Update distribution chart
        if (this.charts.distribution) {
            this.charts.distribution.data.labels = data.distribution_labels || [];
            this.charts.distribution.data.datasets[0].data = data.distribution_values || [];
            this.charts.distribution.update('none');
        }
    }
    
    updatePriceStatistics(data) {
        const elements = {
            totalIncreases: data.increases || 0,
            totalDecreases: data.decreases || 0,
            totalMovements: data.total || 0
        };
        
        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                this.animateCounter(element, value);
            }
        });
    }
    
    updateLivePriceFeed(prices) {
        const container = document.getElementById('livePriceFeed');
        if (!container) return;
        
        container.innerHTML = '';
        
        if (prices.length === 0) {
            container.innerHTML = '<div class="text-center text-gray-500 dark:text-gray-400 py-4">No live prices available</div>';
            return;
        }
        
        prices.slice(0, 10).forEach(price => {
            const priceElement = document.createElement('div');
            priceElement.className = 'flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg mb-2 transition-all duration-300 hover:bg-gray-100 dark:hover:bg-gray-600';
            
            const changeClass = price.price_change_percentage_24h >= 0 ? 'text-green-600' : 'text-red-600';
            const changeIcon = price.price_change_percentage_24h >= 0 ? '▲' : '▼';
            
            priceElement.innerHTML = `
                <div class="flex items-center space-x-3">
                    <div class="w-8 h-8 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center">
                        <span class="text-xs font-bold text-blue-600 dark:text-blue-400">${price.symbol || '?'}</span>
                    </div>
                    <div>
                        <div class="font-medium text-gray-900 dark:text-white">${price.name}</div>
                        <div class="text-sm text-gray-500 dark:text-gray-400">${price.symbol || ''}</div>
                    </div>
                </div>
                <div class="text-right">
                    <div class="font-bold text-gray-900 dark:text-white">$${parseFloat(price.current_price).toFixed(2)}</div>
                    <div class="text-sm ${changeClass}">
                        ${changeIcon} ${Math.abs(price.price_change_percentage_24h).toFixed(2)}%
                    </div>
                </div>
            `;
            
            container.appendChild(priceElement);
        });
        
        this.priceUpdateCount++;
        this.lastUpdateTime = new Date();
        this.updateLastUpdateTime();
    }
    
    updatePriceCounters(prices) {
        // Count price movements
        let increases = 0;
        let decreases = 0;
        
        prices.forEach(price => {
            if (price.price_change_percentage_24h > 0) {
                increases++;
            } else if (price.price_change_percentage_24h < 0) {
                decreases++;
            }
        });
        
        // Update counters with animation
        this.animateCounter(document.getElementById('totalIncreases'), increases);
        this.animateCounter(document.getElementById('totalDecreases'), decreases);
        this.animateCounter(document.getElementById('totalMovements'), increases + decreases);
    }
    
    animateCounter(element, targetValue) {
        if (!element) return;
        
        const currentValue = parseInt(element.textContent) || 0;
        const increment = (targetValue - currentValue) / 10;
        let current = currentValue;
        
        const timer = setInterval(() => {
            current += increment;
            if ((increment > 0 && current >= targetValue) || (increment < 0 && current <= targetValue)) {
                current = targetValue;
                clearInterval(timer);
            }
            element.textContent = Math.round(current);
        }, 50);
    }
    
    updateLastUpdateTime() {
        const lastUpdateElement = document.getElementById('lastUpdateTime');
        if (lastUpdateElement && this.lastUpdateTime) {
            lastUpdateElement.textContent = this.lastUpdateTime.toLocaleTimeString();
        }
    }
    
    updatePortfolioData(portfolioData) {
        // Update portfolio summary cards
        if (portfolioData) {
            const elements = {
                'total-invested': portfolioData.total_invested,
                'current-value': portfolioData.current_value,
                'total-return': portfolioData.total_return,
                'total-return-percentage': portfolioData.total_return_percentage
            };
            
            Object.entries(elements).forEach(([id, value]) => {
                const element = document.getElementById(id);
                if (element) {
                    if (id === 'total-return' || id === 'total-return-percentage') {
                        element.textContent = value >= 0 ? `+$${value}` : `-$${Math.abs(value)}`;
                        element.className = value >= 0 ? 'text-green-600' : 'text-red-600';
                    } else {
                        element.textContent = `$${value.toLocaleString()}`;
                    }
                }
            });
        }
    }
    
    createDefaultCharts() {
        // Create default charts with sample data
        if (this.charts.performance) {
            this.charts.performance.data.labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];
            this.charts.performance.data.datasets[0].data = [10000, 10500, 11000, 10800, 11500, 12000];
            this.charts.performance.update();
        }
        
        if (this.charts.distribution) {
            this.charts.distribution.data.labels = ['Crypto', 'Gold', 'Real Estate', 'Stocks'];
            this.charts.distribution.data.datasets[0].data = [40, 30, 20, 10];
            this.charts.distribution.update();
        }
    }
    
    destroy() {
        this.stopAutoRefresh();
        if (this.websocket) {
            this.websocket.close();
            this.websocket = null;
        }
        Object.values(this.charts).forEach(chart => {
            if (chart) chart.destroy();
        });
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.livePriceDashboard = new LivePriceDashboard();
});

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    if (window.livePriceDashboard) {
        window.livePriceDashboard.destroy();
    }
});
