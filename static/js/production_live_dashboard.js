/**
 * Production Live Dashboard JavaScript
 * Enhanced real-time dashboard that works like CoinMarketCap
 * with live price updates, movement counting, and beautiful animations
 */

class ProductionLiveDashboard {
    constructor() {
        this.websocket = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 10;
        this.reconnectDelay = 3000;
        
        // Price tracking
        this.priceData = {};
        this.previousPrices = {};
        this.movementStats = {
            increases: 0,
            decreases: 0,
            unchanged: 0,
            total: 0
        };
        
        // Update counters
        this.updateCount = 0;
        this.lastUpdateTime = null;
        
        // Charts
        this.charts = {};
        
        this.init();
    }
    
    init() {
        console.log('🚀 Initializing Production Live Dashboard...');
        this.initializeCharts();
        this.setupEventListeners();
        this.connectWebSocket();
        this.startPeriodicUpdates();
        this.loadInitialData();
    }
    
    initializeCharts() {
        // Enhanced Performance Chart
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
                        pointRadius: 4,
                        pointHoverRadius: 6
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
                            borderWidth: 1,
                            cornerRadius: 8
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: false,
                            grid: { 
                                color: 'rgba(156, 163, 175, 0.1)',
                                drawBorder: false
                            },
                            ticks: {
                                callback: function(value) {
                                    return '$' + value.toLocaleString();
                                },
                                color: '#9ca3af'
                            }
                        },
                        x: {
                            grid: { 
                                color: 'rgba(156, 163, 175, 0.1)',
                                drawBorder: false
                            },
                            ticks: {
                                color: '#9ca3af'
                            }
                        }
                    },
                    interaction: {
                        mode: 'nearest',
                        axis: 'x',
                        intersect: false
                    },
                    animation: {
                        duration: 1000,
                        easing: 'easeInOutQuart'
                    }
                }
            });
        }
        
        // Enhanced Distribution Chart - Beautiful and Eye-catching
        const distributionCtx = document.getElementById('distributionChart');
        if (distributionCtx) {
            this.charts.distribution = new Chart(distributionCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Cryptocurrencies', 'Precious Metals', 'Real Estate', 'Stocks & ETFs', 'Commodities'],
                    datasets: [{
                        data: [45, 20, 15, 12, 8],
                        backgroundColor: [
                            'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                            'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
                            'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
                            'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
                            'linear-gradient(135deg, #fa709a 0%, #fee140 100%)'
                        ],
                        borderColor: '#ffffff',
                        borderWidth: 4,
                        hoverOffset: 15,
                        hoverBorderWidth: 6,
                        shadowOffsetX: 0,
                        shadowOffsetY: 4,
                        shadowBlur: 8,
                        shadowColor: 'rgba(0, 0, 0, 0.1)'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                padding: 25,
                                usePointStyle: true,
                                pointStyle: 'circle',
                                font: {
                                    size: 13,
                                    weight: '600',
                                    family: "'Inter', sans-serif"
                                },
                                color: '#374151',
                                generateLabels: function(chart) {
                                    const data = chart.data;
                                    if (data.labels.length && data.datasets.length) {
                                        return data.labels.map((label, i) => {
                                            const dataset = data.datasets[0];
                                            const value = dataset.data[i];
                                            const total = dataset.data.reduce((a, b) => a + b, 0);
                                            const percentage = ((value / total) * 100).toFixed(1);
                                            
                                            return {
                                                text: `${label} (${percentage}%)`,
                                                fillStyle: dataset.backgroundColor[i],
                                                strokeStyle: dataset.borderColor,
                                                lineWidth: dataset.borderWidth,
                                                pointStyle: 'circle',
                                                hidden: false,
                                                index: i
                                            };
                                        });
                                    }
                                    return [];
                                }
                            }
                        },
                        tooltip: {
                            backgroundColor: 'rgba(0, 0, 0, 0.9)',
                            titleColor: '#ffffff',
                            bodyColor: '#ffffff',
                            borderColor: '#3b82f6',
                            borderWidth: 2,
                            cornerRadius: 12,
                            titleFont: {
                                size: 14,
                                weight: 'bold'
                            },
                            bodyFont: {
                                size: 13
                            },
                            padding: 12,
                            callbacks: {
                                title: function(context) {
                                    return context[0].label;
                                },
                                label: function(context) {
                                    const value = context.parsed;
                                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                    const percentage = ((value / total) * 100).toFixed(1);
                                    return `Value: $${value.toLocaleString()} (${percentage}%)`;
                                },
                                afterLabel: function(context) {
                                    return 'Click to view details';
                                }
                            }
                        }
                    },
                    cutout: '70%',
                    radius: '85%',
                    animation: {
                        animateRotate: true,
                        animateScale: true,
                        duration: 1500,
                        easing: 'easeInOutQuart',
                        delay: (context) => {
                            return context.dataIndex * 200;
                        }
                    },
                    interaction: {
                        intersect: false,
                        mode: 'index'
                    },
                    onHover: (event, activeElements) => {
                        event.native.target.style.cursor = activeElements.length > 0 ? 'pointer' : 'default';
                    }
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
                    this.startPeriodicUpdates();
                } else {
                    this.stopPeriodicUpdates();
                }
            });
        }
        
        // Manual refresh button
        const refreshButton = document.getElementById('refreshButton');
        if (refreshButton) {
            refreshButton.addEventListener('click', () => {
                this.fetchLivePrices();
            });
        }
    }
    
    connectWebSocket() {
        try {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const host = window.location.host;
            const wsUrl = `${protocol}//${host}/ws/price-feeds/`;
            
            console.log('🔌 Connecting to WebSocket:', wsUrl);
            
            this.websocket = new WebSocket(wsUrl);
            
            this.websocket.onopen = (event) => {
                console.log('✅ WebSocket connected');
                this.isConnected = true;
                this.reconnectAttempts = 0;
                this.updateConnectionStatus(true);
                
                // Request initial price data
                this.websocket.send(JSON.stringify({
                    type: 'get_prices'
                }));
            };
            
            this.websocket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleWebSocketMessage(data);
                } catch (error) {
                    console.error('❌ Error parsing WebSocket message:', error);
                }
            };
            
            this.websocket.onclose = (event) => {
                console.log('🔌 WebSocket disconnected');
                this.isConnected = false;
                this.updateConnectionStatus(false);
                this.attemptReconnect();
            };
            
            this.websocket.onerror = (error) => {
                console.error('❌ WebSocket error:', error);
                this.isConnected = false;
                this.updateConnectionStatus(false);
            };
            
        } catch (error) {
            console.error('❌ Error connecting to WebSocket:', error);
            this.isConnected = false;
            this.updateConnectionStatus(false);
        }
    }
    
    handleWebSocketMessage(data) {
        console.log('📨 Received WebSocket message:', data);
        
        switch (data.type) {
            case 'price_data':
                this.updateLivePriceFeed(data.prices || []);
                this.updatePriceCounters(data.prices || []);
                break;
                
            case 'price_update':
                this.updateLivePriceFeed(data.price_data || []);
                this.updatePriceCounters(data.price_data || []);
                
                // Update movement statistics if provided
                if (data.movement_stats) {
                    this.updateMovementStatistics(data.movement_stats);
                }
                
                // Update update count
                if (data.update_count) {
                    this.updateCount = data.update_count;
                    this.updateUpdateCounter();
                }
                
                this.lastUpdateTime = new Date();
                this.updateLastUpdateTime();
                break;
                
            case 'portfolio_update':
                this.updatePortfolioData(data.portfolio_data);
                break;
                
            case 'error':
                console.error('❌ WebSocket error message:', data.message);
                break;
                
            default:
                console.log('❓ Unknown WebSocket message type:', data.type);
        }
    }
    
    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`🔄 Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
            
            setTimeout(() => {
                this.connectWebSocket();
            }, this.reconnectDelay);
        } else {
            console.error('❌ Max reconnection attempts reached');
        }
    }
    
    updateConnectionStatus(connected) {
        const statusElements = document.querySelectorAll('.connection-status, .price-connection-status');
        statusElements.forEach(element => {
            if (connected) {
                element.innerHTML = '<div class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div><span class="text-sm text-green-600 dark:text-green-400 ml-1">Live</span>';
                element.className = element.className.replace('text-red-500', 'text-green-500');
            } else {
                element.innerHTML = '<div class="w-2 h-2 bg-red-500 rounded-full"></div><span class="text-sm text-red-600 dark:text-red-400 ml-1">Disconnected</span>';
                element.className = element.className.replace('text-green-500', 'text-red-500');
            }
        });
    }
    
    updateLivePriceFeed(prices) {
        const container = document.getElementById('livePriceFeed');
        if (!container) return;
        
        // Store previous prices for comparison
        this.previousPrices = { ...this.priceData };
        this.priceData = {};
        
        if (prices.length === 0) {
            container.innerHTML = '<div class="text-center text-gray-500 dark:text-gray-400 py-4">No live prices available</div>';
            return;
        }
        
        container.innerHTML = '';
        
        prices.slice(0, 12).forEach(price => {
            this.priceData[price.symbol] = price;
            
            const priceElement = document.createElement('div');
            priceElement.className = 'flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg mb-3 transition-all duration-300 hover:bg-gray-100 dark:hover:bg-gray-600 hover:shadow-lg';
            
            const changeClass = price.price_change_percentage_24h >= 0 ? 'text-green-600' : 'text-red-600';
            const changeIcon = price.price_change_percentage_24h >= 0 ? '▲' : '▼';
            
            // Check for price change animation
            const previousPrice = this.previousPrices[price.symbol];
            let animationClass = '';
            if (previousPrice && previousPrice.current_price !== price.current_price) {
                animationClass = price.current_price > previousPrice.current_price ? 'animate-pulse bg-green-50 dark:bg-green-900' : 'animate-pulse bg-red-50 dark:bg-red-900';
            }
            
            priceElement.className += ` ${animationClass}`;
            
            priceElement.innerHTML = `
                <div class="flex items-center space-x-4">
                    <div class="w-10 h-10 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center shadow-md">
                        <span class="text-sm font-bold text-blue-600 dark:text-blue-400">${price.symbol || '?'}</span>
                    </div>
                    <div>
                        <div class="font-semibold text-gray-900 dark:text-white">${price.name}</div>
                        <div class="text-sm text-gray-500 dark:text-gray-400">${price.symbol || ''}</div>
                    </div>
                </div>
                <div class="text-right">
                    <div class="font-bold text-lg text-gray-900 dark:text-white">$${parseFloat(price.current_price).toFixed(2)}</div>
                    <div class="text-sm ${changeClass} font-medium">
                        ${changeIcon} ${Math.abs(price.price_change_percentage_24h).toFixed(2)}%
                    </div>
                </div>
            `;
            
            container.appendChild(priceElement);
        });
    }
    
    updatePriceCounters(prices) {
        // Count price movements
        let increases = 0;
        let decreases = 0;
        let unchanged = 0;
        
        prices.forEach(price => {
            if (price.price_change_percentage_24h > 0) {
                increases++;
            } else if (price.price_change_percentage_24h < 0) {
                decreases++;
            } else {
                unchanged++;
            }
        });
        
        // Update counters with animation
        this.animateCounter(document.getElementById('totalIncreases'), increases);
        this.animateCounter(document.getElementById('totalDecreases'), decreases);
        this.animateCounter(document.getElementById('totalMovements'), increases + decreases);
        
        // Update movement stats
        this.movementStats = { increases, decreases, unchanged, total: increases + decreases };
    }
    
    updateMovementStatistics(stats) {
        // Update global movement statistics
        this.movementStats = {
            increases: (this.movementStats.increases || 0) + (stats.increases || 0),
            decreases: (this.movementStats.decreases || 0) + (stats.decreases || 0),
            unchanged: (this.movementStats.unchanged || 0) + (stats.unchanged || 0),
            total: (this.movementStats.total || 0) + (stats.total || 0)
        };
        
        // Update display
        this.animateCounter(document.getElementById('totalIncreases'), this.movementStats.increases);
        this.animateCounter(document.getElementById('totalDecreases'), this.movementStats.decreases);
        this.animateCounter(document.getElementById('totalMovements'), this.movementStats.total);
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
    
    updateUpdateCounter() {
        const updateCountElement = document.getElementById('updateCount');
        if (updateCountElement) {
            this.animateCounter(updateCountElement, this.updateCount);
        }
    }
    
    updateLastUpdateTime() {
        const lastUpdateElement = document.getElementById('lastUpdateTime');
        if (lastUpdateElement && this.lastUpdateTime) {
            lastUpdateElement.textContent = this.lastUpdateTime.toLocaleTimeString();
        }
    }
    
    startPeriodicUpdates() {
        this.stopPeriodicUpdates();
        this.periodicInterval = setInterval(() => {
            this.fetchLivePrices();
            this.fetchPriceStatistics();
        }, 30000); // 30 seconds
    }
    
    stopPeriodicUpdates() {
        if (this.periodicInterval) {
            clearInterval(this.periodicInterval);
            this.periodicInterval = null;
        }
    }
    
    loadInitialData() {
        this.fetchPortfolioData();
        this.fetchPriceStatistics();
        this.fetchLivePrices();
    }
    
    async fetchPortfolioData() {
        try {
            const response = await fetch('/investments/api/investments/portfolio_summary/');
            const data = await response.json();
            this.updatePortfolioData(data);
        } catch (error) {
            console.error('❌ Error fetching portfolio data:', error);
        }
    }
    
    async fetchPriceStatistics() {
        try {
            const response = await fetch('/investments/api/price-statistics/');
            const data = await response.json();
            this.updatePriceStatistics(data);
        } catch (error) {
            console.error('❌ Error fetching price statistics:', error);
        }
    }
    
    async fetchLivePrices() {
        try {
            const response = await fetch('/investments/api/live-prices/');
            const data = await response.json();
            this.updateLivePriceFeed(data.prices || []);
            this.updatePriceCounters(data.prices || []);
        } catch (error) {
            console.error('❌ Error fetching live prices:', error);
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
    
    updatePortfolioData(portfolioData) {
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
    
    destroy() {
        this.stopPeriodicUpdates();
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
    console.log('🚀 Initializing Production Live Dashboard...');
    window.productionLiveDashboard = new ProductionLiveDashboard();
});

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    if (window.productionLiveDashboard) {
        window.productionLiveDashboard.destroy();
    }
});
