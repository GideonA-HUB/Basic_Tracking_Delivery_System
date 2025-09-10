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
                execute_from_command_line(['manage.py', 'force_news_update', '--count=30', '--verbosity=0'])
                print("✅ News system updated successfully")
            else:
                print(f"✅ News system has {article_count} articles")
        except Exception as e:
            print(f"⚠️  News system check failed: {e}")
            # Try to create sample data as fallback
            try:
                execute_from_command_line(['manage.py', 'create_sample_news', '--count=20', '--verbosity=0'])
                print("✅ Sample news created as fallback")
            except Exception as e2:
                print(f"⚠️  Sample news creation failed: {e2}")
        
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
