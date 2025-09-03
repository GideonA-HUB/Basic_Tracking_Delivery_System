import hashlib
import hmac
import json
import logging
import requests
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)

class NOWPaymentsService:
    """Service class for handling NOWPayments API interactions"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'NOWPAYMENTS_API_KEY', None)
        self.api_url = getattr(settings, 'NOWPAYMENTS_API_URL', 'https://api.nowpayments.io/v1')
        self.ipn_secret = getattr(settings, 'NOWPAYMENTS_IPN_SECRET', None)
        self.ipn_callback_url = getattr(settings, 'NOWPAYMENTS_IPN_URL', '')
        
        logger.info(f"NOWPayments service initialized:")
        logger.info(f"  API Key: {'✅ Configured' if self.api_key else '❌ Missing'}")
        logger.info(f"  IPN Secret: {'✅ Configured' if self.ipn_secret else '❌ Missing'}")
        logger.info(f"  IPN Callback URL: {'✅ Configured' if self.ipn_callback_url else '❌ Missing'}")
        logger.info(f"  API URL: {self.api_url}")
        
        if not self.api_key:
            logger.error("NOWPAYMENTS_API_KEY not configured")
        if not self.ipn_secret:
            logger.error("NOWPAYMENTS_IPN_SECRET not configured")
        if not self.ipn_callback_url:
            logger.error("NOWPAYMENTS_IPN_URL not configured - IPN callbacks will fail")
    
    def _get_headers(self):
        """Get headers for API requests"""
        # Clean the API key by removing any whitespace or newlines
        clean_api_key = self.api_key.strip() if self.api_key else None
        
        if not clean_api_key:
            logger.error("NOWPAYMENTS_API_KEY is empty or None")
            return {}
        
        # Validate API key format (should start with a number and contain dashes)
        if not clean_api_key or not clean_api_key.replace('-', '').replace('_', '').isdigit():
            logger.error(f"NOWPAYMENTS_API_KEY format appears invalid: {clean_api_key[:10]}...")
            logger.error("API key should contain only numbers and dashes")
            logger.error("Expected format: XXXXXXX-XXXXXXX-XXXXXXX-XXXXXXX")
            logger.error("Please check your Railway environment variables")
            logger.error("You may need to regenerate your API key in NOWPayments dashboard")
            logger.error("Current API key: {clean_api_key}")
            return {}
            
        return {
            'x-api-key': clean_api_key,
            'Content-Type': 'application/json'
        }
    
    def create_payment(self, amount_usd, currency_from='USD', currency_to='SOL', order_id=None, order_description=None):
        """Create a new payment request"""
        try:
            # Validate service configuration first
            if not self.validate_configuration():
                logger.error("NOWPayments service configuration is invalid - cannot create payment")
                return None
            
            # Validate API key
            if not self.api_key or not self.api_key.strip():
                logger.error("NOWPAYMENTS_API_KEY is not configured or empty")
                return None
            
            # Clean API key
            clean_api_key = self.api_key.strip()
            logger.info(f"Creating payment with API key: {clean_api_key[:10]}...")
            
            # Validate IPN callback URL
            if not self.ipn_callback_url:
                logger.error("IPN callback URL is not configured - cannot create payment")
                return None
            
            # Validate URL format
            if not self.ipn_callback_url.startswith('http'):
                logger.error(f"Invalid IPN callback URL format: {self.ipn_callback_url}")
                return None
            
            # Validate URL is accessible
            if not self.ipn_callback_url.startswith('https://meridianassetlogistics.com'):
                logger.warning(f"IPN callback URL is not using the expected domain: {self.ipn_callback_url}")
                logger.warning("Expected domain: https://meridianassetlogistics.com")
                logger.warning("This may cause payment creation to fail")
                logger.warning("Please update NOWPAYMENTS_IPN_URL in Railway environment variables")
                logger.warning("The URL should point to your production domain")
            
            payload = {
                'price_amount': float(amount_usd),
                'price_currency': currency_from,
                'pay_currency': currency_to,
                'order_id': order_id,
                'order_description': order_description,
                'ipn_callback_url': self.ipn_callback_url
            }
            
            headers = self._get_headers()
            if not headers:
                logger.error("Failed to get valid headers")
                return None
            
            logger.info(f"Sending request to NOWPayments API: {self.api_url}/payment")
            logger.info(f"Payload: {payload}")
            logger.info(f"Headers: {headers}")
            
            response = requests.post(
                f"{self.api_url}/payment",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            logger.info(f"NOWPayments API response status: {response.status_code}")
            logger.info(f"NOWPayments API response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Payment created successfully: {data.get('payment_id')}")
                
                # Validate required fields in response
                required_fields = ['payment_id', 'pay_address']
                missing_fields = [field for field in required_fields if not data.get(field)]
                
                if missing_fields:
                    logger.error(f"NOWPayments response missing required fields: {missing_fields}")
                    logger.error(f"Full response: {data}")
                    return None
                
                # Log successful payment creation details
                logger.info(f"Payment ID: {data.get('payment_id')}")
                logger.info(f"Payment Address: {data.get('pay_address')}")
                logger.info(f"Crypto Amount: {data.get('pay_amount')}")
                logger.info(f"Crypto Currency: {data.get('pay_currency')}")
                
                # Additional validation for required fields
                if not data.get('payment_id'):
                    logger.error("Payment ID is missing from response")
                    logger.error("This field is required for payment processing")
                    logger.error(f"Response data: {data}")
                    logger.error("Please check NOWPayments API response format")
                    return None
                
                if not data.get('pay_address'):
                    logger.error("Payment address is missing from response")
                    logger.error("This field is required for user payment instructions")
                    logger.error(f"Response data: {data}")
                    logger.error("Please check NOWPayments API response format")
                    return None
                
                logger.info("✅ Payment creation successful - all required fields present")
                logger.info(f"Payment will be processed with ID: {data.get('payment_id')}")
                logger.info(f"User will pay to address: {data.get('pay_address')}")
                return data
            else:
                logger.error(f"Failed to create payment: {response.status_code} - {response.text}")
                # Try to parse error response for better debugging
                try:
                    error_data = response.json()
                    error_msg = error_data.get('message', 'Unknown error')
                    error_code = error_data.get('code', 'Unknown code')
                    logger.error(f"NOWPayments API error: {error_msg} (Code: {error_code})")
                    
                    # Handle specific error codes
                    if error_code == 'INVALID_REQUEST_PARAMS':
                        logger.error("Invalid request parameters - check payload structure")
                        logger.error(f"Current payload: {payload}")
                        logger.error("Common issues: invalid currency codes, missing required fields")
                        logger.error("Trying to create payment with minimal required parameters")
                        logger.error("Please check NOWPayments API documentation for required parameters")
                    elif error_code == 'API_KEY_INVALID':
                        logger.error("API key is invalid or expired")
                        logger.error("Please check your NOWPayments API key in Railway environment variables")
                        logger.error("You may need to regenerate your API key in NOWPayments dashboard")
                        logger.error("Current API key format: {clean_api_key[:10]}...")
                    elif error_code == 'IPN_CALLBACK_URL_INVALID':
                        logger.error("IPN callback URL is invalid")
                        logger.error(f"Current IPN URL: {self.ipn_callback_url}")
                        logger.error("Please check NOWPAYMENTS_IPN_URL in Railway environment variables")
                        logger.error("URL should be: https://meridianassetlogistics.com/investments/api/payments/ipn/")
                        logger.error("Make sure the URL is accessible and properly formatted")
                    elif error_code == 'PAYMENT_CREATION_FAILED':
                        logger.error("Payment creation failed on NOWPayments side")
                        logger.error("This may be a temporary issue with NOWPayments service")
                        logger.error("Please try again in a few minutes")
                        logger.error("If the issue persists, contact NOWPayments support")
                    else:
                        logger.error(f"Unknown error code: {error_code}")
                        logger.error("Please check NOWPayments API documentation for this error code")
                        logger.error("You may need to contact NOWPayments support")
                        logger.error("Error message: {error_msg}")
                    
                except:
                    logger.error(f"Could not parse error response: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating payment: {str(e)}")
            return None
    
    def get_payment_status(self, payment_id):
        """Get payment status from NOWPayments"""
        try:
            response = requests.get(
                f"{self.api_url}/payment/{payment_id}",
                headers=self._get_headers(),
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get payment status: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting payment status: {str(e)}")
            return None
    
    def get_payment_url(self, payment_id):
        """Get payment URL for a specific payment"""
        try:
            return f"https://nowpayments.io/payment/?iid={payment_id}"
        except Exception as e:
            logger.error(f"Error generating payment URL: {str(e)}")
            return None
    
    def verify_ipn_signature(self, payload, signature):
        """Verify IPN signature to ensure webhook authenticity"""
        try:
            if not self.ipn_secret:
                logger.error("IPN secret not configured")
                return False
            
            # Create expected signature
            expected_signature = hmac.new(
                self.ipn_secret.encode('utf-8'),
                payload.encode('utf-8'),
                hashlib.sha512
            ).hexdigest()
            
            # Compare signatures
            is_valid = hmac.compare_digest(signature, expected_signature)
            
            if is_valid:
                logger.info("IPN signature verified successfully")
            else:
                logger.warning("IPN signature verification failed")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"Error verifying IPN signature: {str(e)}")
            return False
    
    def process_ipn_data(self, ipn_data):
        """Process IPN data and update payment status"""
        try:
            payment_id = ipn_data.get('payment_id')
            payment_status = ipn_data.get('payment_status')
            
            if not payment_id or not payment_status:
                logger.error("Invalid IPN data: missing payment_id or payment_status")
                return False
            
            # Try to find payment in PaymentTransaction first (membership payments)
            from .models import PaymentTransaction, InvestmentTransaction
            
            try:
                transaction = PaymentTransaction.objects.get(
                    nowpayments_payment_id=payment_id
                )
                
                # Update status
                transaction.payment_status = payment_status
                transaction.ipn_data = ipn_data
                transaction.signature_verified = True
                
                # Set paid_at if payment is confirmed
                if payment_status in ['confirmed', 'finished']:
                    transaction.paid_at = timezone.now()
                    
                    # If this is a membership payment, activate it
                    if transaction.payment_type == 'membership':
                        self._activate_membership(transaction)
                
                transaction.save()
                logger.info(f"Membership payment {payment_id} status updated to {payment_status}")
                return True
                
            except PaymentTransaction.DoesNotExist:
                # Try to find investment transaction
                try:
                    investment_transaction = InvestmentTransaction.objects.get(
                        nowpayments_payment_id=payment_id
                    )
                    
                    # Update investment transaction status
                    if payment_status in ['confirmed', 'finished']:
                        investment_transaction.payment_status = 'completed'
                        investment_transaction.completed_at = timezone.now()
                        investment_transaction.nowpayments_payment_status = payment_status
                    elif payment_status in ['failed', 'expired']:
                        investment_transaction.payment_status = 'failed'
                        investment_transaction.nowpayments_payment_status = payment_status
                    else:
                        investment_transaction.nowpayments_payment_status = payment_status
                    
                    investment_transaction.save()
                    logger.info(f"Investment transaction {payment_id} status updated to {payment_status}")
                    return True
                    
                except InvestmentTransaction.DoesNotExist:
                    logger.error(f"Payment {payment_id} not found in any transaction model")
                    return False
                    
        except Exception as e:
            logger.error(f"Error processing IPN data: {str(e)}")
            return False
    
    def process_webhook(self, body, signature):
        """Process webhook data from NOWPayments"""
        try:
            # Verify signature
            if not self.verify_ipn_signature(body, signature):
                logger.error("Webhook signature verification failed")
                return False
            
            # Parse JSON data
            try:
                webhook_data = json.loads(body)
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in webhook: {e}")
                return False
            
            # Process the webhook data
            return self.process_ipn_data(webhook_data)
            
        except Exception as e:
            logger.error(f"Error processing webhook: {str(e)}")
            return False
    
    def _activate_membership(self, transaction):
        """Activate membership when payment is confirmed"""
        try:
            from .models import MembershipPayment
            
            # Create or update membership
            membership, created = MembershipPayment.objects.get_or_create(
                payment_transaction=transaction,
                defaults={
                    'user': transaction.user,
                    'membership_type': 'Standard',
                    'membership_duration': '1 Year',
                    'is_active': True,
                    'activated_at': timezone.now(),
                    'expires_at': timezone.now() + timedelta(days=365)
                }
            )
            
            if not created:
                # Update existing membership
                membership.is_active = True
                membership.activated_at = timezone.now()
                membership.expires_at = timezone.now() + timedelta(days=365)
                membership.save()
            
            logger.info(f"Membership activated for user {transaction.user.username}")
            
        except Exception as e:
            logger.error(f"Error activating membership: {str(e)}")
    
    def create_membership_payment(self, user, amount_usd=1270.00):
        """Create a membership payment request"""
        try:
            # Create payment transaction record
            from .models import PaymentTransaction
            
            transaction = PaymentTransaction.objects.create(
                payment_id=f"MEM_{user.id}_{int(timezone.now().timestamp())}",
                payment_type='membership',
                amount_usd=amount_usd,
                user=user,
                payment_status='pending'
            )
            
            # Create NOWPayments payment
            payment_data = self.create_payment(
                amount_usd=amount_usd,
                order_id=transaction.payment_id,
                order_description=f"Membership Fee - {user.username}"
            )
            
            if payment_data:
                # Update transaction with NOWPayments data
                transaction.nowpayments_payment_id = payment_data.get('payment_id')
                transaction.payment_address = payment_data.get('pay_address')
                transaction.amount_crypto = payment_data.get('pay_amount')
                transaction.crypto_currency = payment_data.get('pay_currency')
                transaction.save()
                
                logger.info(f"Membership payment created: {transaction.payment_id}")
                return transaction
            else:
                # Delete transaction if NOWPayments failed
                transaction.delete()
                logger.error("Failed to create NOWPayments payment - check IPN callback URL configuration")
                return None
                
        except Exception as e:
            logger.error(f"Error creating membership payment: {str(e)}")
            return None

    def create_investment_payment(self, user, amount_usd, investment_type, item, transaction):
        """Create an investment payment request"""
        try:
            # Validate service configuration
            if not self.api_key or not self.api_key.strip():
                logger.error("NOWPayments API key not configured")
                return {'success': False, 'error': 'Payment service not configured'}
            
            if not self.ipn_callback_url:
                logger.error("NOWPayments IPN callback URL not configured")
                return {'success': False, 'error': 'Payment callback URL not configured'}
            
            logger.info(f"Creating investment payment for {user.username}: ${amount_usd} for {item.name}")
            
            # Create NOWPayments payment
            payment_data = self.create_payment(
                amount_usd=amount_usd,
                order_id=f"INV_{transaction.id}_{int(timezone.now().timestamp())}",
                order_description=f"{investment_type.title()} - {item.name} - {user.username}"
            )
            
            if payment_data:
                # Update transaction with NOWPayments data
                transaction.nowpayments_payment_id = payment_data.get('payment_id')
                transaction.payment_address = payment_data.get('pay_address')
                transaction.crypto_amount = payment_data.get('pay_amount')
                transaction.crypto_currency = payment_data.get('pay_currency')
                transaction.save()
                
                logger.info(f"Investment payment created successfully: {transaction.id}")
                logger.info(f"Payment data: {payment_data}")
                
                # Check if we have the minimum required data
                if not payment_data.get('payment_id'):
                    logger.error("NOWPayments response missing payment_id")
                    return {'success': False, 'error': 'Invalid payment response - missing payment ID'}
                
                return {
                    'success': True,
                    'nowpayments_payment_id': payment_data.get('payment_id'),
                    'payment_address': payment_data.get('pay_address'),
                    'crypto_amount': payment_data.get('pay_amount'),
                    'crypto_currency': payment_data.get('pay_currency'),
                    'payment_url': f"https://nowpayments.io/payment/?iid={payment_data.get('payment_id')}"
                }
            else:
                logger.error("NOWPayments API returned no payment data")
                return {'success': False, 'error': 'Payment service returned no data'}
                
        except Exception as e:
            logger.error(f"Error creating investment payment: {str(e)}")
            return {'success': False, 'error': f'Service error: {str(e)}'}

    def validate_configuration(self):
        """Validate that the NOWPayments service is properly configured"""
        errors = []
        
        if not self.api_key or not self.api_key.strip():
            errors.append("NOWPAYMENTS_API_KEY is missing or empty")
        elif not self.api_key.replace('-', '').replace('_', '').isdigit():
            errors.append("NOWPAYMENTS_API_KEY format is invalid")
            
        if not self.ipn_secret or not self.ipn_secret.strip():
            errors.append("NOWPAYMENTS_IPN_SECRET is missing or empty")
            
        if not self.ipn_callback_url or not self.ipn_callback_url.strip():
            errors.append("NOWPAYMENTS_IPN_URL is missing or empty")
        elif not self.ipn_callback_url.startswith('http'):
            errors.append("NOWPAYMENTS_IPN_URL format is invalid")
            
        if errors:
            logger.error("NOWPayments service configuration errors:")
            for error in errors:
                logger.error(f"  - {error}")
            return False
            
        logger.info("✅ NOWPayments service configuration is valid")
        return True

# Global instance
nowpayments_service = NOWPaymentsService()
