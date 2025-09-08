# 🔑 News API Keys Setup Guide

## ✅ **System Updated!**

The news system now supports **5 different APIs** for comprehensive news coverage:

1. **NewsAPI** - General finance, stocks, real estate news
2. **Finnhub** - Stock market data, company news  
3. **CoinGecko** - Cryptocurrency prices and news
4. **CryptoPanic** - Cryptocurrency news aggregation
5. **CoinDesk** - Bitcoin and cryptocurrency news

---

## 🚀 **How to Get Each API Key**

### **1. NewsAPI Key (Recommended First)**

**Step-by-Step:**
1. **Visit**: https://newsapi.org/
2. **Click**: "Get API Key" (top right)
3. **Sign Up**: Enter email and password
4. **Verify Email**: Check your inbox and click verification link
5. **Get Key**: After verification, you'll see your API key on the dashboard
6. **Copy Key**: It looks like `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6`

**Free Tier**: 1,000 requests/day
**Best For**: General finance, stocks, real estate news

---

### **2. Finnhub API Key**

**Step-by-Step:**
1. **Visit**: https://finnhub.io/
2. **Click**: "Get Free API Key"
3. **Sign Up**: Enter email and password
4. **Verify Email**: Check your inbox and click verification link
5. **Get Key**: Go to dashboard, your key will be displayed
6. **Copy Key**: It looks like `c1d2e3f4g5h6i7j8k9l0m1n2o3p4q5r6`

**Free Tier**: 60 calls/minute, 1,000 calls/day
**Best For**: Stock market data, company news

---

### **3. CoinGecko API Key**

**Step-by-Step:**
1. **Visit**: https://www.coingecko.com/en/api
2. **Click**: "Get Free API Key"
3. **Sign Up**: Create account
4. **Get Key**: Available on dashboard
5. **Copy Key**: It looks like `x1y2z3a4b5c6d7e8f9g0h1i2j3k4l5m6`

**Free Tier**: 1,000 requests/day
**Best For**: Cryptocurrency prices and news

---

### **4. CryptoPanic API Key**

**Step-by-Step:**
1. **Visit**: https://cryptopanic.com/developers/api/
2. **Sign Up**: Create account
3. **Get Key**: Available after registration
4. **Copy Key**: It looks like `p1q2r3s4t5u6v7w8x9y0z1a2b3c4d5e6`

**Free Tier**: 1,000 requests/day
**Best For**: Cryptocurrency news aggregation

---

### **5. CoinDesk API Key**

**Step-by-Step:**
1. **Visit**: https://www.coindesk.com/coindesk20
2. **Look for**: API documentation or contact them
3. **Sign Up**: Create account
4. **Get Key**: Available after registration
5. **Copy Key**: It looks like `m1n2o3p4q5r6s7t8u9v0w1x2y3z4a5b6`

**Free Tier**: Limited free tier available
**Best For**: Bitcoin and cryptocurrency news

---

## 🔧 **Add to Railway Environment Variables**

### **Step 1: Go to Railway Dashboard**
1. Visit: https://railway.app/
2. Login to your account
3. Select your `meridian-asset-logistics` project

### **Step 2: Add Environment Variables**
1. **Click**: "Variables" tab
2. **Add these variables**:
   ```
   NEWSAPI_KEY=your_actual_newsapi_key_here
   FINNHUB_API_KEY=your_actual_finnhub_key_here
   COINGECKO_API_KEY=your_actual_coingecko_key_here
   CRYPTOPANIC_API_KEY=your_actual_cryptopanic_key_here
   COINDESK_API_KEY=your_actual_coindesk_key_here
   ```

### **Step 3: Deploy**
1. **Railway will automatically redeploy**
2. **Wait for deployment to complete**
3. **Test the system**

---

## 🧪 **Test the System**

### **With Sample Data (No API Keys Needed):**
- Visit: `https://meridianassetlogistics.com/investments/news/`
- You should see 15 sample news articles
- Test the dashboard widgets
- Test the marketplace integration

### **With Real API Keys:**
- After adding API keys to Railway
- Visit: `https://meridianassetlogistics.com/investments/news/`
- You should see real, live news articles
- News will auto-refresh every 15 minutes

---

## 📊 **Expected Results**

### **After Adding API Keys:**
- **Real-time news** from multiple sources
- **Categorized news** (Crypto, Stocks, Real Estate)
- **Auto-refresh** every 15 minutes
- **Professional news widgets** in dashboard and marketplace
- **User engagement tracking**
- **Admin controls** for managing news

### **News Categories You'll See:**
- **Bitcoin News**: Latest Bitcoin updates
- **Ethereum News**: Ethereum developments
- **Stock Market**: NASDAQ, NYSE, trading news
- **Real Estate**: Property, housing, mortgage news
- **General Finance**: Investment, market analysis

---

## 🎯 **Priority Order**

### **Start Here (Recommended):**
1. **NewsAPI** - Easiest to set up, covers most news types
2. **CoinGecko** - Great for cryptocurrency news
3. **Finnhub** - Perfect for stock market data

### **Alternative:**
- Start with just **NewsAPI** to test the system
- Add other APIs later as needed

---

## 💡 **Pro Tips**

1. **Free Tiers Are Sufficient**: All APIs offer generous free tiers
2. **Start Simple**: Begin with NewsAPI, add others gradually
3. **Test First**: Use sample data to test the system before adding real APIs
4. **Monitor Usage**: Check API usage in the admin panel
5. **Backup Plan**: Sample data ensures the system works even without APIs

---

## 🔄 **Update News Sources**

After adding API keys, update the news sources in the database:

```bash
python manage.py fetch_news --setup-sources
```

This will create the new news sources (CoinGecko, CryptoPanic, CoinDesk) in your database.

---

## 📈 **Auto-Refresh Setup**

To automatically fetch news every 15 minutes, add this to your cron job:

```bash
*/15 * * * * python manage.py fetch_news
```

---

## 🎉 **You're All Set!**

The news system is now **fully functional** with sample data and ready for real API integration! 

**Next Steps:**
1. Get your API keys (start with NewsAPI)
2. Add them to Railway environment variables
3. Test the live system
4. Set up auto-refresh cron job

**Your investment platform will now have:**
- ✅ Live cryptocurrency news
- ✅ Stock market updates  
- ✅ Real estate news
- ✅ Professional news widgets
- ✅ Auto-refreshing content
- ✅ User engagement tracking
