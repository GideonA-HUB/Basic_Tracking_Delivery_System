"""
Serializers for news models
"""
from rest_framework import serializers
from .news_models import NewsArticle, NewsCategory, NewsSource, UserNewsPreference, NewsAnalytics


class NewsSourceSerializer(serializers.ModelSerializer):
    """Serializer for news sources"""
    
    class Meta:
        model = NewsSource
        fields = ['id', 'name', 'base_url', 'is_active', 'last_fetch']


class NewsCategorySerializer(serializers.ModelSerializer):
    """Serializer for news categories"""
    
    class Meta:
        model = NewsCategory
        fields = ['id', 'name', 'display_name', 'description', 'is_active']


class NewsArticleSerializer(serializers.ModelSerializer):
    """Serializer for news articles"""
    source = NewsSourceSerializer(read_only=True)
    category = NewsCategorySerializer(read_only=True)
    time_ago = serializers.ReadOnlyField()
    
    class Meta:
        model = NewsArticle
        fields = [
            'id', 'title', 'summary', 'url', 'image_url', 'published_at',
            'source', 'category', 'author', 'tags', 'sentiment_score',
            'relevance_score', 'is_featured', 'view_count', 'time_ago'
        ]
        read_only_fields = ['id', 'published_at', 'view_count', 'time_ago']


class NewsArticleListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for news article lists"""
    category_name = serializers.CharField(source='category.display_name', read_only=True)
    source_name = serializers.CharField(source='source.name', read_only=True)
    time_ago = serializers.ReadOnlyField()
    
    class Meta:
        model = NewsArticle
        fields = [
            'id', 'title', 'summary', 'url', 'image_url', 'published_at',
            'category_name', 'source_name', 'is_featured', 'time_ago'
        ]


class UserNewsPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for user news preferences"""
    preferred_categories = NewsCategorySerializer(many=True, read_only=True)
    preferred_category_names = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = UserNewsPreference
        fields = [
            'preferred_categories', 'preferred_category_names',
            'auto_refresh_enabled', 'refresh_interval_minutes',
            'show_featured_only'
        ]
    
    def update(self, instance, validated_data):
        """Update user preferences"""
        preferred_category_names = validated_data.pop('preferred_category_names', None)
        
        if preferred_category_names is not None:
            from .news_models import NewsCategory
            categories = NewsCategory.objects.filter(name__in=preferred_category_names)
            instance.preferred_categories.set(categories)
        
        return super().update(instance, validated_data)


class NewsWidgetSerializer(serializers.ModelSerializer):
    """Serializer for news widgets"""
    category_name = serializers.CharField(source='category.display_name', read_only=True)
    source_name = serializers.CharField(source='source.name', read_only=True)
    time_ago = serializers.ReadOnlyField()
    
    class Meta:
        model = NewsArticle
        fields = [
            'id', 'title', 'summary', 'url', 'image_url', 'published_at',
            'category_name', 'source_name', 'is_featured', 'time_ago'
        ]


class NewsAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for news analytics"""
    article_title = serializers.CharField(source='article.title', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = NewsAnalytics
        fields = [
            'id', 'article_title', 'user_username', 'action',
            'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']
