#!/usr/bin/env python
"""
Startup script that ensures migrations run before starting the server
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

def main():
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
    
    # Initialize Django
    django.setup()
    
    print("🚀 Starting application with migration check...")
    
    try:
        # Run migrations first
        print("🔄 Running migrations...")
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])
        print("✅ Migrations completed successfully")
        
        # Collect static files
        print("📁 Collecting static files...")
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput', '--clear'])
        print("✅ Static files collected successfully")
        
        # Fix news system
        print("📰 Checking news system...")
        try:
            from investments.news_models import NewsArticle
            article_count = NewsArticle.objects.count()
            
            if article_count < 10:
                print("🔄 Low article count, fetching news...")
                try:
                    execute_from_command_line(['manage.py', 'force_news_update', '--count=30', '--verbosity=0'])
                    print("✅ News system updated successfully")
                except Exception as api_error:
                    print(f"⚠️  API fetch failed: {api_error}")
                    print("🔄 Creating sample news as fallback...")
                    execute_from_command_line(['manage.py', 'create_sample_news', '--count=50', '--verbosity=0'])
                    print("✅ Sample news created as fallback")
            else:
                print(f"✅ News system has {article_count} articles")
        except Exception as e:
            print(f"⚠️  News system check failed: {e}")
            # Force create sample data as fallback
            print("🔄 FORCE creating sample news...")
            try:
                execute_from_command_line(['manage.py', 'create_sample_news', '--count=50', '--verbosity=0'])
                print("✅ Sample news created as fallback")
            except Exception as e2:
                print(f"⚠️  Sample news creation failed: {e2}")
                # EMERGENCY FIX - Use the bulletproof command
                print("🚨 EMERGENCY: Using bulletproof news creation...")
                try:
                    execute_from_command_line(['manage.py', 'emergency_news_fix', '--verbosity=0'])
                    print("✅ Emergency news fix completed successfully")
                except Exception as e3:
                    print(f"❌ Emergency fix failed: {e3}")
                    # Last resort - create news directly
                    print("🔄 Creating news directly in database...")
                    try:
                        from investments.news_models import NewsCategory, NewsSource
                        from django.utils import timezone
                        
                        # Create categories
                        crypto_cat, _ = NewsCategory.objects.get_or_create(
                            name='crypto',
                            defaults={'display_name': 'Cryptocurrency', 'description': 'Crypto news'}
                        )
                        stocks_cat, _ = NewsCategory.objects.get_or_create(
                            name='stocks',
                            defaults={'display_name': 'Stock Market', 'description': 'Stock news'}
                        )
                        real_estate_cat, _ = NewsCategory.objects.get_or_create(
                            name='real_estate',
                            defaults={'display_name': 'Real Estate', 'description': 'Real estate news'}
                        )
                        
                        # Create source
                        source, _ = NewsSource.objects.get_or_create(
                            name='Sample News',
                            defaults={'base_url': 'https://example.com', 'is_active': True}
                        )
                        
                        # Create articles
                        articles = [
                            {
                                'title': 'Bitcoin Reaches New All-Time High Amid Institutional Adoption',
                                'summary': 'Bitcoin has surged to new record levels as major institutions continue to adopt cryptocurrency.',
                                'category': crypto_cat,
                                'is_featured': True
                            },
                            {
                                'title': 'Stock Market Rally Continues as Tech Stocks Lead Gains',
                                'summary': 'Major indices are up as technology companies report strong quarterly earnings.',
                                'category': stocks_cat,
                                'is_featured': True
                            },
                            {
                                'title': 'Real Estate Market Shows Strong Growth in Q4',
                                'summary': 'Property values continue to rise across major metropolitan areas.',
                                'category': real_estate_cat,
                                'is_featured': False
                            },
                            {
                                'title': 'Ethereum 2.0 Staking Rewards Hit Record Levels',
                                'summary': 'Ethereum staking rewards have reached new highs as the network continues to grow.',
                                'category': crypto_cat,
                                'is_featured': True
                            },
                            {
                                'title': 'Gold Prices Stabilize After Recent Volatility',
                                'summary': 'Gold has found support levels after recent market fluctuations.',
                                'category': stocks_cat,
                                'is_featured': False
                            }
                        ]
                        
                        created_count = 0
                        for article_data in articles:
                            if not NewsArticle.objects.filter(title=article_data['title']).exists():
                                NewsArticle.objects.create(
                                    title=article_data['title'],
                                    summary=article_data['summary'],
                                    content=article_data['summary'],
                                    source=source,
                                    category=article_data['category'],
                                    is_featured=article_data['is_featured'],
                                    is_active=True,
                                    published_at=timezone.now()
                                )
                                created_count += 1
                        
                        print(f"✅ Created {created_count} news articles directly")
                    except Exception as e4:
                        print(f"❌ Direct creation failed: {e4}")
        
        # Start the server
        print("🚀 Starting Daphne server...")
        import subprocess
        import sys
        
        # Get port from environment
        port = os.environ.get('PORT', '8080')
        
        # Start Daphne
        cmd = [
            'daphne', 
            '-b', '0.0.0.0', 
            '-p', port, 
            'delivery_tracker.asgi:application'
        ]
        
        print(f"🚀 Starting server on port {port}")
        subprocess.run(cmd)
        
    except Exception as e:
        print(f"❌ Error during startup: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
