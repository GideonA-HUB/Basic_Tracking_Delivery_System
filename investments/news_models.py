"""
News models for the investment platform
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class NewsSource(models.Model):
    """News source configuration"""
    name = models.CharField(max_length=100, unique=True)
    api_key = models.CharField(max_length=500, blank=True)
    base_url = models.URLField()
    is_active = models.BooleanField(default=True)
    rate_limit_per_hour = models.IntegerField(default=1000)
    last_fetch = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class NewsCategory(models.Model):
    """News categories for filtering"""
    CATEGORY_CHOICES = [
        ('crypto', 'Cryptocurrency'),
        ('stocks', 'Stock Market'),
        ('real_estate', 'Real Estate'),
        ('forex', 'Forex'),
        ('commodities', 'Commodities'),
        ('general', 'General Finance'),
        ('bitcoin', 'Bitcoin'),
        ('ethereum', 'Ethereum'),
        ('altcoins', 'Altcoins'),
    ]
    
    name = models.CharField(max_length=50, choices=CATEGORY_CHOICES, unique=True)
    display_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'name']
        verbose_name_plural = 'News Categories'

    def __str__(self):
        return self.display_name


class NewsArticle(models.Model):
    """Individual news articles"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=500)
    summary = models.TextField(blank=True)
    content = models.TextField(blank=True)
    url = models.URLField()
    image_url = models.URLField(blank=True)
    published_at = models.DateTimeField()
    source = models.ForeignKey(NewsSource, on_delete=models.CASCADE, related_name='articles')
    category = models.ForeignKey(NewsCategory, on_delete=models.CASCADE, related_name='articles')
    
    # Metadata
    author = models.CharField(max_length=200, blank=True)
    tags = models.JSONField(default=list, blank=True)
    sentiment_score = models.FloatField(null=True, blank=True)  # -1 to 1
    relevance_score = models.FloatField(default=0.0)  # 0 to 1
    
    # Status
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    view_count = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at', '-created_at']
        indexes = [
            models.Index(fields=['-published_at']),
            models.Index(fields=['category', '-published_at']),
            models.Index(fields=['is_featured', '-published_at']),
        ]

    def __str__(self):
        return self.title[:100]

    @property
    def time_ago(self):
        """Human readable time since publication"""
        now = timezone.now()
        diff = now - self.published_at
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "Just now"

    def increment_view_count(self):
        """Increment view count"""
        self.view_count += 1
        self.save(update_fields=['view_count'])


class NewsCache(models.Model):
    """Cache for news API responses"""
    cache_key = models.CharField(max_length=200, unique=True)
    data = models.JSONField()
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Cache: {self.cache_key}"

    @classmethod
    def is_valid(cls, cache_key):
        """Check if cache is still valid"""
        try:
            cache = cls.objects.get(cache_key=cache_key)
            return cache.expires_at > timezone.now()
        except cls.DoesNotExist:
            return False

    @classmethod
    def get_data(cls, cache_key):
        """Get cached data if valid"""
        try:
            cache = cls.objects.get(cache_key=cache_key)
            if cache.expires_at > timezone.now():
                return cache.data
            else:
                cache.delete()
                return None
        except cls.DoesNotExist:
            return None

    @classmethod
    def set_data(cls, cache_key, data, expires_in_minutes=15):
        """Set cached data"""
        expires_at = timezone.now() + timezone.timedelta(minutes=expires_in_minutes)
        cls.objects.update_or_create(
            cache_key=cache_key,
            defaults={'data': data, 'expires_at': expires_at}
        )


class UserNewsPreference(models.Model):
    """User preferences for news filtering"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='news_preferences')
    preferred_categories = models.ManyToManyField(NewsCategory, blank=True)
    auto_refresh_enabled = models.BooleanField(default=True)
    refresh_interval_minutes = models.IntegerField(default=15)
    show_featured_only = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"News Preferences for {self.user.username}"


class NewsAnalytics(models.Model):
    """Analytics for news engagement"""
    article = models.ForeignKey(NewsArticle, on_delete=models.CASCADE, related_name='analytics')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    action = models.CharField(max_length=50, choices=[
        ('view', 'View'),
        ('click', 'Click'),
        ('share', 'Share'),
        ('bookmark', 'Bookmark'),
    ])
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['article', 'action']),
            models.Index(fields=['-timestamp']),
        ]

    def __str__(self):
        return f"{self.article.title[:50]} - {self.action}"
