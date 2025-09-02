# Railway Deployment Fix Guide

## 🚨 Critical Issues Fixed

### 1. Daphne Command Syntax Error
**Problem**: `daphne: error: unrecognized arguments: --env DJANGO_SETTINGS_MODULE=delivery_tracker.settings_production`

**Solution**: Removed invalid `--env` flag and set environment variable correctly:
```bash
DJANGO_SETTINGS_MODULE=delivery_tracker.settings_production daphne -b 0.0.0.0 -p $PORT delivery_tracker.asgi:application
```

### 2. Django AppRegistryNotReady Error
**Problem**: `django.core.exceptions.AppRegistryNotReady: Apps aren't loaded yet.`

**Solution**: 
- Modified `asgi.py` to call `django.setup()` before importing WebSocket routing
- Updated `consumers.py` to use `apps.get_model()` instead of direct imports

## 🔧 Required Railway Environment Variables

Set these in your Railway project dashboard under Variables tab:

| Variable Name | Value | Required |
|---------------|-------|----------|
| `DJANGO_SETTINGS_MODULE` | `delivery_tracker.settings_production` | ✅ Yes |
| `DATABASE_URL` | `[Your PostgreSQL connection string]` | ✅ Yes |
| `SECRET_KEY` | `[Your Django secret key]` | ✅ Yes |
| `DJANGO_SUPERUSER_PASSWORD` | `[Admin password]` | ✅ Yes |
| `ALLOWED_HOSTS` | `meridianassetlogistics.com,meridian-asset-logistics.up.railway.app` | ✅ Yes |
| `CORS_ALLOWED_ORIGINS` | `https://meridianassetlogistics.com,https://meridian-asset-logistics.up.railway.app` | ✅ Yes |
| `CSRF_TRUSTED_ORIGINS` | `https://meridianassetlogistics.com,https://meridian-asset-logistics.up.railway.app` | ✅ Yes |

## 🚀 Deployment Steps

1. **Commit and push the fixes:**
   ```bash
   git add .
   git commit -m "Fix ASGI configuration and Daphne command syntax"
   git push origin main
   ```

2. **Set environment variables in Railway dashboard**

3. **Wait for auto-deploy (5-10 minutes)**

4. **Verify deployment success**

## ✅ Expected Results After Fix

- ✅ Container starts successfully (no more Daphne errors)
- ✅ Django apps load properly (no more AppRegistryNotReady errors)
- ✅ WebSocket endpoint `/ws/price-feeds/` works
- ✅ Live price updates function properly
- ✅ Website opens without 502 errors
- ✅ Real-time charts and updates visible

## 🔍 Troubleshooting

If you still see errors:

1. **Check Railway logs** for new error messages
2. **Verify environment variables** are set correctly
3. **Ensure all files are committed** and pushed
4. **Wait for complete deployment** before testing

## 📁 Files Modified

- `delivery_tracker/asgi.py` - Fixed Django initialization order
- `investments/consumers.py` - Fixed model imports
- `railway.json` - Fixed Daphne command syntax
- `delivery_tracker/settings_production.py` - Added channels configuration

The fix addresses both the Daphne syntax error and the Django initialization issue, ensuring your WebSocket-based live updates will work properly in production.
