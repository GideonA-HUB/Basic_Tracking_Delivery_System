#!/usr/bin/env python
"""
Railway News Fix Script
Run this on Railway to force news update
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
django.setup()

from django.core.management import call_command

def fix_news_on_railway():
    print("🚀 FIXING NEWS ON RAILWAY...")
    
    try:
        # Force news update
        print("📰 Fetching news from APIs...")
        call_command('force_news_update', '--count=30', verbosity=2)
        
        print("✅ NEWS FIX COMPLETE!")
        print("Check: https://meridianassetlogistics.com/investments/news/")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        # Try to create sample data as fallback
        try:
            print("Creating sample data as fallback...")
            call_command('create_sample_news', '--count=20', verbosity=2)
            print("✅ Sample data created!")
        except Exception as e2:
            print(f"❌ Fallback failed: {e2}")

if __name__ == '__main__':
    fix_news_on_railway()
