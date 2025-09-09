#!/usr/bin/env python
"""
Railway Deployment Fix Script
Fixes common deployment issues for the Meridian Asset Logistics platform
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings_production')

# Initialize Django
django.setup()

from django.core.management import execute_from_command_line
from django.db import connection
from investments.models import RealTimePriceFeed, InvestmentItem
from investments.news_models import NewsArticle, NewsSource, NewsCategory
import logging

logger = logging.getLogger(__name__)

def fix_database_issues():
    """Fix common database issues"""
    try:
        logger.info("🔧 Fixing database issues...")
        
        # Check database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            logger.info("✅ Database connection successful")
        
        # Ensure we have basic price feeds
        create_basic_price_feeds()
        
        # Ensure we have basic news data
        create_basic_news_data()
        
        logger.info("✅ Database issues fixed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database fix failed: {e}")
        return False

def create_basic_price_feeds():
    """Create basic price feeds if they don't exist"""
    try:
        logger.info("📊 Creating basic price feeds...")
        
        basic_feeds = [
            {'symbol': 'BTC', 'name': 'Bitcoin (BTC)', 'current_price': 110000.00, 'price_change_24h': 0.0, 'price_change_percentage_24h': 0.0},
            {'symbol': 'ETH', 'name': 'Ethereum (ETH)', 'current_price': 4300.00, 'price_change_24h': 0.0, 'price_change_percentage_24h': 0.0},
            {'symbol': 'ADA', 'name': 'Cardano (ADA)', 'current_price': 0.80, 'price_change_24h': 0.0, 'price_change_percentage_24h': 0.0},
            {'symbol': 'SOL', 'name': 'Solana (SOL)', 'current_price': 200.00, 'price_change_24h': 0.0, 'price_change_percentage_24h': 0.0},
            {'symbol': 'XAU', 'name': 'Gold Bullion (1 oz)', 'current_price': 2000.00, 'price_change_24h': 0.0, 'price_change_percentage_24h': 0.0},
            {'symbol': 'XAG', 'name': 'Silver Bullion (1 oz)', 'current_price': 25.00, 'price_change_24h': 0.0, 'price_change_percentage_24h': 0.0},
        ]
        
        for feed_data in basic_feeds:
            feed, created = RealTimePriceFeed.objects.get_or_create(
                symbol=feed_data['symbol'],
                defaults={
                    'name': feed_data['name'],
                    'current_price': feed_data['current_price'],
                    'price_change_24h': feed_data['price_change_24h'],
                    'price_change_percentage_24h': feed_data['price_change_percentage_24h'],
                    'is_active': True
                }
            )
            if created:
                logger.info(f"✅ Created price feed: {feed.name}")
            else:
                logger.info(f"📊 Price feed exists: {feed.name}")
        
        logger.info("✅ Basic price feeds ready")
        
    except Exception as e:
        logger.error(f"❌ Failed to create price feeds: {e}")

def create_basic_news_data():
    """Create basic news data if it doesn't exist"""
    try:
        logger.info("📰 Creating basic news data...")
        
        # Create news categories
        crypto_category, _ = NewsCategory.objects.get_or_create(
            name='Cryptocurrency',
            defaults={'description': 'Cryptocurrency and blockchain news'}
        )
        
        stocks_category, _ = NewsCategory.objects.get_or_create(
            name='Stocks',
            defaults={'description': 'Stock market and equity news'}
        )
        
        real_estate_category, _ = NewsCategory.objects.get_or_create(
            name='Real Estate',
            defaults={'description': 'Real estate and property news'}
        )
        
        # Create news sources
        source, _ = NewsSource.objects.get_or_create(
            name='Meridian News',
            defaults={
                'url': 'https://meridianassetlogistics.com',
                'is_active': True
            }
        )
        
        # Create sample news articles
        sample_articles = [
            {
                'title': 'Bitcoin Reaches New All-Time High',
                'summary': 'Bitcoin has reached a new all-time high, driven by institutional adoption and positive market sentiment.',
                'category': crypto_category,
                'tags': ['bitcoin', 'cryptocurrency', 'price']
            },
            {
                'title': 'Ethereum 2.0 Upgrade Shows Promising Results',
                'summary': 'The Ethereum 2.0 upgrade continues to show promising results with improved scalability and reduced energy consumption.',
                'category': crypto_category,
                'tags': ['ethereum', 'blockchain', 'upgrade']
            },
            {
                'title': 'Real Estate Market Shows Strong Growth',
                'summary': 'The real estate market continues to show strong growth with increased demand for both residential and commercial properties.',
                'category': real_estate_category,
                'tags': ['real estate', 'property', 'growth']
            },
            {
                'title': 'Stock Market Reaches Record Highs',
                'summary': 'Major stock indices have reached record highs, driven by strong corporate earnings and economic recovery.',
                'category': stocks_category,
                'tags': ['stocks', 'market', 'earnings']
            }
        ]
        
        for article_data in sample_articles:
            article, created = NewsArticle.objects.get_or_create(
                title=article_data['title'],
                defaults={
                    'summary': article_data['summary'],
                    'category': article_data['category'],
                    'source': source,
                    'url': f"https://meridianassetlogistics.com/news/{article_data['title'].lower().replace(' ', '-')}",
                    'is_active': True,
                    'is_featured': True
                }
            )
            if created:
                logger.info(f"✅ Created news article: {article.title}")
            else:
                logger.info(f"📰 News article exists: {article.title}")
        
        logger.info("✅ Basic news data ready")
        
    except Exception as e:
        logger.error(f"❌ Failed to create news data: {e}")

def run_migrations():
    """Run database migrations"""
    try:
        logger.info("🔄 Running database migrations...")
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])
        logger.info("✅ Migrations completed")
        return True
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        return False

def collect_static_files():
    """Collect static files"""
    try:
        logger.info("📁 Collecting static files...")
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
        logger.info("✅ Static files collected")
        return True
    except Exception as e:
        logger.error(f"❌ Static file collection failed: {e}")
        return False

def main():
    """Main deployment fix function"""
    logger.info("🚀 Starting Railway deployment fix...")
    
    # Run migrations first
    if not run_migrations():
        logger.error("❌ Migration failed, aborting")
        return False
    
    # Collect static files
    if not collect_static_files():
        logger.error("❌ Static file collection failed, aborting")
        return False
    
    # Fix database issues
    if not fix_database_issues():
        logger.error("❌ Database fix failed, aborting")
        return False
    
    logger.info("✅ Railway deployment fix completed successfully!")
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
