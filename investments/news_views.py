"""
News views and API endpoints
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.conf import settings
import json
import logging

from .news_models import (
    NewsArticle, NewsCategory, NewsSource, NewsCache, 
    UserNewsPreference, NewsAnalytics
)
from .news_services import NewsAggregator
from .news_serializers import NewsArticleSerializer, NewsCategorySerializer

logger = logging.getLogger(__name__)


class NewsArticleViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for news articles"""
    queryset = NewsArticle.objects.filter(is_active=True)
    serializer_class = NewsArticleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__name=category)
        
        # Filter by featured
        featured = self.request.query_params.get('featured')
        if featured and featured.lower() == 'true':
            queryset = queryset.filter(is_featured=True)
        
        # Filter by source
        source = self.request.query_params.get('source')
        if source:
            queryset = queryset.filter(source__name=source)
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(summary__icontains=search) |
                Q(tags__icontains=search)
            )
        
        return queryset.order_by('-published_at')
    
    @action(detail=True, methods=['post'])
    def track_view(self, request, pk=None):
        """Track article view"""
        article = self.get_object()
        
        # Create analytics record
        NewsAnalytics.objects.create(
            article=article,
            user=request.user if request.user.is_authenticated else None,
            action='view',
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # Increment view count
        article.increment_view_count()
        
        return Response({'status': 'success'})
    
    @action(detail=True, methods=['post'])
    def track_click(self, request, pk=None):
        """Track article click"""
        article = self.get_object()
        
        NewsAnalytics.objects.create(
            article=article,
            user=request.user if request.user.is_authenticated else None,
            action='click',
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return Response({'status': 'success'})
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class NewsCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for news categories"""
    queryset = NewsCategory.objects.filter(is_active=True)
    serializer_class = NewsCategorySerializer
    permission_classes = [permissions.IsAuthenticated]


@method_decorator(csrf_exempt, name='dispatch')
class NewsAPIView(APIView):
    """Main news API endpoint"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get news articles"""
        try:
            # Get parameters
            category = request.GET.get('category')
            limit = int(request.GET.get('limit', 20))
            featured_only = request.GET.get('featured', 'false').lower() == 'true'
            search = request.GET.get('search')
            
            # Get user preferences
            user_prefs = self.get_user_preferences(request.user)
            
            # Build queryset
            queryset = NewsArticle.objects.filter(is_active=True)
            
            if category:
                queryset = queryset.filter(category__name=category)
            elif user_prefs and user_prefs.preferred_categories.exists():
                queryset = queryset.filter(category__in=user_prefs.preferred_categories.all())
            
            if featured_only or (user_prefs and user_prefs.show_featured_only):
                queryset = queryset.filter(is_featured=True)
            
            if search:
                queryset = queryset.filter(
                    Q(title__icontains=search) | 
                    Q(summary__icontains=search)
                )
            
            # Order and limit
            articles = queryset.order_by('-published_at')[:limit]
            
            # Serialize data
            serializer = NewsArticleSerializer(articles, many=True, context={'request': request})
            
            return Response({
                'status': 'success',
                'articles': serializer.data,
                'count': len(articles),
                'timestamp': timezone.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error in NewsAPIView: {e}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get_user_preferences(self, user):
        """Get user news preferences"""
        try:
            return UserNewsPreference.objects.get(user=user)
        except UserNewsPreference.DoesNotExist:
            return None


@method_decorator(csrf_exempt, name='dispatch')
class NewsRefreshAPIView(APIView):
    """API endpoint to refresh news"""
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request):
        """Trigger news refresh"""
        try:
            aggregator = NewsAggregatorService()
            
            # Fetch new articles
            articles = aggregator.fetch_all_news()
            
            # Save articles
            saved_count = aggregator.save_articles(articles)
            
            # Update featured news
            aggregator.update_featured_news()
            
            return Response({
                'status': 'success',
                'message': f'Refreshed news successfully',
                'articles_fetched': len(articles),
                'articles_saved': saved_count,
                'timestamp': timezone.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error refreshing news: {e}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class PublicNewsRefreshAPIView(APIView):
    """Public API endpoint to refresh news (for cron jobs)"""
    permission_classes = []  # No authentication required
    
    def get(self, request):
        """Trigger news refresh via GET request"""
        try:
            # Check for secret token to prevent abuse
            secret_token = request.GET.get('token')
            expected_token = getattr(settings, 'NEWS_REFRESH_TOKEN', 'meridian-news-refresh-2025')
            
            if secret_token != expected_token:
                return Response({
                    'status': 'error',
                    'message': 'Invalid token'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            aggregator = NewsAggregatorService()
            
            # Fetch new articles
            articles = aggregator.fetch_all_news()
            
            # Save articles
            saved_count = aggregator.save_articles(articles)
            
            # Update featured news
            aggregator.update_featured_news()
            
            return Response({
                'status': 'success',
                'message': f'Refreshed news successfully',
                'articles_fetched': len(articles),
                'articles_saved': saved_count,
                'timestamp': timezone.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error refreshing news: {e}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class NewsWidgetAPIView(APIView):
    """API endpoint for news widgets"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get news for widgets"""
        try:
            widget_type = request.GET.get('type', 'dashboard')
            limit = int(request.GET.get('limit', 10))
            
            if widget_type == 'dashboard':
                # Dashboard widget - mix of featured and recent
                featured = NewsArticle.objects.filter(
                    is_active=True, is_featured=True
                ).order_by('-published_at')[:limit//2]
                
                recent = NewsArticle.objects.filter(
                    is_active=True, is_featured=False
                ).order_by('-published_at')[:limit//2]
                
                articles = list(featured) + list(recent)
                
            elif widget_type == 'crypto':
                # Crypto widget
                articles = NewsArticle.objects.filter(
                    is_active=True,
                    category__name__in=['crypto', 'bitcoin', 'ethereum', 'altcoins']
                ).order_by('-published_at')[:limit]
                
            elif widget_type == 'stocks':
                # Stocks widget
                articles = NewsArticle.objects.filter(
                    is_active=True,
                    category__name='stocks'
                ).order_by('-published_at')[:limit]
                
            elif widget_type == 'real_estate':
                # Real estate widget
                articles = NewsArticle.objects.filter(
                    is_active=True,
                    category__name='real_estate'
                ).order_by('-published_at')[:limit]
                
            else:
                # Default - recent news
                articles = NewsArticle.objects.filter(
                    is_active=True
                ).order_by('-published_at')[:limit]
            
            # Serialize data
            serializer = NewsArticleSerializer(articles, many=True, context={'request': request})
            
            return Response({
                'status': 'success',
                'articles': serializer.data,
                'widget_type': widget_type,
                'count': len(articles),
                'timestamp': timezone.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error in NewsWidgetAPIView: {e}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class NewsPreferencesAPIView(APIView):
    """API endpoint for user news preferences"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get user preferences"""
        try:
            prefs, created = UserNewsPreference.objects.get_or_create(user=request.user)
            
            return Response({
                'status': 'success',
                'preferences': {
                    'preferred_categories': [cat.name for cat in prefs.preferred_categories.all()],
                    'auto_refresh_enabled': prefs.auto_refresh_enabled,
                    'refresh_interval_minutes': prefs.refresh_interval_minutes,
                    'show_featured_only': prefs.show_featured_only,
                }
            })
            
        except Exception as e:
            logger.error(f"Error getting news preferences: {e}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        """Update user preferences"""
        try:
            prefs, created = UserNewsPreference.objects.get_or_create(user=request.user)
            
            data = request.data
            
            # Update preferences
            if 'preferred_categories' in data:
                categories = NewsCategory.objects.filter(name__in=data['preferred_categories'])
                prefs.preferred_categories.set(categories)
            
            if 'auto_refresh_enabled' in data:
                prefs.auto_refresh_enabled = data['auto_refresh_enabled']
            
            if 'refresh_interval_minutes' in data:
                prefs.refresh_interval_minutes = data['refresh_interval_minutes']
            
            if 'show_featured_only' in data:
                prefs.show_featured_only = data['show_featured_only']
            
            prefs.save()
            
            return Response({
                'status': 'success',
                'message': 'Preferences updated successfully'
            })
            
        except Exception as e:
            logger.error(f"Error updating news preferences: {e}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Frontend views
@login_required
def news_dashboard(request):
    """News dashboard page"""
    try:
        # Check if we need to fetch fresh news
        total_articles = NewsArticle.objects.filter(is_active=True).count()
        
        # If we have less than 20 articles, try to fetch fresh news
        if total_articles < 20:
            logger.info("Low article count, fetching fresh news from APIs")
            try:
                aggregator = NewsAggregator()
                aggregator.fetch_all_news(['crypto', 'bitcoin', 'stocks', 'real_estate'], 10)
            except Exception as e:
                logger.warning(f"Could not fetch fresh news: {e}")
        
        categories = NewsCategory.objects.filter(is_active=True)
        
        # Get featured news
        featured_news = NewsArticle.objects.filter(
            is_active=True, 
            is_featured=True
        ).order_by('-published_at')[:6]
        
        # Get latest news
        latest_news = NewsArticle.objects.filter(
            is_active=True
        ).order_by('-published_at')[:20]
        
        # Get category-specific news
        crypto_news = NewsArticle.objects.filter(
            is_active=True,
            category__name__in=['crypto', 'bitcoin', 'ethereum', 'altcoins']
        ).order_by('-published_at')[:5]
        
        stocks_news = NewsArticle.objects.filter(
            is_active=True,
            category__name='stocks'
        ).order_by('-published_at')[:5]
        
        real_estate_news = NewsArticle.objects.filter(
            is_active=True,
            category__name='real_estate'
        ).order_by('-published_at')[:5]
        
        context = {
            'categories': categories,
            'user_preferences': UserNewsPreference.objects.filter(user=request.user).first(),
            'featured_news': featured_news,
            'latest_news': latest_news,
            'crypto_news': crypto_news,
            'stocks_news': stocks_news,
            'real_estate_news': real_estate_news,
        }
        
        return render(request, 'investments/news_dashboard.html', context)
        
    except Exception as e:
        logger.error(f"Error in news_dashboard: {e}")
        context = {
            'categories': [],
            'user_preferences': None,
            'featured_news': [],
            'latest_news': [],
            'crypto_news': [],
            'stocks_news': [],
            'real_estate_news': [],
            'error': str(e)
        }
        return render(request, 'investments/news_dashboard.html', context)


@login_required
def news_article_detail(request, article_id):
    """News article detail page"""
    article = get_object_or_404(NewsArticle, id=article_id, is_active=True)
    
    # Track view
    NewsAnalytics.objects.create(
        article=article,
        user=request.user,
        action='view',
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    
    article.increment_view_count()
    
    # Get related articles
    related_articles = NewsArticle.objects.filter(
        is_active=True,
        category=article.category
    ).exclude(id=article.id).order_by('-published_at')[:5]
    
    context = {
        'article': article,
        'related_articles': related_articles
    }
    
    return render(request, 'investments/news_article_detail.html', context)
