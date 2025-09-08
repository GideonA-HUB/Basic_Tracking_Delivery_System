# News Integration System Setup Guide

## 🚀 **Complete News Integration System for Meridian Asset Logistics**

This guide will help you set up a comprehensive news integration system that fetches real-time news related to Bitcoin, Ethereum, cryptocurrencies, real estate, and stock markets.

## 📋 **Features Implemented**

### ✅ **Core Features**
- **Multi-API Integration**: CryptoControl, NewsAPI, Finnhub
- **Real-time News Fetching**: Automatic updates every 15 minutes
- **Categorized News**: Crypto, Stocks, Real Estate, General Finance
- **Dashboard Integration**: News widgets in investment dashboard
- **Marketplace Integration**: Related news for each asset type
- **Portfolio Integration**: News relevant to user's investments
- **Admin Controls**: Enable/disable sources, pin featured news
- **User Preferences**: Customizable news filtering
- **Analytics Tracking**: View and click tracking
- **Responsive Design**: Works on all devices

### ✅ **News Sources**
- **CryptoControl**: Cryptocurrency news (Bitcoin, Ethereum, Altcoins)
- **NewsAPI**: General finance, stocks, real estate news
- **Finnhub**: Stock market and company-specific news

### ✅ **News Categories**
- Cryptocurrency
- Stock Market
- Real Estate
- Forex
- Commodities
- General Finance
- Bitcoin-specific
- Ethereum-specific
- Altcoins

## 🛠️ **Setup Instructions**

### **Step 1: Run Database Migrations**

```bash
# Create migrations for news models
python manage.py makemigrations investments

# Apply migrations
python manage.py migrate
```

### **Step 2: Set Up News System**

```bash
# Set up news sources and categories
python manage.py setup_news_system

# Fetch initial news (optional)
python manage.py setup_news_system --fetch-initial-news
```

### **Step 3: Configure API Keys**

Add these environment variables to your Railway deployment:

```env
# News API Keys
NEWSAPI_KEY=your_newsapi_key_here
FINNHUB_API_KEY=your_finnhub_api_key_here
CRYPTOCONTROL_API_KEY=your_cryptocontrol_key_here
```

### **Step 4: Set Up Automated News Fetching**

Add a cron job to fetch news regularly:

```bash
# Fetch news every 15 minutes
*/15 * * * * cd /path/to/your/project && python manage.py fetch_news
```

## 🔑 **API Keys Setup**

### **1. NewsAPI (Free Tier Available)**
- Visit: https://newsapi.org/
- Sign up for free account
- Get API key from dashboard
- Free tier: 1000 requests/day

### **2. Finnhub (Free Tier Available)**
- Visit: https://finnhub.io/
- Sign up for free account
- Get API key from dashboard
- Free tier: 60 calls/minute

### **3. CryptoControl (Free Tier Available)**
- Visit: https://cryptocontrol.io/
- Sign up for free account
- Get API key from dashboard
- Free tier: 1000 requests/day

## 📱 **Usage Guide**

### **For Users**

#### **Dashboard News Widget**
- Located on investment dashboard
- Shows featured, crypto, stocks, and real estate news
- Auto-refreshes every 15 minutes
- Click to read full articles

#### **Marketplace News Widget**
- Shows news relevant to specific asset types
- Appears on individual asset pages
- Contextual news based on asset category

#### **News Dashboard**
- Access at: `/investments/news/`
- Full news browsing experience
- Filter by category, search, featured
- User preferences and settings

### **For Administrators**

#### **News Management**
- Access admin panel: `/admin/investments/`
- Manage news sources and categories
- View analytics and engagement
- Pin featured news articles

#### **Manual News Refresh**
```bash
# Refresh all news
python manage.py fetch_news

# Refresh specific category
python manage.py fetch_news --category crypto

# Set up sources only
python manage.py fetch_news --setup-sources
```

## 🎨 **Integration Examples**

### **Dashboard Integration**
```html
<!-- Include in dashboard template -->
{% include 'investments/dashboard_news_widget.html' %}
```

### **Marketplace Integration**
```html
<!-- Include in marketplace template -->
{% include 'investments/marketplace_news_widget.html' %}
```

### **Custom News Widget**
```html
<!-- Custom news widget -->
<div class="news-widget" data-widget-type="crypto" data-limit="10">
    <!-- Widget content -->
</div>
```

## 🔧 **API Endpoints**

### **News API**
- `GET /investments/api/news/` - Get news articles
- `GET /investments/api/news/widget/` - Get news for widgets
- `POST /investments/api/news/refresh/` - Refresh news (admin)
- `GET /investments/api/news/preferences/` - Get user preferences
- `POST /investments/api/news/preferences/` - Update preferences

### **Article Tracking**
- `POST /investments/api/news/articles/{id}/track_view/` - Track article view
- `POST /investments/api/news/articles/{id}/track_click/` - Track article click

## 📊 **Analytics & Tracking**

### **Available Metrics**
- Article views and clicks
- User engagement by category
- Popular news sources
- Time-based analytics
- User preference insights

### **Admin Analytics**
- Access via Django admin
- View engagement statistics
- Export analytics data
- Monitor API usage

## 🎯 **Customization Options**

### **News Sources**
- Add new news sources in admin
- Configure rate limits
- Enable/disable sources
- Custom API endpoints

### **Categories**
- Add custom categories
- Configure display names
- Set sort order
- Enable/disable categories

### **User Preferences**
- Preferred categories
- Auto-refresh settings
- Featured news only
- Refresh intervals

## 🚨 **Troubleshooting**

### **Common Issues**

#### **News Not Loading**
1. Check API keys are set correctly
2. Verify network connectivity
3. Check API rate limits
4. Review server logs

#### **API Rate Limits**
1. Check API usage in admin
2. Adjust refresh intervals
3. Upgrade API plans if needed
4. Implement better caching

#### **Database Issues**
1. Run migrations: `python manage.py migrate`
2. Check database connectivity
3. Verify model imports
4. Review error logs

### **Debug Commands**
```bash
# Test news fetching
python manage.py fetch_news --limit 5

# Check news sources
python manage.py shell
>>> from investments.news_models import NewsSource
>>> NewsSource.objects.all()

# Test API connections
python manage.py shell
>>> from investments.news_services import NewsAggregatorService
>>> aggregator = NewsAggregatorService()
>>> articles = aggregator.fetch_all_news(5)
```

## 📈 **Performance Optimization**

### **Caching Strategy**
- API responses cached for 15 minutes
- Database queries optimized with indexes
- Frontend caching for widgets
- CDN for static assets

### **Rate Limiting**
- Respects API rate limits
- Implements backoff strategies
- Queues requests when needed
- Monitors usage patterns

## 🔒 **Security Features**

### **Data Protection**
- No sensitive data in logs
- Secure API key storage
- User data encryption
- GDPR compliance ready

### **Access Control**
- Admin-only news refresh
- User-specific preferences
- Secure API endpoints
- CSRF protection

## 🎉 **Success Indicators**

Your news system is working correctly when:

1. ✅ News articles appear in dashboard widgets
2. ✅ Categories filter correctly
3. ✅ Auto-refresh works every 15 minutes
4. ✅ Click tracking functions properly
5. ✅ Admin can manage sources and categories
6. ✅ Users can set preferences
7. ✅ API keys are configured correctly
8. ✅ No errors in server logs

## 📞 **Support**

For issues or questions:
1. Check the troubleshooting section
2. Review server logs
3. Test API connections
4. Verify database setup
5. Contact system administrator

---

**🎯 The News Integration System is now ready to provide your users with real-time, relevant investment news across all platforms!**
