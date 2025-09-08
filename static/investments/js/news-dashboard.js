/**
 * News Dashboard JavaScript
 */
class NewsDashboard {
    constructor() {
        this.currentPage = 1;
        this.pageSize = 20;
        this.currentFilters = {
            category: '',
            featured: '',
            search: ''
        };
        this.isLoading = false;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.loadFeaturedNews();
        this.loadMainNews();
        this.loadUserPreferences();
    }
    
    setupEventListeners() {
        // Filter controls
        document.getElementById('category-filter').addEventListener('change', (e) => {
            this.currentFilters.category = e.target.value;
            this.resetAndLoadNews();
        });
        
        document.getElementById('featured-filter').addEventListener('change', (e) => {
            this.currentFilters.featured = e.target.value;
            this.resetAndLoadNews();
        });
        
        document.getElementById('search-filter').addEventListener('input', 
            this.debounce((e) => {
                this.currentFilters.search = e.target.value;
                this.resetAndLoadNews();
            }, 500)
        );
        
        // Refresh button
        document.getElementById('refresh-news').addEventListener('click', () => {
            this.refreshAllNews();
        });
        
        // Load more button
        document.getElementById('load-more-news').addEventListener('click', () => {
            this.loadMoreNews();
        });
        
        // News settings button
        document.getElementById('saveNewsPreferences').addEventListener('click', () => {
            this.saveNewsPreferences();
        });
    }
    
    async loadFeaturedNews() {
        try {
            const response = await fetch('/investments/api/news/?featured=true&limit=6');
            const data = await response.json();
            
            if (data.status === 'success') {
                this.renderFeaturedNews(data.articles);
            }
        } catch (error) {
            console.error('Error loading featured news:', error);
        }
    }
    
    renderFeaturedNews(articles) {
        const container = document.getElementById('featured-news');
        if (!container) return;
        
        container.innerHTML = '';
        
        articles.forEach(article => {
            const articleElement = this.createFeaturedArticleElement(article);
            container.appendChild(articleElement);
        });
    }
    
    createFeaturedArticleElement(article) {
        const div = document.createElement('div');
        div.className = 'featured-news-item';
        div.innerHTML = `
            <div class="featured-news-image">
                <img src="${article.image_url || '/static/images/news-placeholder.jpg'}" 
                     alt="${article.title}" 
                     onerror="this.src='/static/images/news-placeholder.jpg'">
                <div class="featured-badge">
                    <i class="fas fa-star"></i> Featured
                </div>
            </div>
            <div class="featured-news-content">
                <div class="featured-news-meta">
                    <span class="news-source">${article.source_name}</span>
                    <span class="news-time">${article.time_ago}</span>
                </div>
                <h3 class="featured-news-title">
                    <a href="${article.url}" target="_blank" onclick="newsDashboard.trackClick('${article.id}')">
                        ${article.title}
                    </a>
                </h3>
                <p class="featured-news-summary">${article.summary}</p>
                <div class="featured-news-actions">
                    <a href="${article.url}" target="_blank" class="btn btn-sm btn-primary">
                        Read More <i class="fas fa-external-link-alt"></i>
                    </a>
                </div>
            </div>
        `;
        
        return div;
    }
    
    async loadMainNews(reset = false) {
        if (this.isLoading) return;
        
        this.isLoading = true;
        
        if (reset) {
            this.currentPage = 1;
            document.getElementById('main-news').innerHTML = '';
        }
        
        try {
            const params = new URLSearchParams({
                limit: this.pageSize,
                page: this.currentPage
            });
            
            if (this.currentFilters.category) {
                params.append('category', this.currentFilters.category);
            }
            
            if (this.currentFilters.featured) {
                params.append('featured', this.currentFilters.featured);
            }
            
            if (this.currentFilters.search) {
                params.append('search', this.currentFilters.search);
            }
            
            const response = await fetch(`/investments/api/news/?${params}`);
            const data = await response.json();
            
            if (data.status === 'success') {
                this.renderMainNews(data.articles, reset);
                this.updateLoadMoreButton(data.articles.length);
            }
        } catch (error) {
            console.error('Error loading main news:', error);
        } finally {
            this.isLoading = false;
        }
    }
    
    renderMainNews(articles, reset = false) {
        const container = document.getElementById('main-news');
        if (!container) return;
        
        if (reset) {
            container.innerHTML = '';
        }
        
        articles.forEach(article => {
            const articleElement = this.createMainArticleElement(article);
            container.appendChild(articleElement);
        });
    }
    
    createMainArticleElement(article) {
        const div = document.createElement('div');
        div.className = 'main-news-item';
        div.innerHTML = `
            <div class="main-news-content">
                <div class="main-news-image">
                    <img src="${article.image_url || '/static/images/news-placeholder.jpg'}" 
                         alt="${article.title}"
                         onerror="this.src='/static/images/news-placeholder.jpg'">
                </div>
                <div class="main-news-text">
                    <div class="main-news-meta">
                        <span class="news-source">${article.source_name}</span>
                        <span class="news-category">${article.category_name}</span>
                        <span class="news-time">${article.time_ago}</span>
                    </div>
                    <h4 class="main-news-title">
                        <a href="${article.url}" target="_blank" onclick="newsDashboard.trackClick('${article.id}')">
                            ${article.title}
                        </a>
                    </h4>
                    <p class="main-news-summary">${article.summary}</p>
                    <div class="main-news-actions">
                        <a href="${article.url}" target="_blank" class="btn btn-sm btn-primary">
                            Read More <i class="fas fa-external-link-alt"></i>
                        </a>
                        <button class="btn btn-sm btn-outline-secondary" onclick="newsDashboard.shareArticle('${article.id}', '${article.title}', '${article.url}')">
                            <i class="fas fa-share"></i> Share
                        </button>
                    </div>
                </div>
            </div>
            ${article.is_featured ? '<div class="featured-badge"><i class="fas fa-star"></i> Featured</div>' : ''}
        `;
        
        return div;
    }
    
    async loadMoreNews() {
        this.currentPage++;
        await this.loadMainNews(false);
    }
    
    resetAndLoadNews() {
        this.loadMainNews(true);
    }
    
    async refreshAllNews() {
        const refreshBtn = document.getElementById('refresh-news');
        const originalText = refreshBtn.innerHTML;
        
        refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Refreshing...';
        refreshBtn.disabled = true;
        
        try {
            // Trigger server-side news refresh
            await fetch('/investments/api/news/refresh/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken(),
                    'Content-Type': 'application/json',
                },
            });
            
            // Reload all news
            await Promise.all([
                this.loadFeaturedNews(),
                this.loadMainNews(true)
            ]);
            
            // Show success message
            this.showNotification('News refreshed successfully!', 'success');
            
        } catch (error) {
            console.error('Error refreshing news:', error);
            this.showNotification('Failed to refresh news. Please try again.', 'error');
        } finally {
            refreshBtn.innerHTML = originalText;
            refreshBtn.disabled = false;
        }
    }
    
    async loadUserPreferences() {
        try {
            const response = await fetch('/investments/api/news/preferences/');
            const data = await response.json();
            
            if (data.status === 'success') {
                this.populatePreferencesForm(data.preferences);
            }
        } catch (error) {
            console.error('Error loading user preferences:', error);
        }
    }
    
    populatePreferencesForm(preferences) {
        // Set preferred categories
        preferences.preferred_categories.forEach(category => {
            const checkbox = document.getElementById(`cat_${category}`);
            if (checkbox) checkbox.checked = true;
        });
        
        // Set other preferences
        document.getElementById('autoRefresh').checked = preferences.auto_refresh_enabled;
        document.getElementById('refreshInterval').value = preferences.refresh_interval_minutes;
        document.getElementById('showFeaturedOnly').checked = preferences.show_featured_only;
    }
    
    async saveNewsPreferences() {
        try {
            const form = document.getElementById('newsPreferencesForm');
            const formData = new FormData(form);
            
            const preferences = {
                preferred_categories: Array.from(formData.getAll('preferred_categories')),
                auto_refresh_enabled: formData.has('auto_refresh_enabled'),
                refresh_interval_minutes: parseInt(formData.get('refresh_interval_minutes')),
                show_featured_only: formData.has('show_featured_only')
            };
            
            const response = await fetch('/investments/api/news/preferences/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken(),
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(preferences)
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                this.showNotification('Preferences saved successfully!', 'success');
                $('#newsSettingsModal').modal('hide');
                
                // Reload news with new preferences
                this.resetAndLoadNews();
            } else {
                this.showNotification('Failed to save preferences.', 'error');
            }
        } catch (error) {
            console.error('Error saving preferences:', error);
            this.showNotification('Failed to save preferences.', 'error');
        }
    }
    
    async trackClick(articleId) {
        try {
            await fetch(`/investments/api/news/articles/${articleId}/track_click/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken(),
                    'Content-Type': 'application/json',
                },
            });
        } catch (error) {
            console.error('Error tracking click:', error);
        }
    }
    
    shareArticle(articleId, title, url) {
        if (navigator.share) {
            navigator.share({
                title: title,
                url: url
            });
        } else {
            // Fallback: copy to clipboard
            navigator.clipboard.writeText(url).then(() => {
                this.showNotification('Article link copied to clipboard!', 'success');
            });
        }
    }
    
    updateLoadMoreButton(articleCount) {
        const loadMoreBtn = document.getElementById('load-more-news');
        const container = document.getElementById('load-more-container');
        
        if (articleCount < this.pageSize) {
            container.style.display = 'none';
        } else {
            container.style.display = 'block';
        }
    }
    
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
        notification.style.position = 'fixed';
        notification.style.top = '20px';
        notification.style.right = '20px';
        notification.style.zIndex = '9999';
        notification.style.minWidth = '300px';
        
        notification.innerHTML = `
            ${message}
            <button type="button" class="close" data-dismiss="alert">
                <span>&times;</span>
            </button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
    }
    
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
    
    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
               document.querySelector('meta[name="csrf-token"]')?.content || '';
    }
}

// Initialize news dashboard when DOM is loaded
let newsDashboard;
document.addEventListener('DOMContentLoaded', function() {
    newsDashboard = new NewsDashboard();
});
