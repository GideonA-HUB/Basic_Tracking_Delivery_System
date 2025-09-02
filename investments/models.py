from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal
import uuid


class InvestmentCategory(models.Model):
    """Categories for investment items"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='fas fa-chart-line')
    color = models.CharField(max_length=7, default='#1e40af')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Investment Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class InvestmentItem(models.Model):
    """Investment items that can be bought or invested in"""
    
    INVESTMENT_TYPE_CHOICES = [
        ('investment_only', 'Investment Only'),
        ('delivery_only', 'Delivery Only'),
        ('both', 'Investment & Delivery'),
    ]
    
    category = models.ForeignKey(InvestmentCategory, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=200)
    description = models.TextField()
    short_description = models.CharField(max_length=300, blank=True)
    
    # Symbol for live price updates (links to RealTimePriceFeed)
    symbol = models.CharField(max_length=20, blank=True, null=True, help_text="Symbol for live price updates (e.g., BTC, ETH, XAU)")
    
    # Investment details
    current_price_usd = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    price_change_24h = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    price_change_percentage_24h = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    
    # Item specifications
    weight = models.DecimalField(max_digits=8, decimal_places=3, blank=True, null=True)
    purity = models.CharField(max_length=50, blank=True, null=True)  # For precious metals
    dimensions = models.CharField(max_length=100, blank=True, null=True)
    origin = models.CharField(max_length=100, blank=True, null=True)
    
    # Investment options
    investment_type = models.CharField(max_length=20, choices=INVESTMENT_TYPE_CHOICES, default='both')
    minimum_investment = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    maximum_investment = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    
    # Availability
    total_available = models.DecimalField(max_digits=12, decimal_places=3, blank=True, null=True)
    currently_available = models.DecimalField(max_digits=12, decimal_places=3, blank=True, null=True)
    
    # Images and media
    main_image_url = models.URLField(max_length=500, blank=True, null=True, help_text="Enter the URL of the main image")
    additional_image_urls = models.JSONField(default=list, blank=True, help_text="Enter URLs of additional images as a list")
    
    # Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_price_update = models.DateTimeField(auto_now=True, help_text="Last time the price was updated")
    
    class Meta:
        ordering = ['-is_featured', '-created_at']
    
    def __str__(self):
        return f"{self.name} - ${self.current_price_usd}"
    
    @property
    def is_available_for_investment(self):
        return self.investment_type in ['investment_only', 'both'] and self.is_active
    
    @property
    def is_available_for_delivery(self):
        return self.investment_type in ['delivery_only', 'both'] and self.is_active
    
    def update_price(self, new_price, price_change=None, price_change_percentage=None):
        """Update the current price and calculate changes"""
        if price_change is None:
            price_change = new_price - self.current_price_usd
        if price_change_percentage is None:
            price_change_percentage = (price_change / self.current_price_usd) * 100
        
        self.current_price_usd = new_price
        self.price_change_24h = price_change
        self.price_change_percentage_24h = price_change_percentage
        self.save()
        
        # Create price history record
        PriceHistory.objects.create(
            item=self,
            price=new_price,
            change_amount=price_change,
            change_percentage=price_change_percentage,
            timestamp=timezone.now()
        )
    
    def get_investment_type_display(self):
        """Get display text for investment type"""
        type_map = {
            'investment_only': 'Investment Only',
            'delivery_only': 'Delivery Only',
            'both': 'Investment & Delivery'
        }
        return type_map.get(self.investment_type, 'Unknown')


class PriceHistory(models.Model):
    """Historical price data for investment items"""
    item = models.ForeignKey(InvestmentItem, on_delete=models.CASCADE, related_name='price_history')
    price = models.DecimalField(max_digits=12, decimal_places=2)
    change_amount = models.DecimalField(max_digits=8, decimal_places=2)
    change_percentage = models.DecimalField(max_digits=6, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = 'Price History'
    
    def __str__(self):
        return f"{self.item.name} - ${self.price} at {self.timestamp}"
    
    @property
    def get_price_change_class(self):
        """Get CSS class for price change styling"""
        if self.change_percentage > 0:
            return 'text-green-600 dark:text-green-400'
        elif self.change_percentage < 0:
            return 'text-red-600 dark:text-red-400'
        else:
            return 'text-gray-600 dark:text-gray-400'


class UserInvestment(models.Model):
    """User's investment in a specific item"""
    
    INVESTMENT_STATUS_CHOICES = [
        ('active', 'Active'),
        ('sold', 'Sold'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='investments')
    item = models.ForeignKey(InvestmentItem, on_delete=models.CASCADE, related_name='user_investments')
    
    # Investment details
    investment_amount_usd = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    quantity = models.DecimalField(max_digits=12, decimal_places=6, validators=[MinValueValidator(Decimal('0.000001'))])
    purchase_price_per_unit = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Current value
    current_value_usd = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_return_usd = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_return_percentage = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    # Investment type
    investment_type = models.CharField(max_length=20, choices=[
        ('hold', 'Hold for Investment'),
        ('delivery', 'Buy for Delivery'),
    ])
    
    # Status
    status = models.CharField(max_length=20, choices=INVESTMENT_STATUS_CHOICES, default='active')
    
    # Timestamps
    purchased_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sold_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-purchased_at']
        verbose_name_plural = 'User Investments'
    
    def __str__(self):
        return f"{self.user.username} - {self.item.name} - ${self.investment_amount_usd}"
    
    def save(self, *args, **kwargs):
        # Calculate current value and returns
        self.current_value_usd = self.quantity * self.item.current_price_usd
        self.total_return_usd = self.current_value_usd - self.investment_amount_usd
        if self.investment_amount_usd > 0:
            self.total_return_percentage = (self.total_return_usd / self.investment_amount_usd) * 100
        super().save(*args, **kwargs)
    
    @property
    def is_profitable(self):
        return self.total_return_usd > 0
    
    @property
    def days_held(self):
        from django.utils import timezone
        return (timezone.now() - self.purchased_at).days
    
    @property
    def total_return_display(self):
        """Get formatted total return display"""
        if self.total_return_usd >= 0:
            return f"+${self.total_return_usd}"
        else:
            return f"-${abs(self.total_return_usd)}"
    
    @property
    def total_return_percentage_display(self):
        """Get formatted total return percentage display"""
        if self.total_return_percentage >= 0:
            return f"+{self.total_return_percentage:.2f}%"
        else:
            return f"{self.total_return_percentage:.2f}%"


class InvestmentTransaction(models.Model):
    """Transactions related to investments"""
    
    TRANSACTION_TYPE_CHOICES = [
        ('purchase', 'Purchase'),
        ('sale', 'Sale'),
        ('delivery', 'Delivery'),
        ('refund', 'Refund'),
    ]
    
    TRANSACTION_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    transaction_id = models.UUIDField(default=uuid.uuid4, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='investment_transactions')
    investment = models.ForeignKey(UserInvestment, on_delete=models.CASCADE, related_name='transactions', blank=True, null=True)
    item = models.ForeignKey(InvestmentItem, on_delete=models.CASCADE, related_name='transactions')
    
    # Transaction details
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    amount_usd = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.DecimalField(max_digits=12, decimal_places=6, blank=True, null=True)
    price_per_unit = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Payment details
    payment_method = models.CharField(max_length=50, default='nowpayments')
    payment_reference = models.CharField(max_length=200, blank=True, null=True)
    payment_status = models.CharField(max_length=20, choices=TRANSACTION_STATUS_CHOICES, default='pending')
    
    # NOWPayments specific fields
    nowpayments_payment_id = models.CharField(max_length=200, blank=True, null=True)
    nowpayments_payment_status = models.CharField(max_length=50, blank=True, null=True)
    crypto_amount = models.DecimalField(max_digits=20, decimal_places=8, blank=True, null=True)
    crypto_currency = models.CharField(max_length=10, blank=True, null=True)
    
    # Metadata
    description = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Investment Transactions'
    
    def __str__(self):
        return f"{self.transaction_id} - {self.user.username} - {self.transaction_type} - ${self.amount_usd}"
    
    @property
    def is_completed(self):
        return self.payment_status == 'completed'
    
    @property
    def is_pending(self):
        return self.payment_status == 'pending'
    
    @property
    def status(self):
        """Alias for payment_status for template compatibility"""
        return self.payment_status
    
    @property
    def get_status_display(self):
        """Get status display for template compatibility"""
        return self.get_payment_status_display()


class InvestmentPortfolio(models.Model):
    """User's overall investment portfolio summary"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='investment_portfolio')
    
    # Portfolio summary
    total_invested = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    current_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_return = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_return_percentage = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    # Active investments count
    active_investments_count = models.PositiveIntegerField(default=0)
    total_investments_count = models.PositiveIntegerField(default=0)
    
    # Last updated
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Investment Portfolios'
    
    def __str__(self):
        return f"{self.user.username}'s Portfolio - ${self.current_value}"
    
    def update_portfolio_summary(self):
        """Update portfolio summary based on current investments"""
        active_investments = self.user.investments.filter(status='active')
        
        self.total_invested = sum(inv.investment_amount_usd for inv in active_investments)
        self.current_value = sum(inv.current_value_usd for inv in active_investments)
        self.total_return = self.current_value - self.total_invested
        
        if self.total_invested > 0:
            self.total_return_percentage = (self.total_return / self.total_invested) * 100
        
        self.active_investments_count = active_investments.count()
        self.total_investments_count = self.user.investments.count()
        self.save()
    
    @property
    def is_profitable(self):
        return self.total_return > 0
    
    @property
    def total_return_display(self):
        """Get formatted total return display"""
        if self.total_return >= 0:
            return f"+${self.total_return}"
        else:
            return f"-${abs(self.total_return)}"
    
    @property
    def total_return_percentage_display(self):
        """Get formatted total return percentage display"""
        if self.total_return_percentage >= 0:
            return f"+{self.total_return_percentage:.2f}%"
        else:
            return f"{self.total_return_percentage:.2f}%"


class AutoInvestmentPlan(models.Model):
    """Auto-investment plans for users"""
    
    PLAN_FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('biweekly', 'Bi-weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]
    
    PLAN_STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='auto_investment_plans')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Investment details
    investment_amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    frequency = models.CharField(max_length=20, choices=PLAN_FREQUENCY_CHOICES, default='monthly')
    target_asset = models.ForeignKey(InvestmentItem, on_delete=models.CASCADE, related_name='auto_investment_plans')
    
    # Schedule
    start_date = models.DateField()
    next_investment_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    
    # Status
    status = models.CharField(max_length=20, choices=PLAN_STATUS_CHOICES, default='active')
    total_invested = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    investments_count = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_investment_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Auto Investment Plans'
    
    def __str__(self):
        return f"{self.user.username} - {self.name} ({self.frequency})"
    
    def calculate_next_investment_date(self):
        """Calculate the next investment date based on frequency"""
        from datetime import timedelta
        from dateutil.relativedelta import relativedelta
        
        if self.last_investment_at:
            base_date = self.last_investment_at.date()
        else:
            base_date = self.start_date
        
        if self.frequency == 'daily':
            return base_date + timedelta(days=1)
        elif self.frequency == 'weekly':
            return base_date + timedelta(weeks=1)
        elif self.frequency == 'biweekly':
            return base_date + timedelta(weeks=2)
        elif self.frequency == 'monthly':
            return base_date + relativedelta(months=1)
        elif self.frequency == 'quarterly':
            return base_date + relativedelta(months=3)
        elif self.frequency == 'yearly':
            return base_date + relativedelta(years=1)
        
        return base_date
    
    def is_due_for_investment(self):
        """Check if the plan is due for investment"""
        from django.utils import timezone
        return self.next_investment_date <= timezone.now().date() and self.status == 'active'


class RealTimePriceFeed(models.Model):
    """Real-time price feeds for various assets"""
    
    ASSET_TYPE_CHOICES = [
        ('gold', 'Gold'),
        ('silver', 'Silver'),
        ('platinum', 'Platinum'),
        ('palladium', 'Palladium'),
        ('diamond', 'Diamond'),
        ('crypto', 'Cryptocurrency'),
        ('real_estate', 'Real Estate'),
        ('art', 'Art'),
        ('other', 'Other'),
    ]
    
    CURRENCY_CHOICES = [
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
        ('GBP', 'British Pound'),
        ('NGN', 'Nigerian Naira'),
        ('BTC', 'Bitcoin'),
        ('ETH', 'Ethereum'),
    ]
    
    name = models.CharField(max_length=200)
    asset_type = models.CharField(max_length=20, choices=ASSET_TYPE_CHOICES)
    symbol = models.CharField(max_length=20, blank=True)
    
    # Current price
    current_price = models.DecimalField(max_digits=20, decimal_places=8)
    base_currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
    
    # Price changes
    price_change_24h = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    price_change_percentage_24h = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    price_change_7d = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    price_change_percentage_7d = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    # Market data
    market_cap = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    volume_24h = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    
    # API source
    api_source = models.CharField(max_length=100, blank=True)
    api_url = models.URLField(blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['asset_type', 'name']
        verbose_name_plural = 'Real Time Price Feeds'
    
    def __str__(self):
        return f"{self.name} - {self.get_asset_type_display()} ({self.base_currency})"
    
    def update_price(self, new_price, price_change_24h=None, price_change_percentage_24h=None):
        """Update the current price and calculate changes"""
        if price_change_24h is None:
            price_change_24h = new_price - self.current_price
        if price_change_percentage_24h is None and self.current_price > 0:
            price_change_percentage_24h = (price_change_24h / self.current_price) * 100
        
        self.current_price = new_price
        self.price_change_24h = price_change_24h
        self.price_change_percentage_24h = price_change_percentage_24h or 0
        self.save()
        
        # Create price history record
        RealTimePriceHistory.objects.create(
            price_feed=self,
            price=new_price,
            change_amount=price_change_24h,
            change_percentage=price_change_percentage_24h or 0,
            timestamp=timezone.now()
        )


class RealTimePriceHistory(models.Model):
    """Historical real-time price data"""
    price_feed = models.ForeignKey(RealTimePriceFeed, on_delete=models.CASCADE, related_name='price_history')
    price = models.DecimalField(max_digits=20, decimal_places=8)
    change_amount = models.DecimalField(max_digits=20, decimal_places=8)
    change_percentage = models.DecimalField(max_digits=8, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = 'Real Time Price History'
    
    def __str__(self):
        return f"{self.price_feed.name} - {self.price} at {self.timestamp}"


class CurrencyConversion(models.Model):
    """Currency conversion rates"""
    
    CURRENCY_CHOICES = [
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
        ('GBP', 'British Pound'),
        ('NGN', 'Nigerian Naira'),
        ('BTC', 'Bitcoin'),
        ('ETH', 'Ethereum'),
    ]
    
    from_currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES)
    to_currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES)
    exchange_rate = models.DecimalField(max_digits=20, decimal_places=8)
    
    # API source
    api_source = models.CharField(max_length=100, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['from_currency', 'to_currency']
        ordering = ['from_currency', 'to_currency']
        verbose_name_plural = 'Currency Conversions'
    
    def __str__(self):
        return f"{self.from_currency} to {self.to_currency}: {self.exchange_rate}"
    
    @classmethod
    def get_conversion_rate(cls, from_currency, to_currency):
        """Get conversion rate between two currencies"""
        if from_currency == to_currency:
            return Decimal('1.0')
        
        try:
            conversion = cls.objects.get(from_currency=from_currency, to_currency=to_currency)
            return conversion.exchange_rate
        except cls.DoesNotExist:
            # Try reverse conversion
            try:
                conversion = cls.objects.get(from_currency=to_currency, to_currency=from_currency)
                return Decimal('1.0') / conversion.exchange_rate
            except cls.DoesNotExist:
                return None


class CustomerCashoutRequest(models.Model):
    """Customer cashout requests that need customer care approval"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cashout_requests')
    
    # Request details
    amount_usd = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    requested_currency = models.CharField(max_length=3, choices=CurrencyConversion.CURRENCY_CHOICES, default='USD')
    bank_account_details = models.TextField(blank=True)
    reason = models.TextField(blank=True)
    
    # Status and approval
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_cashouts')
    approved_at = models.DateTimeField(blank=True, null=True)
    rejection_reason = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Customer Cashout Requests'
    
    def __str__(self):
        return f"{self.user.username} - ${self.amount_usd} - {self.get_status_display()}"
    
    @property
    def can_be_approved(self):
        """Check if the cashout request can be approved"""
        return self.status == 'pending'
    
    @property
    def can_be_rejected(self):
        """Check if the cashout request can be rejected"""
        return self.status == 'pending'
    
    def approve(self, approved_by_user):
        """Approve the cashout request"""
        if self.can_be_approved:
            self.status = 'approved'
            self.approved_by = approved_by_user
            self.approved_at = timezone.now()
            self.save()
            return True
        return False
    
    def reject(self, rejection_reason):
        """Reject the cashout request"""
        if self.can_be_rejected:
            self.status = 'rejected'
            self.rejection_reason = rejection_reason
            self.save()
            return True
        return False
