#!/usr/bin/env python3
"""
FORCE PRODUCTION UPDATE
This script forces an immediate update of production prices.
"""

import os
import sys
import django
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
django.setup()

from investments.models import RealTimePriceFeed

def force_update_production_prices():
    """Force update production prices via API call"""
    try:
        print("🚨 FORCING PRODUCTION PRICE UPDATE...")
        
        # Get current real prices from CoinGecko
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,cardano,solana&vs_currencies=usd&include_24hr_change=true"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Update Bitcoin
            if 'bitcoin' in data:
                btc_price = data['bitcoin']['usd']
                btc_change = data['bitcoin'].get('usd_24h_change', 0)
                
                # Update local database
                feed, created = RealTimePriceFeed.objects.get_or_create(
                    symbol='BTC',
                    defaults={'name': 'Bitcoin (BTC)', 'is_active': True}
                )
                feed.current_price = btc_price
                feed.price_change_percentage_24h = btc_change
                feed.save()
                
                print(f"✅ Updated Bitcoin: ${btc_price:,.2f} ({btc_change:+.2f}%)")
            
            # Update Ethereum
            if 'ethereum' in data:
                eth_price = data['ethereum']['usd']
                eth_change = data['ethereum'].get('usd_24h_change', 0)
                
                feed, created = RealTimePriceFeed.objects.get_or_create(
                    symbol='ETH',
                    defaults={'name': 'Ethereum (ETH)', 'is_active': True}
                )
                feed.current_price = eth_price
                feed.price_change_percentage_24h = eth_change
                feed.save()
                
                print(f"✅ Updated Ethereum: ${eth_price:,.2f} ({eth_change:+.2f}%)")
            
            # Update Cardano
            if 'cardano' in data:
                ada_price = data['cardano']['usd']
                ada_change = data['cardano'].get('usd_24h_change', 0)
                
                feed, created = RealTimePriceFeed.objects.get_or_create(
                    symbol='ADA',
                    defaults={'name': 'Cardano (ADA)', 'is_active': True}
                )
                feed.current_price = ada_price
                feed.price_change_percentage_24h = ada_change
                feed.save()
                
                print(f"✅ Updated Cardano: ${ada_price:,.2f} ({ada_change:+.2f}%)")
            
            # Update Solana
            if 'solana' in data:
                sol_price = data['solana']['usd']
                sol_change = data['solana'].get('usd_24h_change', 0)
                
                feed, created = RealTimePriceFeed.objects.get_or_create(
                    symbol='SOL',
                    defaults={'name': 'Solana (SOL)', 'is_active': True}
                )
                feed.current_price = sol_price
                feed.price_change_percentage_24h = sol_change
                feed.save()
                
                print(f"✅ Updated Solana: ${sol_price:,.2f} ({sol_change:+.2f}%)")
            
            print("🎉 PRODUCTION PRICES UPDATED SUCCESSFULLY!")
            return True
            
        else:
            print(f"❌ API Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error updating prices: {e}")
        return False

if __name__ == "__main__":
    force_update_production_prices()
