# Railway Production Email Setup Guide

## 🚀 Setting Up Email for meridianassetlogistics.com

### Step 1: Create Email Account on Namecheap

1. **Login to Namecheap** → Domain List
2. **Find meridianassetlogistics.com** → Click "Manage"
3. **Go to Email section** → "Private Email" or "Email Hosting"
4. **Create Email Account**:
   - Email: `meridian@meridianassetlogistics.com`
   - Password: [Create strong password - save this!]
   - Mailbox Size: 1GB (or as needed)

### Step 2: Railway Environment Variables

Add these variables in your Railway project dashboard:

```env
# Production Settings
DEBUG=False
ALLOWED_HOSTS=meridianassetlogistics.com,www.meridianassetlogistics.com
CSRF_TRUSTED_ORIGINS=https://meridianassetlogistics.com,https://www.meridianassetlogistics.com
SITE_URL=https://meridianassetlogistics.com

# Email Configuration (Namecheap)
EMAIL_HOST=mail.meridianassetlogistics.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=meridian@meridianassetlogistics.com
EMAIL_HOST_PASSWORD=your-actual-email-password-here
DEFAULT_FROM_EMAIL=meridian@meridianassetlogistics.com
SERVER_EMAIL=meridian@meridianassetlogistics.com

# Database (if using Railway PostgreSQL)
DATABASE_URL=your-railway-database-url

# Other API Keys
GOOGLE_MAPS_API_KEY=your-google-maps-key
NOWPAYMENTS_API_KEY=your-nowpayments-key
NOWPAYMENTS_IPN_SECRET=your-nowpayments-secret
NOWPAYMENTS_IPN_URL=https://meridianassetlogistics.com/investments/api/payments/ipn/
```

### Step 3: Test Email Configuration

After deploying with the new environment variables:

1. **SSH into your Railway deployment** (if available)
2. **Run the test command**:
   ```bash
   python manage.py test_email
   ```

Or create a simple test endpoint in your Django app:

```python
# In your views.py
from django.http import JsonResponse
from tracking.email_utils import test_email_configuration

def test_email_view(request):
    success = test_email_configuration()
    return JsonResponse({'email_test': 'success' if success else 'failed'})
```

### Step 4: Email Client Setup (Optional)

If you want to use this email in Gmail, Outlook, etc.:

**IMAP Settings:**
- Server: `mail.meridianassetlogistics.com`
- Port: 993 (SSL)
- Username: `meridian@meridianassetlogistics.com`
- Password: [Your email password]

**SMTP Settings:**
- Server: `mail.meridianassetlogistics.com`
- Port: 587 (STARTTLS)
- Username: `meridian@meridianassetlogistics.com`
- Password: [Your email password]

### Step 5: Using Email in Your App

```python
from tracking.email_utils import send_tracking_notification

# Send tracking update
send_tracking_notification(
    recipient_email='customer@example.com',
    tracking_number='TRK123456',
    status='In Transit',
    delivery_info={
        'location': 'Distribution Center',
        'estimated_delivery': 'Tomorrow'
    }
)
```

### Troubleshooting

**Common Issues:**

1. **Email not sending**: Check Railway logs for SMTP errors
2. **Authentication failed**: Verify email password in Railway variables
3. **Connection timeout**: Check if Railway allows outbound SMTP connections
4. **Domain not found**: Ensure DNS is properly configured for mail subdomain

**Railway Logs:**
```bash
railway logs
```

**Test Email Manually:**
```python
from django.core.mail import send_mail
send_mail('Test', 'Test message', 'meridian@meridianassetlogistics.com', ['your-test@email.com'])
```

### Security Notes

- Never commit email passwords to git
- Use Railway's environment variables for all sensitive data
- Enable 2FA on your Namecheap account
- Use strong, unique passwords for email account
