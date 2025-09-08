# Email Configuration Troubleshooting Guide

## 🚨 Current Issue Analysis

Based on the persistent email configuration failures, there are multiple potential causes:

### **Issue #1: Railway Environment Variables Not Loading**
- Django shows default values instead of Railway environment variables
- This suggests a fundamental issue with Railway's environment variable system

### **Issue #2: Incorrect SMTP Server Configuration**
- Current: `mail.meridianassetlogistics.com`
- Correct Namecheap: `mail.privateemail.com`

### **Issue #3: Namecheap Email Account Status**
- Account might not be fully activated
- DNS records might not be properly configured

## 🔧 Step-by-Step Resolution

### **Step 1: Verify Railway Environment Variables**

1. **Check Railway Dashboard**:
   - Go to your Railway project
   - Verify these variables are set:
   ```
   EMAIL_HOST=mail.privateemail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_USE_SSL=False
   EMAIL_HOST_USER=meridian@meridianassetlogistics.com
   EMAIL_HOST_PASSWORD=your-actual-password
   DEFAULT_FROM_EMAIL=meridian@meridianassetlogistics.com
   SERVER_EMAIL=meridian@meridianassetlogistics.com
   ```

2. **Test Environment Variables**:
   - Visit: `https://meridianassetlogistics.com/api/debug-env/`
   - Check if `railway_detection` shows Railway environment variables

### **Step 2: Fix Namecheap Email Configuration**

1. **Create Email Account** (if not done):
   - Login to Namecheap
   - Go to Domain List → Manage `meridianassetlogistics.com`
   - Create email: `meridian@meridianassetlogistics.com`
   - Set strong password

2. **Configure DNS Records**:
   - **MX Records**:
     - `mx1.privateemail.com` (Priority: 10)
     - `mx2.privateemail.com` (Priority: 10)
   - **SPF Record**:
     - Type: TXT
     - Host: @
     - Value: `v=spf1 include:spf.privateemail.com ~all`

3. **Verify Email Account**:
   - Try logging into webmail at: `https://webmail.privateemail.com`
   - Username: `meridian@meridianassetlogistics.com`
   - Password: [Your email password]

### **Step 3: Update Railway Environment Variables**

Update your Railway environment variables to use the correct Namecheap settings:

```env
# Correct Namecheap Private Email Settings
EMAIL_HOST=mail.privateemail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=meridian@meridianassetlogistics.com
EMAIL_HOST_PASSWORD=your-actual-email-password
DEFAULT_FROM_EMAIL=meridian@meridianassetlogistics.com
SERVER_EMAIL=meridian@meridianassetlogistics.com

# Alternative SMTP settings (if 587 doesn't work)
SMTP_HOST=mail.privateemail.com
SMTP_PORT=465
SMTP_USER=meridian@meridianassetlogistics.com
SMTP_PASSWORD=your-actual-email-password
```

### **Step 4: Test Email Configuration**

1. **Deploy the updated code** to Railway
2. **Test environment variables**: `https://meridianassetlogistics.com/api/debug-env/`
3. **Test email functionality**: `https://meridianassetlogistics.com/api/test-email/`

### **Step 5: Alternative Testing Methods**

If the above doesn't work, try these alternatives:

1. **Test with different ports**:
   - Port 465 (SSL)
   - Port 587 (TLS)
   - Port 25 (unencrypted - not recommended)

2. **Test with different SMTP servers**:
   - `mail.privateemail.com` (primary)
   - `smtp.privateemail.com` (alternative)

3. **Manual email test**:
   ```python
   from django.core.mail import send_mail
   send_mail('Test', 'Test message', 'meridian@meridianassetlogistics.com', ['your-test@email.com'])
   ```

## 🔍 Diagnostic Commands

### **Check Railway Logs**:
```bash
railway logs
```

### **Check Environment Variables**:
```bash
railway variables
```

### **Test Email Manually**:
```python
# In Django shell
from django.core.mail import send_mail
from django.conf import settings
print(f"Email Host: {settings.EMAIL_HOST}")
print(f"Email Port: {settings.EMAIL_PORT}")
print(f"Email User: {settings.EMAIL_HOST_USER}")
```

## 🚨 Common Issues and Solutions

### **Issue: Environment Variables Not Loading**
- **Cause**: Railway environment variable system issue
- **Solution**: Use multiple fallback strategies in Django settings

### **Issue: SMTP Authentication Failed**
- **Cause**: Wrong password or email account not activated
- **Solution**: Verify email account and password in Namecheap

### **Issue: Connection Timeout**
- **Cause**: Wrong SMTP server or port
- **Solution**: Use `mail.privateemail.com` with port 587 or 465

### **Issue: DNS Not Propagated**
- **Cause**: DNS changes take time to propagate
- **Solution**: Wait 30 minutes and test again

## 📞 Support Contacts

- **Namecheap Support**: https://www.namecheap.com/support/
- **Railway Support**: https://railway.app/help

## ✅ Success Indicators

You'll know the email system is working when:

1. **Debug endpoint shows**:
   ```json
   {
     "django_settings": {
       "EMAIL_HOST": "mail.privateemail.com",
       "EMAIL_HOST_USER": "meridian@meridianassetlogistics.com",
       "DEFAULT_FROM_EMAIL": "meridian@meridianassetlogistics.com"
     }
   }
   ```

2. **Email test returns**:
   ```json
   {
     "status": "success",
     "email_from": "meridian@meridianassetlogistics.com"
   }
   ```

3. **You receive a test email** at the configured address
