from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal
import uuid

# Import news models
from .news_models import *


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
    price_change_percentage_24h = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
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
    
    def update_price(self, new_price, price_change=None, price_change_percentage=None, volume_24h=None, market_cap=None):
        """Update the current price and calculate changes with movement tracking"""
        old_price = self.current_price_usd
        
        if price_change is None:
            price_change = new_price - old_price
        if price_change_percentage is None:
            price_change_percentage = (price_change / old_price) * 100 if old_price > 0 else 0
        
        # Safety check: Limit percentage to prevent database overflow
        if price_change_percentage > 999999.99:
            price_change_percentage = 999999.99
        elif price_change_percentage < -999999.99:
            price_change_percentage = -999999.99
        
        # Determine movement type
        if price_change > 0:
            movement_type = 'increase'
        elif price_change < 0:
            movement_type = 'decrease'
        else:
            movement_type = 'unchanged'
        
        # Update item price
        self.current_price_usd = new_price
        self.price_change_24h = price_change
        self.price_change_percentage_24h = price_change_percentage
        self.last_price_update = timezone.now()
        self.save()
        
        # Create price history record with movement tracking
        PriceHistory.objects.create(
            item=self,
            price=new_price,
            change_amount=price_change,
            change_percentage=price_change_percentage,
            movement_type=movement_type,
            volume_24h=volume_24h,
            market_cap=market_cap,
            timestamp=timezone.now()
        )
        
        # Update movement statistics
        try:
            stats = PriceMovementStats.get_or_create_today_stats(self)
            stats.increment_movement(movement_type)
            
            # Update 24h price statistics
            if not stats.highest_price_24h or new_price > stats.highest_price_24h:
                stats.highest_price_24h = new_price
            if not stats.lowest_price_24h or new_price < stats.lowest_price_24h:
                stats.lowest_price_24h = new_price
            
            # Calculate average price for 24h
            from django.db.models import Avg
            from datetime import timedelta
            end_time = timezone.now()
            start_time = end_time - timedelta(hours=24)
            
            avg_price = PriceHistory.objects.filter(
                item=self,
                timestamp__range=(start_time, end_time)
            ).aggregate(avg=Avg('price'))['avg']
            
            if avg_price:
                stats.average_price_24h = avg_price
            
            stats.save()
            
        except Exception as e:
            # Log error but don't fail the price update
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error updating movement stats for {self.name}: {e}")
    
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
    change_percentage = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Price movement tracking
    movement_type = models.CharField(max_length=10, choices=[
        ('increase', 'Increase'),
        ('decrease', 'Decrease'),
        ('unchanged', 'Unchanged')
    ], default='unchanged')
    
    # Volume and market data
    volume_24h = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    market_cap = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = 'Price History'
        indexes = [
            models.Index(fields=['item', 'timestamp']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['movement_type']),
        ]
    
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
    
    @classmethod
    def get_price_movements_count(cls, item, days=1):
        """Get count of price movements for an item"""
        from django.utils import timezone
        from datetime import timedelta
        
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        movements = cls.objects.filter(
            item=item,
            timestamp__range=(start_date, end_date)
        ).values('movement_type').annotate(count=models.Count('id'))
        
        return {movement['movement_type']: movement['count'] for movement in movements}
    
    @classmethod
    def get_daily_average(cls, item, days=7):
        """Get daily average price for an item"""
        from django.utils import timezone
        from datetime import timedelta
        from django.db.models import Avg
        
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        return cls.objects.filter(
            item=item,
            timestamp__range=(start_date, end_date)
        ).aggregate(avg_price=Avg('price'))['avg_price']
    
    @classmethod
    def get_price_range(cls, item, days=30):
        """Get highest and lowest prices for an item"""
        from django.utils import timezone
        from datetime import timedelta
        from django.db.models import Max, Min
        
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        return cls.objects.filter(
            item=item,
            timestamp__range=(start_date, end_date)
        ).aggregate(
            highest=Max('price'),
            lowest=Min('price')
        )


class PriceMovementStats(models.Model):
    """Statistics for price movements and counting"""
    item = models.ForeignKey(InvestmentItem, on_delete=models.CASCADE, related_name='movement_stats')
    
    # Daily counters
    increases_today = models.PositiveIntegerField(default=0)
    decreases_today = models.PositiveIntegerField(default=0)
    unchanged_today = models.PositiveIntegerField(default=0)
    
    # Weekly counters
    increases_this_week = models.PositiveIntegerField(default=0)
    decreases_this_week = models.PositiveIntegerField(default=0)
    unchanged_this_week = models.PositiveIntegerField(default=0)
    
    # Monthly counters
    increases_this_month = models.PositiveIntegerField(default=0)
    decreases_this_month = models.PositiveIntegerField(default=0)
    unchanged_this_month = models.PositiveIntegerField(default=0)
    
    # Price statistics
    highest_price_24h = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    lowest_price_24h = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    average_price_24h = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    
    # Last update
    last_updated = models.DateTimeField(auto_now=True)
    date = models.DateField(auto_now_add=True)
    
    class Meta:
        unique_together = ['item', 'date']
        ordering = ['-date']
        verbose_name_plural = 'Price Movement Statistics'
    
    def __str__(self):
        return f"{self.item.name} - {self.date} - ↑{self.increases_today} ↓{self.decreases_today}"
    
    @classmethod
    def get_or_create_today_stats(cls, item):
        """Get or create today's stats for an item"""
        from django.utils import timezone
        
        today = timezone.now().date()
        stats, created = cls.objects.get_or_create(
            item=item,
            date=today,
            defaults={
                'increases_today': 0,
                'decreases_today': 0,
                'unchanged_today': 0,
            }
        )
        return stats
    
    def increment_movement(self, movement_type):
        """Increment movement counter"""
        if movement_type == 'increase':
            self.increases_today += 1
        elif movement_type == 'decrease':
            self.decreases_today += 1
        else:
            self.unchanged_today += 1
        self.save()
    
    @property
    def total_movements_today(self):
        """Total price movements today"""
        return self.increases_today + self.decreases_today + self.unchanged_today
    
    @property
    def net_movement_today(self):
        """Net movement (positive = more increases, negative = more decreases)"""
        return self.increases_today - self.decreases_today


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
    payment_address = models.CharField(max_length=255, blank=True, null=True, help_text="NOWPayments payment address")
    
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
    
    def update_price(self, new_price, price_change_24h=None, price_change_percentage_24h=None, volume_24h=None, market_cap=None):
        """Update the current price and calculate changes"""
        if price_change_24h is None:
            price_change_24h = new_price - self.current_price
        if price_change_percentage_24h is None and self.current_price > 0:
            price_change_percentage_24h = (price_change_24h / self.current_price) * 100
        
        # Safety check: Limit percentage to prevent database overflow
        if price_change_percentage_24h and price_change_percentage_24h > 999999.99:
            price_change_percentage_24h = 999999.99
        elif price_change_percentage_24h and price_change_percentage_24h < -999999.99:
            price_change_percentage_24h = -999999.99
        
        self.current_price = new_price
        self.price_change_24h = price_change_24h
        self.price_change_percentage_24h = price_change_percentage_24h or 0
        
        # Update volume and market cap if provided
        if volume_24h is not None:
            self.volume_24h = volume_24h
        if market_cap is not None:
            self.market_cap = market_cap
            
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

class PaymentTransaction(models.Model):
    """Model for tracking payment transactions"""
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('waiting', 'Waiting for Payment'),
        ('confirming', 'Confirming'),
        ('confirmed', 'Confirmed'),
        ('sending', 'Sending'),
        ('partially_paid', 'Partially Paid'),
        ('finished', 'Finished'),
        ('failed', 'Failed'),
        ('expired', 'Expired'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_TYPE_CHOICES = [
        ('membership', 'Membership Fee'),
        ('investment', 'Investment'),
        ('delivery', 'Buy & Deliver'),
    ]
    
    # Basic payment info
    payment_id = models.CharField(max_length=255, unique=True, help_text="NOWPayments payment ID")
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    
    # Amount details
    amount_usd = models.DecimalField(max_digits=10, decimal_places=2)
    amount_crypto = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    crypto_currency = models.CharField(max_length=10, default='SOL')
    
    # User and item info
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    investment_item = models.ForeignKey(InvestmentItem, on_delete=models.CASCADE, null=True, blank=True)
    
    # NOWPayments specific fields
    nowpayments_payment_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    payment_address = models.CharField(max_length=255, null=True, blank=True)
    payment_extra_id = models.CharField(max_length=255, null=True, blank=True)
    
    # Webhook data
    ipn_data = models.JSONField(default=dict, blank=True)
    signature_verified = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Payment Transaction'
        verbose_name_plural = 'Payment Transactions'
    
    def __str__(self):
        return f"{self.payment_type} - ${self.amount_usd} - {self.payment_status}"
    
    @property
    def is_paid(self):
        return self.payment_status in ['confirmed', 'finished']
    
    @property
    def is_failed(self):
        return self.payment_status in ['failed', 'expired']
    
    @property
    def is_pending(self):
        return self.payment_status in ['pending', 'waiting', 'confirming', 'sending', 'partially_paid']

class MembershipPayment(models.Model):
    """Model for tracking membership payments"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_transaction = models.OneToOneField(PaymentTransaction, on_delete=models.CASCADE)
    membership_type = models.CharField(max_length=50, default='Standard')
    membership_duration = models.CharField(max_length=50, default='1 Year')
    is_active = models.BooleanField(default=False)
    activated_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Membership Payment'
        verbose_name_plural = 'Membership Payments'
    
    def __str__(self):
        return f"{self.user.username} - {self.membership_type} Membership"
    
    @property
    def days_remaining(self):
        if self.expires_at:
            from django.utils import timezone
            now = timezone.now()
            if self.expires_at > now:
                return (self.expires_at - now).days
        return 0


class CryptoWithdrawal(models.Model):
    """Model for crypto withdrawal list - shows people who have withdrawn"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('halted', 'Halted'),
    ]
    
    PRIORITY_CHOICES = [
        ('normal', 'Normal'),
        ('fast', 'Fast Track'),
        ('urgent', 'Urgent'),
    ]
    
    # Basic info
    name = models.CharField(max_length=100, help_text="Full name of the person")
    amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    currency = models.CharField(max_length=10, default='USD')
    crypto_currency = models.CharField(max_length=10, default='BTC')
    
    # Status and priority
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='normal')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    estimated_delivery = models.DateTimeField(null=True, blank=True, help_text="Estimated delivery date")
    
    # Payment info
    payment_id = models.CharField(max_length=100, blank=True, help_text="NOWPayments transaction ID")
    payment_address = models.CharField(max_length=200, blank=True, help_text="Crypto address for payment")
    payment_amount = models.DecimalField(max_digits=15, decimal_places=8, null=True, blank=True, help_text="Amount in crypto")
    
    # Additional info
    notes = models.TextField(blank=True, help_text="Internal notes")
    is_public = models.BooleanField(default=True, help_text="Show in public withdrawal list")
    order_position = models.PositiveIntegerField(default=0, help_text="Position in the list (0 = top)")
    
    class Meta:
        ordering = ['order_position', '-created_at']
        verbose_name = 'Crypto Withdrawal'
        verbose_name_plural = 'Crypto Withdrawals'
    
    def __str__(self):
        return f"{self.name} - ${self.amount} ({self.status})"
    
    def save(self, *args, **kwargs):
        # Auto-set order position if not set
        if self.order_position == 0:
            max_pos = CryptoWithdrawal.objects.aggregate(
                max_pos=models.Max('order_position')
            )['max_pos'] or 0
            self.order_position = max_pos + 1
        super().save(*args, **kwargs)
    
    @property
    def is_fast_track(self):
        return self.priority == 'fast'
    
    @property
    def display_amount(self):
        return f"${self.amount:,.2f}"
    
    @property
    def status_display(self):
        return dict(self.STATUS_CHOICES)[self.status]
    
    @property
    def priority_display(self):
        return dict(self.PRIORITY_CHOICES)[self.priority]
    
    @property
    def estimated_delivery_display(self):
        """Display estimated delivery in a user-friendly format"""
        if not self.estimated_delivery:
            return "TBD"
        
        from django.utils import timezone
        now = timezone.now()
        
        # Handle timezone mismatch - make both timezone-aware
        if self.estimated_delivery.tzinfo is None:
            # If estimated_delivery is naive, make it timezone-aware
            estimated_delivery = timezone.make_aware(self.estimated_delivery)
        else:
            estimated_delivery = self.estimated_delivery
            
        delta = estimated_delivery - now
        
        if delta.days < 0:
            return "Overdue"
        elif delta.days == 0:
            return "Today"
        elif delta.days == 1:
            return "Tomorrow"
        elif delta.days < 7:
            return f"{delta.days} days"
        elif delta.days < 14:
            weeks = delta.days // 7
            remaining_days = delta.days % 7
            if remaining_days == 0:
                return f"{weeks} week{'s' if weeks > 1 else ''}"
            else:
                return f"{weeks} week{'s' if weeks > 1 else ''} {remaining_days} day{'s' if remaining_days > 1 else ''}"
        elif delta.days < 28:  # Changed from 30 to 28 to handle 3 weeks (21 days) properly
            weeks = delta.days // 7
            remaining_days = delta.days % 7
            if remaining_days == 0:
                return f"{weeks} week{'s' if weeks > 1 else ''}"
            else:
                return f"{weeks} week{'s' if weeks > 1 else ''} {remaining_days} day{'s' if remaining_days > 1 else ''}"
        elif delta.days < 30:
            weeks = delta.days // 7
            return f"{weeks} week{'s' if weeks > 1 else ''}"
        else:
            months = delta.days // 30
            remaining_days = delta.days % 30
            if remaining_days == 0:
                return f"{months} month{'s' if months > 1 else ''}"
            else:
                weeks = remaining_days // 7
                if weeks > 0:
                    return f"{months} month{'s' if months > 1 else ''} {weeks} week{'s' if weeks > 1 else ''}"
                else:
                    return f"{months} month{'s' if months > 1 else ''} {remaining_days} day{'s' if remaining_days > 1 else ''}"