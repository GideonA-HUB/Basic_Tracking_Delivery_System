#!/usr/bin/env python
"""
Startup script to fix news on Railway
This runs automatically when the app starts
"""
import os
import sys
import django
import logging

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
django.setup()

from django.core.management import call_command
from investments.news_models import NewsArticle

logger = logging.getLogger(__name__)

def startup_news_fix():
    """Fix news on startup"""
    try:
        # Check if we have any news articles
        article_count = NewsArticle.objects.count()
        
        if article_count < 10:  # If we have less than 10 articles
            logger.info("🚀 Low article count, fetching news on startup...")
            
            # Try to fetch from APIs
            try:
                call_command('force_news_update', '--count=30', verbosity=0)
                logger.info("✅ News fetched from APIs successfully")
            except Exception as e:
                logger.warning(f"API fetch failed: {e}, creating sample data...")
                # Create sample data as fallback
                call_command('create_sample_news', '--count=20', verbosity=0)
                logger.info("✅ Sample news created as fallback")
        else:
            logger.info(f"✅ News system already has {article_count} articles")
            
    except Exception as e:
        logger.error(f"❌ Startup news fix failed: {e}")

if __name__ == '__main__':
    startup_news_fix()
