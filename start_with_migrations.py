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
        
        # HYBRID NEWS SYSTEM - Try real APIs first, fallback to sample
        print("📰 HYBRID NEWS SYSTEM - Attempting real news first...")
        try:
            from investments.news_models import NewsArticle, NewsCategory, NewsSource
            from django.utils import timezone
            
            # Check current article count
            current_count = NewsArticle.objects.count()
            print(f"📊 Current articles in database: {current_count}")
            
            # Try to fetch real news from APIs first
            if current_count < 20:  # Only fetch if we have few articles
                print("🔄 Attempting to fetch real news from APIs...")
                try:
                    # Try the new force_api_news command with debugging
                    execute_from_command_line(['manage.py', 'force_api_news', '--count=30', '--test-apis', '--verbosity=2'])
                    print("✅ API news command completed!")
                    
                    # Check if we got real articles
                    new_count = NewsArticle.objects.count()
                    if new_count > current_count:
                        print(f"🎉 SUCCESS! Added {new_count - current_count} real news articles!")
                    else:
                        print("⚠️  No new articles from APIs, using fallback...")
                        raise Exception("No new articles from APIs")
                        
                except Exception as api_error:
                    print(f"⚠️  API fetch failed: {api_error}")
                    print("🔄 Falling back to sample news...")
                    
                    # Clear existing news and create sample
                    NewsArticle.objects.all().delete()
                    print("🗑️  Cleared existing news for fresh start")
                    
                    # Create categories
                    categories = [
                        {'name': 'crypto', 'display_name': 'Cryptocurrency', 'description': 'Crypto news'},
                        {'name': 'bitcoin', 'display_name': 'Bitcoin', 'description': 'Bitcoin news'},
                        {'name': 'ethereum', 'display_name': 'Ethereum', 'description': 'Ethereum news'},
                        {'name': 'stocks', 'display_name': 'Stock Market', 'description': 'Stock news'},
                        {'name': 'real_estate', 'display_name': 'Real Estate', 'description': 'Real estate news'},
                        {'name': 'altcoins', 'display_name': 'Altcoins', 'description': 'Altcoin news'},
                    ]
                    
                    created_categories = {}
                    for cat_data in categories:
                        cat, created = NewsCategory.objects.get_or_create(
                            name=cat_data['name'],
                            defaults=cat_data
                        )
                        created_categories[cat_data['name']] = cat
                        print(f"✅ Category: {cat_data['name']}")
                    
                    # Create source
                    source, created = NewsSource.objects.get_or_create(
                        name='Meridian News',
                        defaults={
                            'base_url': 'https://meridianassetlogistics.com',
                            'is_active': True
                        }
                    )
                    print("✅ News source created")
                    
                    # Create sample articles
                    articles = [
                        {
                            'title': 'Bitcoin Reaches New All-Time High Amid Institutional Adoption',
                            'summary': 'Bitcoin has surged to new record levels as major institutions continue to adopt cryptocurrency, driving unprecedented market growth.',
                            'category': 'crypto',
                            'is_featured': True
                        },
                        {
                            'title': 'Stock Market Rally Continues as Tech Stocks Lead Gains',
                            'summary': 'Major indices are up as technology companies report strong quarterly earnings, with the S&P 500 reaching new highs.',
                            'category': 'stocks',
                            'is_featured': True
                        },
                        {
                            'title': 'Real Estate Market Shows Strong Growth in Q4',
                            'summary': 'Property values continue to rise across major metropolitan areas, with commercial real estate leading the recovery.',
                            'category': 'real_estate',
                            'is_featured': True
                        },
                        {
                            'title': 'Ethereum 2.0 Staking Rewards Hit Record Levels',
                            'summary': 'Ethereum staking rewards have reached new highs as the network continues to grow and improve efficiency.',
                            'category': 'ethereum',
                            'is_featured': True
                        },
                        {
                            'title': 'Gold Prices Stabilize After Recent Volatility',
                            'summary': 'Gold has found support levels after recent market fluctuations, with investors seeking safe haven assets.',
                            'category': 'stocks',
                            'is_featured': False
                        },
                        {
                            'title': 'Bitcoin ETF Approval Drives Institutional Investment',
                            'summary': 'Recent Bitcoin ETF approvals have led to increased institutional investment in cryptocurrency markets.',
                            'category': 'bitcoin',
                            'is_featured': True
                        },
                        {
                            'title': 'Real Estate Investment Trusts Show Strong Performance',
                            'summary': 'REITs continue to perform well as investors seek stable returns in the current market environment.',
                            'category': 'real_estate',
                            'is_featured': False
                        },
                        {
                            'title': 'Cryptocurrency Market Cap Reaches New Milestone',
                            'summary': 'The total cryptocurrency market cap has reached a new all-time high, driven by increased adoption.',
                            'category': 'crypto',
                            'is_featured': True
                        },
                        {
                            'title': 'Tech Stocks Lead Market Recovery',
                            'summary': 'Technology companies are leading the market recovery with strong earnings and innovative products.',
                            'category': 'stocks',
                            'is_featured': False
                        },
                        {
                            'title': 'Ethereum Network Upgrade Improves Efficiency',
                            'summary': 'Latest Ethereum network upgrade has improved transaction efficiency and reduced fees significantly.',
                            'category': 'ethereum',
                            'is_featured': False
                        },
                        {
                            'title': 'Altcoin Season Begins as Bitcoin Consolidates',
                            'summary': 'Alternative cryptocurrencies are showing strong performance as Bitcoin enters a consolidation phase.',
                            'category': 'altcoins',
                            'is_featured': True
                        },
                        {
                            'title': 'Commercial Real Estate Sees Record Investment',
                            'summary': 'Commercial real estate markets are experiencing record levels of investment from institutional buyers.',
                            'category': 'real_estate',
                            'is_featured': False
                        },
                        {
                            'title': 'Bitcoin Mining Difficulty Reaches New High',
                            'summary': 'Bitcoin mining difficulty has reached a new all-time high, indicating strong network security.',
                            'category': 'bitcoin',
                            'is_featured': False
                        },
                        {
                            'title': 'DeFi Protocols Show Continued Growth',
                            'summary': 'Decentralized finance protocols continue to show strong growth with increasing total value locked.',
                            'category': 'crypto',
                            'is_featured': False
                        },
                        {
                            'title': 'Housing Market Shows Signs of Cooling',
                            'summary': 'The housing market is showing signs of cooling as interest rates stabilize and inventory increases.',
                            'category': 'real_estate',
                            'is_featured': False
                        }
                    ]
                    
                    created_count = 0
                    for article_data in articles:
                        NewsArticle.objects.create(
                            title=article_data['title'],
                            summary=article_data['summary'],
                            content=article_data['summary'] + " This is a comprehensive analysis of the current market trends and their implications for investors.",
                            source=source,
                            category=created_categories[article_data['category']],
                            is_featured=article_data['is_featured'],
                            is_active=True,
                            published_at=timezone.now()
                        )
                        created_count += 1
                    
                    print(f"✅ FALLBACK: Created {created_count} sample news articles!")
            else:
                print(f"✅ News system already has {current_count} articles - skipping creation")
            
            # Show final statistics
            total_articles = NewsArticle.objects.count()
            featured_articles = NewsArticle.objects.filter(is_featured=True).count()
            active_articles = NewsArticle.objects.filter(is_active=True).count()
            
            print(f"📊 FINAL STATS: {total_articles} total, {featured_articles} featured, {active_articles} active")
            
        except Exception as e:
            print(f"❌ CRITICAL ERROR in hybrid news system: {e}")
            import traceback
            traceback.print_exc()
        
        # FORCE FETCH MARKETAUX NEWS BEFORE STARTING SERVER
        print("🚀 FORCE FETCHING MARKETAUX NEWS...")
        try:
            # Import the force fetch function
            from investments.management.commands.force_marketaux_news import Command as ForceFetchCommand
            
            # Create command instance and run it
            force_fetch = ForceFetchCommand()
            force_fetch.handle(count=30)
            print("✅ Force fetch completed!")
        except Exception as force_error:
            print(f"⚠️ Force fetch failed: {force_error}")
            print("🔄 Continuing without force fetch...")
        
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
