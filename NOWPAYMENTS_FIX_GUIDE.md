# NOWPayments Fix Guide

## Issues Fixed

### 1. API Key Format Validation
- **Problem**: The API key validation was too strict, only allowing numbers and dashes
- **Solution**: Updated validation to allow alphanumeric characters, dashes, and underscores
- **Files Modified**: `investments/services.py`

### 2. IPN Callback URL Configuration
- **Problem**: IPN callback URL was pointing to wrong domain
- **Solution**: Updated to use correct Railway domain: `https://meridian-asset-logistics.up.railway.app`
- **Files Modified**: 
  - `delivery_tracker/settings_production.py`
  - `investments/services.py`
  - `investments/views.py`

## Required Environment Variables

Make sure these environment variables are set in your Railway deployment:

```bash
# NOWPayments Configuration
NOWPAYMENTS_API_KEY=your_api_key_here
NOWPAYMENTS_IPN_SECRET=your_ipn_secret_here
NOWPAYMENTS_IPN_URL=https://meridian-asset-logistics.up.railway.app/investments/api/payments/ipn/
```

## How to Get NOWPayments Credentials

1. **API Key**:
   - Log in to your NOWPayments dashboard
   - Go to "Store settings" and enter your wallet address
   - Scroll to "API keys" section and click "Add new key"
   - Copy the generated API key

2. **IPN Secret**:
   - In the same dashboard, go to "Store settings"
   - Find the "IPN Secret" field
   - Generate or copy the IPN secret

3. **IPN Callback URL**:
   - Set to: `https://meridian-asset-logistics.up.railway.app/investments/api/payments/ipn/`

## Testing the Configuration

Run the test script to verify your configuration:

```bash
cd Basic_Tracking_Delivery_System
python test_nowpayments_config.py
```

## Deployment Steps

1. **Set Environment Variables in Railway**:
   - Go to your Railway project dashboard
   - Navigate to "Variables" tab
   - Add the required environment variables listed above

2. **Redeploy**:
   - Railway will automatically redeploy when you add environment variables
   - Or trigger a manual deployment

3. **Test Payment Flow**:
   - Try creating an investment payment
   - Try paying membership fee
   - Check logs for any remaining issues

## Troubleshooting

### If payments still fail:

1. **Check API Key Format**:
   - Ensure it's at least 10 characters long
   - Contains only alphanumeric characters, dashes, and underscores
   - No extra spaces or special characters

2. **Verify IPN URL**:
   - Must be exactly: `https://meridian-asset-logistics.up.railway.app/investments/api/payments/ipn/`
   - Must be accessible from the internet
   - Must use HTTPS

3. **Check Logs**:
   - Look for NOWPayments service initialization messages
   - Check for configuration validation errors
   - Monitor payment creation attempts

### Common Error Messages:

- `NOWPAYMENTS_API_KEY format is invalid`: API key doesn't meet format requirements
- `IPN callback URL is invalid`: URL format or accessibility issue
- `Payment service returned no data`: NOWPayments API call failed

## Files Modified

1. `investments/services.py` - Fixed API key validation and updated domain references
2. `delivery_tracker/settings_production.py` - Updated default IPN URL
3. `investments/views.py` - Updated error messages with correct domain
4. `test_nowpayments_config.py` - New test script for configuration validation

## Next Steps

After deploying these fixes:

1. Test investment payment creation
2. Test membership payment creation
3. Verify IPN webhook functionality
4. Monitor payment processing

The payment system should now work correctly with proper NOWPayments integration.
