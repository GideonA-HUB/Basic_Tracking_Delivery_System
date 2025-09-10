#!/usr/bin/env python
"""
Simple test to check if API keys are loaded correctly
"""
import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(project_dir))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
django.setup()

from django.conf import settings

def test_api_keys():
    """Test if API keys are loaded correctly"""
    print("🔑 TESTING API KEYS LOADING...")
    
    # Test direct access
    print(f"NEWSAPI_KEY: {'✅ Set' if getattr(settings, 'NEWSAPI_KEY', '') else '❌ Not Set'}")
    print(f"FINNHUB_API_KEY: {'✅ Set' if getattr(settings, 'FINNHUB_API_KEY', '') else '❌ Not Set'}")
    print(f"CRYPTOPANIC_API_KEY: {'✅ Set' if getattr(settings, 'CRYPTOPANIC_API_KEY', '') else '❌ Not Set'}")
    print(f"COINDESK_API_KEY: {'✅ Set' if getattr(settings, 'COINDESK_API_KEY', '') else '❌ Not Set'}")
    
    # Test environment variables
    print(f"\nENV NEWSAPI_KEY: {'✅ Set' if os.environ.get('NEWSAPI_KEY') else '❌ Not Set'}")
    print(f"ENV FINNHUB_API_KEY: {'✅ Set' if os.environ.get('FINNHUB_API_KEY') else '❌ Not Set'}")
    print(f"ENV CRYPTOPANIC_API_KEY: {'✅ Set' if os.environ.get('CRYPTOPANIC_API_KEY') else '❌ Not Set'}")
    print(f"ENV COINDESK_API_KEY: {'✅ Set' if os.environ.get('COINDESK_API_KEY') else '❌ Not Set'}")
    
    # Show key details if available
    newsapi_key = getattr(settings, 'NEWSAPI_KEY', '')
    if newsapi_key:
        print(f"\nNewsAPI Key length: {len(newsapi_key)}")
        print(f"NewsAPI Key preview: {newsapi_key[:8]}...")
    
    finnhub_key = getattr(settings, 'FINNHUB_API_KEY', '')
    if finnhub_key:
        print(f"Finnhub Key length: {len(finnhub_key)}")
        print(f"Finnhub Key preview: {finnhub_key[:8]}...")

if __name__ == "__main__":
    test_api_keys()
