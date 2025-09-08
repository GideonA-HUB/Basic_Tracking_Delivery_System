# 🔄 Auto-Refresh Setup Guide

## ✅ **System Ready for Auto-Refresh!**

Your news system now has a public refresh endpoint that can be called by external cron services to automatically fetch new news every 15 minutes.

---

## 🚀 **Setup Options**

### **Option 1: Railway Cron Jobs (Recommended)**

Railway supports cron jobs natively. Here's how to set it up:

#### **Step 1: Create a Cron Job in Railway**
1. **Go to Railway Dashboard**
2. **Select your project**
3. **Click "Settings" tab**
4. **Scroll down to "Cron Jobs" section**
5. **Click "Add Cron Job"**

#### **Step 2: Configure the Cron Job**
- **Command**: `python manage.py fetch_news`
- **Schedule**: `*/15 * * * *` (every 15 minutes)
- **Description**: `Fetch news from APIs`

#### **Step 3: Save and Deploy**
- **Click "Save"**
- **Railway will automatically deploy the cron job**

---

### **Option 2: External Cron Service (Alternative)**

If Railway doesn't support cron jobs, you can use an external service:

#### **Using Cron-job.org (Free)**
1. **Visit**: https://cron-job.org/
2. **Sign up** for a free account
3. **Create a new cron job**:
   - **URL**: `https://meridianassetlogistics.com/investments/api/news/refresh/public/?token=meridian-news-refresh-2025`
   - **Schedule**: Every 15 minutes
   - **Method**: GET

#### **Using UptimeRobot (Free)**
1. **Visit**: https://uptimerobot.com/
2. **Sign up** for a free account
3. **Add a new monitor**:
   - **Type**: HTTP(s)
   - **URL**: `https://meridianassetlogistics.com/investments/api/news/refresh/public/?token=meridian-news-refresh-2025`
   - **Interval**: 15 minutes

#### **Using EasyCron (Free)**
1. **Visit**: https://www.easycron.com/
2. **Sign up** for a free account
3. **Create a new cron job**:
   - **URL**: `https://meridianassetlogistics.com/investments/api/news/refresh/public/?token=meridian-news-refresh-2025`
   - **Schedule**: Every 15 minutes
   - **Method**: GET

---

### **Option 3: Manual Testing**

You can test the refresh endpoint manually:

#### **Test the Endpoint**
Visit this URL in your browser:
```
https://meridianassetlogistics.com/investments/api/news/refresh/public/?token=meridian-news-refresh-2025
```

#### **Expected Response**
```json
{
    "status": "success",
    "message": "Refreshed news successfully",
    "articles_fetched": 25,
    "articles_saved": 20,
    "timestamp": "2025-01-08T10:30:00.000Z"
}
```

---

## 🔧 **Add Refresh Token to Railway**

### **Step 1: Add to Railway Environment Variables**
1. **Go to Railway Dashboard**
2. **Select your project**
3. **Click "Variables" tab**
4. **Add this variable**:
   ```
   NEWS_REFRESH_TOKEN=meridian-news-refresh-2025
   ```

### **Step 2: Deploy**
- **Railway will automatically redeploy**
- **The refresh endpoint will be secured**

---

## 📊 **What Happens During Auto-Refresh**

### **Every 15 Minutes:**
1. **Fetches News** from all configured APIs:
   - NewsAPI (stocks, real estate, general finance)
   - CoinDesk (cryptocurrency news)
   - Finnhub (stock market data)
   - CryptoPanic (additional crypto news)

2. **Saves New Articles** to database
3. **Updates Featured News** based on relevance
4. **Caches Results** for better performance
5. **Logs Activity** for monitoring

### **Expected Results:**
- **✅ Fresh News**: New articles every 15 minutes
- **✅ No Duplicates**: System prevents duplicate articles
- **✅ Featured Updates**: Most relevant news gets featured
- **✅ Performance**: Cached results for fast loading
- **✅ Monitoring**: Logs for troubleshooting

---

## 🧪 **Test Your Setup**

### **Step 1: Test the Endpoint**
Visit: `https://meridianassetlogistics.com/investments/api/news/refresh/public/?token=meridian-news-refresh-2025`

### **Step 2: Check the News Dashboard**
Visit: `https://meridianassetlogistics.com/investments/news/`

### **Step 3: Monitor the Logs**
Check Railway logs to see the refresh activity.

---

## 📈 **Monitoring and Maintenance**

### **Check Refresh Status**
- **Visit the endpoint** to see if it's working
- **Check Railway logs** for any errors
- **Monitor news dashboard** for new articles

### **Troubleshooting**
- **401 Error**: Check if the token is correct
- **500 Error**: Check if API keys are configured
- **No New Articles**: Check if APIs are working

### **Performance Optimization**
- **Adjust Frequency**: Change from 15 minutes to 30 minutes if needed
- **Limit Articles**: Reduce the number of articles fetched per API
- **Monitor Usage**: Check API usage limits

---

## 🎯 **Recommended Setup**

### **For Production:**
1. **Use Railway Cron Jobs** (if available)
2. **Set refresh interval** to 15 minutes
3. **Monitor logs** regularly
4. **Set up alerts** for failures

### **For Development:**
1. **Use external cron service** (cron-job.org)
2. **Test manually** first
3. **Monitor API usage**
4. **Adjust frequency** as needed

---

## 🎉 **You're All Set!**

Your news system will now automatically refresh every 15 minutes, keeping your investment platform up-to-date with the latest news from multiple sources!

**Benefits:**
- ✅ **Always Fresh**: News updates every 15 minutes
- ✅ **Multiple Sources**: NewsAPI, CoinDesk, Finnhub, CryptoPanic
- ✅ **Automatic**: No manual intervention needed
- ✅ **Reliable**: Fallback mechanisms for API failures
- ✅ **Monitored**: Logs and status tracking

**Your investment platform now has a fully automated news system!** 🚀
