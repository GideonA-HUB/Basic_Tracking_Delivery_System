"""
Management command to test MarketAux API directly
"""
from django.core.management.base import BaseCommand
from django.conf import settings
import requests
import json

class Command(BaseCommand):
    help = 'Test MarketAux API directly'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test-key',
            type=str,
            help='Test with a specific API key'
        )

    def handle(self, *args, **options):
        test_key = options.get('test_key')
        
        self.stdout.write("🔍 TESTING MARKETAUX API...")
        self.stdout.write("=" * 50)
        
        # Get API key
        if test_key:
            api_key = test_key
            self.stdout.write(f"Using provided test key: {api_key[:8]}...")
        else:
            api_key = getattr(settings, 'MARKETAUX_API_KEY', '')
            self.stdout.write(f"Using settings key: {'✅ Set' if api_key else '❌ Not Set'}")
        
        if not api_key:
            self.stdout.write("❌ No API key available!")
            return
        
        # Test API call
        self.stdout.write(f"\n🌐 Testing API call with key: {api_key[:8]}...")
        
        try:
            url = "https://api.marketaux.com/v1/news/all"
            params = {
                'api_token': api_key,
                'symbols': 'BTC,ETH,AAPL,MSFT',
                'limit': 5,
                'language': 'en',
                'filter_entities': 'true'
            }
            
            self.stdout.write(f"Request URL: {url}")
            self.stdout.write(f"Request params: {params}")
            
            response = requests.get(url, params=params, timeout=15)
            
            self.stdout.write(f"\nResponse Status: {response.status_code}")
            self.stdout.write(f"Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                self.stdout.write("✅ API call successful!")
                
                # Show response structure
                self.stdout.write(f"\nResponse structure:")
                self.stdout.write(f"  Keys: {list(data.keys())}")
                
                if 'data' in data:
                    articles = data['data']
                    self.stdout.write(f"  Articles count: {len(articles)}")
                    
                    if articles:
                        self.stdout.write(f"\nFirst article:")
                        first = articles[0]
                        for key, value in first.items():
                            if isinstance(value, str) and len(value) > 100:
                                self.stdout.write(f"  {key}: {value[:100]}...")
                            else:
                                self.stdout.write(f"  {key}: {value}")
                else:
                    self.stdout.write("  No 'data' key in response")
                    self.stdout.write(f"  Full response: {json.dumps(data, indent=2)}")
            else:
                self.stdout.write(f"❌ API call failed!")
                self.stdout.write(f"Error: {response.text}")
                
        except requests.exceptions.RequestException as e:
            self.stdout.write(f"❌ Request error: {e}")
        except Exception as e:
            self.stdout.write(f"❌ Unexpected error: {e}")
        
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("Test completed!")
