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
            
        return {
            'x-api-key': clean_api_key,
            'Content-Type': 'application/json'
        }
    
    def create_payment(self, amount_usd, currency_from='USD', currency_to='SOL', order_id=None, order_description=None):
        """Create a new payment request"""
        try:
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
                
            payload = {
                'price_amount': float(amount_usd),
                'price_currency': currency_from,
                'pay_currency': currency_to,
                'order_id': order_id,
                'order_description': order_description,
                'ipn_callback_url': self.ipn_callback_url,
                'is_fixed_rate': True,
                'is_fixed_pay_currency': True
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
                return data
            else:
                logger.error(f"Failed to create payment: {response.status_code} - {response.text}")
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
                    logger.info(f"Investment payment {payment_id} status updated to {payment_status}")
                    return True
                    
                except InvestmentTransaction.DoesNotExist:
                    logger.warning(f"Payment transaction not found for NOWPayments ID: {payment_id}")
                    return False
                
        except Exception as e:
            logger.error(f"Error processing IPN data: {str(e)}")
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

# Global instance
nowpayments_service = NOWPaymentsService()
