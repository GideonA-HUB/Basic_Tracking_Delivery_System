from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
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
    main_image = models.ImageField(upload_to='investment_items/', blank=True, null=True)
    additional_images = models.JSONField(default=list, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
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
            change_percentage=price_change_percentage
        )


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
