#!/usr/bin/env python
"""
Simulate Live Price Updates
This script simulates real-time price updates for testing the live price system
"""

import os
import sys
import django
import time
import random
from decimal import Decimal
from django.utils import timezone

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
django.setup()

from investments.models import RealTimePriceFeed, InvestmentItem
from investments.price_services import price_service
import logging

logger = logging.getLogger(__name__)

def simulate_price_updates():
    """Simulate live price updates"""
    print("🚀 Starting Live Price Simulation...")
    print("Press Ctrl+C to stop")
    print()
    
    # Get all active price feeds
    feeds = RealTimePriceFeed.objects.filter(is_active=True)
    print(f"📊 Monitoring {feeds.count()} price feeds:")
    for feed in feeds:
        print(f"   - {feed.name} ({feed.symbol}): ${feed.current_price}")
    print()
    
    update_count = 0
    
    try:
        while True:
            update_count += 1
            print(f"🔄 Update #{update_count} - {timezone.now().strftime('%H:%M:%S')}")
            
            # Simulate price changes for each feed
            for feed in feeds:
                # Generate random price change (-2% to +2%)
                change_percent = random.uniform(-2.0, 2.0)
                old_price = float(feed.current_price)
                new_price = old_price * (1 + change_percent / 100)
                
                # Calculate changes
                change_amount = new_price - old_price
                change_percentage = change_percent
                
                # Update the feed
                feed.update_price(
                    Decimal(str(new_price)),
                    Decimal(str(change_amount)),
                    Decimal(str(change_percentage))
                )
                
                # Update corresponding investment items
                update_investment_items(feed)
                
                # Display update
                change_symbol = "📈" if change_amount >= 0 else "📉"
                print(f"   {change_symbol} {feed.name} ({feed.symbol}): ${old_price:.2f} → ${new_price:.2f} ({change_percentage:+.2f}%)")
            
            print()
            
            # Wait 30 seconds before next update
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\n⏹️  Live price simulation stopped")
        print(f"📊 Total updates: {update_count}")

def update_investment_items(feed):
    """Update investment items based on price feed changes"""
    # Map feed symbols to investment item names
    item_mapping = {
        'BTC': 'Bitcoin (BTC)',
        'ETH': 'Ethereum (ETH)',
        'ADA': 'Cardano (ADA)',
        'XAU': 'Gold Bullion (1 oz)',
        'XAG': 'Silver Bullion (1 oz)',
        'XPT': 'Platinum Bullion (1 oz)',
    }
    
    item_name = item_mapping.get(feed.symbol)
    if item_name:
        try:
            item = InvestmentItem.objects.filter(name=item_name).first()
            if item:
                old_price = float(item.current_price_usd)
                new_price = float(feed.current_price)
                
                if old_price != new_price:
                    # Calculate price change
                    price_change = new_price - old_price
                    price_change_percentage = (price_change / old_price * 100) if old_price > 0 else 0
                    
                    # Update item price
                    item.current_price_usd = Decimal(str(new_price))
                    item.price_change_24h = Decimal(str(price_change))
                    item.price_change_percentage_24h = Decimal(str(price_change_percentage))
                    item.save()
                    
        except Exception as e:
            logger.error(f"Error updating investment item {item_name}: {e}")

def main():
    """Main function"""
    print("=== Live Price Update Simulator ===")
    print()
    
    # Check if price feeds exist
    feeds_count = RealTimePriceFeed.objects.filter(is_active=True).count()
    if feeds_count == 0:
        print("❌ No active price feeds found!")
        print("Please run 'python manage.py setup_price_feeds' first.")
        return
    
    print(f"✅ Found {feeds_count} active price feeds")
    print()
    
    # Start simulation
    simulate_price_updates()

if __name__ == '__main__':
    main()
