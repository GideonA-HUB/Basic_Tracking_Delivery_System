"""
Management views for admin operations
"""
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.management import call_command
from django.contrib import messages
from django.shortcuts import redirect
from .news_models import NewsArticle
import logging

logger = logging.getLogger(__name__)


@staff_member_required
def fix_news_system(request):
    """Web endpoint to fix news system"""
    try:
        # Check current article count
        article_count = NewsArticle.objects.count()
        
        if article_count < 10:
            # Try to fetch from APIs
            try:
                call_command('force_news_update', '--count=30', verbosity=0)
                messages.success(request, f'✅ Successfully fetched news from APIs!')
            except Exception as e:
                logger.warning(f"API fetch failed: {e}, creating sample data...")
                # Create sample data as fallback
                call_command('create_sample_news', '--count=20', verbosity=0)
                messages.success(request, f'✅ Created sample news as fallback!')
        else:
            messages.info(request, f'✅ News system already has {article_count} articles')
        
        # Get updated stats
        updated_count = NewsArticle.objects.count()
        featured_count = NewsArticle.objects.filter(is_featured=True).count()
        
        context = {
            'article_count': updated_count,
            'featured_count': featured_count,
            'success': True
        }
        
        return render(request, 'investments/news_fix_result.html', context)
        
    except Exception as e:
        logger.error(f"Error in fix_news_system: {e}")
        messages.error(request, f'❌ Error fixing news system: {str(e)}')
        return render(request, 'investments/news_fix_result.html', {'error': str(e)})


@staff_member_required
def news_system_status(request):
    """Check news system status"""
    try:
        total_articles = NewsArticle.objects.count()
        featured_articles = NewsArticle.objects.filter(is_featured=True).count()
        active_articles = NewsArticle.objects.filter(is_active=True).count()
        
        # Get articles by category
        from .news_models import NewsCategory
        categories = NewsCategory.objects.all()
        category_stats = {}
        for category in categories:
            count = NewsArticle.objects.filter(category=category).count()
            if count > 0:
                category_stats[category.name] = count
        
        # Get articles by source
        from .news_models import NewsSource
        sources = NewsSource.objects.all()
        source_stats = {}
        for source in sources:
            count = NewsArticle.objects.filter(source=source).count()
            if count > 0:
                source_stats[source.name] = count
        
        context = {
            'total_articles': total_articles,
            'featured_articles': featured_articles,
            'active_articles': active_articles,
            'category_stats': category_stats,
            'source_stats': source_stats,
        }
        
        return render(request, 'investments/news_status.html', context)
        
    except Exception as e:
        logger.error(f"Error in news_system_status: {e}")
        return render(request, 'investments/news_status.html', {'error': str(e)})


@csrf_exempt
@require_http_methods(["POST"])
def api_fix_news(request):
    """API endpoint to fix news (for external calls)"""
    try:
        # Check current article count
        article_count = NewsArticle.objects.count()
        
        if article_count < 10:
            # Try to fetch from APIs
            try:
                call_command('force_news_update', '--count=30', verbosity=0)
                message = 'Successfully fetched news from APIs!'
            except Exception as e:
                logger.warning(f"API fetch failed: {e}, creating sample data...")
                # Create sample data as fallback
                call_command('create_sample_news', '--count=20', verbosity=0)
                message = 'Created sample news as fallback!'
        else:
            message = f'News system already has {article_count} articles'
        
        # Get updated stats
        updated_count = NewsArticle.objects.count()
        featured_count = NewsArticle.objects.filter(is_featured=True).count()
        
        return JsonResponse({
            'success': True,
            'message': message,
            'article_count': updated_count,
            'featured_count': featured_count
        })
        
    except Exception as e:
        logger.error(f"Error in api_fix_news: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
