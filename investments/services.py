import requests
import json
import hashlib
import hmac
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
from .models import InvestmentTransaction
import logging

logger = logging.getLogger(__name__)


class NOWPaymentsService:
    """Service for integrating with NOWPayments API"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'NOWPAYMENTS_API_KEY', '')
        self.api_secret = getattr(settings, 'NOWPAYMENTS_API_SECRET', '')
        self.base_url = 'https://api.nowpayments.io/v1'
        self.webhook_secret = getattr(settings, 'NOWPAYMENTS_WEBHOOK_SECRET', '')
        
        if not self.api_key:
            logger.warning("NOWPayments API key not configured")
    
    def _make_request(self, endpoint, method='GET', data=None, headers=None):
        """Make HTTP request to NOWPayments API"""
        url = f"{self.base_url}/{endpoint}"
        
        if headers is None:
            headers = {}
        
        headers.update({
            'x-api-key': self.api_key,
            'Content-Type': 'application/json'
        })
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, params=data)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"NOWPayments API request failed: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse NOWPayments API response: {e}")
            return None
    
    def create_payment(self, transaction, crypto_currency='BTC'):
        """Create a new payment request"""
        try:
            payment_data = {
                'price_amount': float(transaction.amount_usd),
                'price_currency': 'usd',
                'pay_currency': crypto_currency.lower(),
                'ipn_callback_url': f"{settings.SITE_URL}/investments/webhook/",
                'order_id': str(transaction.transaction_id),
                'order_description': f"Investment: {transaction.item.name}",
                'is_fixed_rate': False,
                'is_fractional': True
            }
            
            response = self._make_request('payment', method='POST', data=payment_data)
            
            if response and response.get('payment_id'):
                # Update transaction with NOWPayments details
                transaction.nowpayments_payment_id = response['payment_id']
                transaction.nowpayments_payment_status = response.get('payment_status', 'waiting')
                transaction.crypto_currency = crypto_currency.upper()
                transaction.save()
                
                return response
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to create NOWPayments payment: {e}")
            return None
    
    def get_payment_status(self, payment_id):
        """Get current payment status"""
        return self._make_request(f'payment/{payment_id}')
    
    def get_payment_status_minimal(self, payment_id):
        """Get minimal payment status info"""
        return self._make_request(f'payment/{payment_id}/status')
    
    def get_estimated_price(self, amount_usd, crypto_currency='BTC'):
        """Get estimated crypto amount for USD value"""
        data = {
            'amount': float(amount_usd),
            'currency_from': 'usd',
            'currency_to': crypto_currency.lower()
        }
        
        return self._make_request('estimate', data=data)
    
    def get_available_currencies(self):
        """Get list of available cryptocurrencies"""
        return self._make_request('currencies')
    
    def get_minimum_payment_amount(self, crypto_currency='BTC'):
        """Get minimum payment amount for a cryptocurrency"""
        return self._make_request(f'min-amount/{crypto_currency.lower()}')
    
    def verify_webhook_signature(self, payload, signature):
        """Verify webhook signature for security"""
        if not self.webhook_secret:
            logger.warning("Webhook secret not configured")
            return False
        
        expected_signature = hmac.new(
            self.webhook_secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()
        
        return hmac.compare_digest(expected_signature, signature)
    
    def process_webhook(self, payload, signature):
        """Process incoming webhook from NOWPayments"""
        try:
            if not self.verify_webhook_signature(payload, signature):
                logger.error("Invalid webhook signature")
                return False
            
            data = json.loads(payload)
            payment_id = data.get('payment_id')
            payment_status = data.get('payment_status')
            
            if not payment_id or not payment_status:
                logger.error("Invalid webhook payload")
                return False
            
            # Find and update transaction
            try:
                transaction = InvestmentTransaction.objects.get(
                    nowpayments_payment_id=payment_id
                )
            except InvestmentTransaction.DoesNotExist:
                logger.error(f"Transaction not found for payment ID: {payment_id}")
                return False
            
            # Update transaction status
            old_status = transaction.payment_status
            transaction.nowpayments_payment_status = payment_status
            
            # Map NOWPayments status to our status
            status_mapping = {
                'waiting': 'pending',
                'confirming': 'processing',
                'confirmed': 'processing',
                'sending': 'processing',
                'partially_paid': 'processing',
                'finished': 'completed',
                'failed': 'failed',
                'expired': 'cancelled',
                'refunded': 'cancelled'
            }
            
            new_status = status_mapping.get(payment_status, 'pending')
            transaction.payment_status = new_status
            
            # Update crypto amount if provided
            if 'pay_amount' in data:
                transaction.crypto_amount = Decimal(str(data['pay_amount']))
            
            # Set completion timestamp if completed
            if new_status == 'completed':
                transaction.completed_at = timezone.now()
                
                # Create user investment if this is a purchase
                if transaction.transaction_type == 'purchase':
                    self._create_user_investment(transaction)
            
            transaction.save()
            
            logger.info(f"Updated transaction {transaction.transaction_id} status: {old_status} -> {new_status}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to process webhook: {e}")
            return False
    
    def _create_user_investment(self, transaction):
        """Create user investment after successful payment"""
        try:
            from .models import UserInvestment
            
            # Calculate quantity based on amount and price
            quantity = transaction.amount_usd / transaction.price_per_unit
            
            # Determine investment type based on transaction description
            investment_type = 'hold'  # Default to hold
            if 'delivery' in transaction.description.lower():
                investment_type = 'delivery'
            
            # Create user investment
            user_investment = UserInvestment.objects.create(
                user=transaction.user,
                item=transaction.item,
                investment_amount_usd=transaction.amount_usd,
                quantity=quantity,
                purchase_price_per_unit=transaction.price_per_unit,
                investment_type=investment_type,
                status='active'
            )
            
            # Link transaction to investment
            transaction.investment = user_investment
            transaction.save()
            
            # Update user's portfolio
            self._update_user_portfolio(transaction.user)
            
            logger.info(f"Created user investment: {user_investment.id}")
            
        except Exception as e:
            logger.error(f"Failed to create user investment: {e}")
    
    def _update_user_portfolio(self, user):
        """Update user's investment portfolio summary"""
        try:
            from .models import InvestmentPortfolio
            
            portfolio, created = InvestmentPortfolio.objects.get_or_create(user=user)
            portfolio.update_portfolio_summary()
            
        except Exception as e:
            logger.error(f"Failed to update user portfolio: {e}")
    
    def get_payment_url(self, payment_id):
        """Get payment URL for user to complete payment"""
        return f"https://nowpayments.io/payment/?iid={payment_id}"
    
    def cancel_payment(self, payment_id):
        """Cancel a pending payment"""
        return self._make_request(f'payment/{payment_id}/cancel', method='POST')
    
    def refund_payment(self, payment_id, amount=None):
        """Refund a completed payment"""
        data = {}
        if amount:
            data['amount'] = float(amount)
        
        return self._make_request(f'payment/{payment_id}/refund', method='POST', data=data)


class InvestmentPriceService:
    """Service for managing investment item prices and updates"""
    
    @staticmethod
    def update_item_price(item, new_price, source='manual'):
        """Update item price and create price history"""
        try:
            old_price = item.current_price_usd
            price_change = new_price - old_price
            
            if old_price > 0:
                price_change_percentage = (price_change / old_price) * 100
            else:
                price_change_percentage = 0
            
            # Update item price
            item.update_price(new_price, price_change, price_change_percentage)
            
            # Update all user investments for this item
            for user_investment in item.user_investments.filter(status='active'):
                user_investment.save()  # This will recalculate current value and returns
            
            # Update user portfolios
            users_to_update = set(user_investment.user for user_investment in item.user_investments.filter(status='active'))
            for user in users_to_update:
                if hasattr(user, 'investment_portfolio'):
                    user.investment_portfolio.update_portfolio_summary()
            
            logger.info(f"Updated price for {item.name}: ${old_price} -> ${new_price}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update item price: {e}")
            return False
    
    @staticmethod
    def get_price_chart_data(item, days=30):
        """Get price chart data for an item"""
        from .models import PriceHistory
        from django.utils import timezone
        
        end_date = timezone.now()
        start_date = end_date - timezone.timedelta(days=days)
        
        price_history = PriceHistory.objects.filter(
            item=item,
            timestamp__gte=start_date,
            timestamp__lte=end_date
        ).order_by('timestamp')
        
        chart_data = {
            'labels': [],
            'prices': [],
            'changes': []
        }
        
        for record in price_history:
            chart_data['labels'].append(record.timestamp.strftime('%Y-%m-%d %H:%M'))
            chart_data['prices'].append(float(record.price))
            chart_data['changes'].append(float(record.change_percentage))
        
        return chart_data


# Global instance
nowpayments_service = NOWPaymentsService()
price_service = InvestmentPriceService()
