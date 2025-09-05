"""
Django management command to fix real-time prices on production server
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
import requests
import logging

from investments.models import InvestmentItem, RealTimePriceFeed, PriceHistory, PriceMovementStats

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Fix real-time prices on production server'

    def handle(self, *args, **options):
        self.stdout.write("🚨 FIXING REAL-TIME PRICES ON PRODUCTION SERVER...")
        
        try:
            # Fetch real prices from CoinGecko API
            response = requests.get(
                'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,cardano&vs_currencies=usd&include_24hr_change=true',
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Update Bitcoin
                btc_price = data['bitcoin']['usd']
                btc_change = data['bitcoin'].get('usd_24h_change', 0)
                
                btc_items = InvestmentItem.objects.filter(symbol='BTC', is_active=True)
                for item in btc_items:
                    item.current_price_usd = Decimal(str(btc_price))
                    item.price_change_24h = Decimal(str(btc_change))
                    item.price_change_percentage_24h = Decimal(str(btc_change))
                    item.last_price_update = timezone.now()
                    item.save()
                    self.stdout.write(f"✅ Updated {item.name}: ${btc_price} ({btc_change:+.2f}%)")
                
                # Update Ethereum
                eth_price = data['ethereum']['usd']
                eth_change = data['ethereum'].get('usd_24h_change', 0)
                
                eth_items = InvestmentItem.objects.filter(symbol='ETH', is_active=True)
                for item in eth_items:
                    item.current_price_usd = Decimal(str(eth_price))
                    item.price_change_24h = Decimal(str(eth_change))
                    item.price_change_percentage_24h = Decimal(str(eth_change))
                    item.last_price_update = timezone.now()
                    item.save()
                    self.stdout.write(f"✅ Updated {item.name}: ${eth_price} ({eth_change:+.2f}%)")
                
                # Update Cardano
                ada_price = data['cardano']['usd']
                ada_change = data['cardano'].get('usd_24h_change', 0)
                
                ada_items = InvestmentItem.objects.filter(symbol='ADA', is_active=True)
                for item in ada_items:
                    item.current_price_usd = Decimal(str(ada_price))
                    item.price_change_24h = Decimal(str(ada_change))
                    item.price_change_percentage_24h = Decimal(str(ada_change))
                    item.last_price_update = timezone.now()
                    item.save()
                    self.stdout.write(f"✅ Updated {item.name}: ${ada_price} ({ada_change:+.2f}%)")
                
                # Update price feeds
                for symbol, price_data in [('BTC', {'price': btc_price, 'change': btc_change}), 
                                         ('ETH', {'price': eth_price, 'change': eth_change}),
                                         ('ADA', {'price': ada_price, 'change': ada_change})]:
                    feed, created = RealTimePriceFeed.objects.get_or_create(
                        symbol=symbol,
                        defaults={'name': f'{symbol} Feed', 'is_active': True}
                    )
                    feed.current_price = Decimal(str(price_data['price']))
                    feed.price_change_24h = Decimal(str(price_data['change']))
                    feed.price_change_percentage_24h = Decimal(str(price_data['change']))
                    feed.last_updated = timezone.now()
                    feed.is_active = True
                    feed.save()
                
                self.stdout.write(self.style.SUCCESS("✅ Real-time prices updated successfully!"))
                
            else:
                self.stdout.write(self.style.ERROR("❌ Failed to fetch real-time prices"))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error: {e}"))
