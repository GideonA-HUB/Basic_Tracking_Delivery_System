#!/usr/bin/env python3
"""
Script to simulate real-time price updates for the investment system
Run this periodically to see live price updates in action
"""

import os
import sys
import django
import random
import time
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
django.setup()

from django.utils import timezone
from investments.models import RealTimePriceFeed, InvestmentItem, UserInvestment


def simulate_price_updates():
    """Simulate realistic price updates for all assets"""
    print("🔄 SIMULATING REAL-TIME PRICE UPDATES")
    print("=" * 50)
    
    # Update real-time price feeds
    price_feeds = RealTimePriceFeed.objects.filter(is_active=True)
    
    for feed in price_feeds:
        current_price = float(feed.current_price)
        
        # Simulate realistic price movements (small changes)
        price_change_percent = random.uniform(-2.0, 2.0)  # ±2% max change
        price_change_amount = current_price * (price_change_percent / 100)
        new_price = current_price + price_change_amount
        
        # Update the price feed
        feed.update_price(
            Decimal(str(new_price)),
            Decimal(str(price_change_amount)),
            Decimal(str(price_change_percent))
        )
        
        print(f"📈 {feed.name}: ${new_price:.2f} ({price_change_percent:+.2f}%)")
    
    # Update investment item prices
    investment_items = InvestmentItem.objects.filter(is_active=True)
    
    for item in investment_items:
        current_price = float(item.current_price_usd)
        
        # Simulate price changes
        price_change_percent = random.uniform(-1.5, 1.5)  # ±1.5% max change
        price_change_amount = current_price * (price_change_percent / 100)
        new_price = current_price + price_change_amount
        
        # Update the item price
        item.update_price(
            Decimal(str(new_price)),
            Decimal(str(price_change_amount)),
            Decimal(str(price_change_percent))
        )
        
        print(f"💎 {item.name}: ${new_price:.2f} ({price_change_percent:+.2f}%)")
    
    # Update user investment values
    user_investments = UserInvestment.objects.filter(status='active')
    
    total_portfolio_change = 0
    for investment in user_investments:
        old_value = float(investment.current_value_usd)
        
        # Recalculate current value based on updated item price
        investment.current_value_usd = investment.quantity * investment.item.current_price_usd
        investment.total_return_usd = investment.current_value_usd - investment.investment_amount_usd
        
        if investment.investment_amount_usd > 0:
            investment.total_return_percentage = (investment.total_return_usd / investment.investment_amount_usd) * 100
        
        investment.save()
        
        new_value = float(investment.current_value_usd)
        value_change = new_value - old_value
        total_portfolio_change += value_change
        
        print(f"💰 {investment.user.username} - {investment.item.name}: ${new_value:.2f} (${value_change:+.2f})")
    
    print(f"\n📊 Total Portfolio Change: ${total_portfolio_change:+.2f}")
    print(f"⏰ Updated at: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)


def continuous_updates(interval_seconds=30, max_updates=10):
    """Run continuous price updates"""
    print(f"🔄 Starting continuous price updates (every {interval_seconds} seconds, max {max_updates} updates)")
    print("Press Ctrl+C to stop")
    print("=" * 50)
    
    try:
        for i in range(max_updates):
            print(f"\n🔄 Update #{i+1}/{max_updates}")
            simulate_price_updates()
            
            if i < max_updates - 1:  # Don't sleep after the last update
                print(f"⏳ Waiting {interval_seconds} seconds for next update...")
                time.sleep(interval_seconds)
    
    except KeyboardInterrupt:
        print("\n⏹️  Stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")


def main():
    """Main function"""
    if len(sys.argv) > 1:
        if sys.argv[1] == 'continuous':
            interval = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            max_updates = int(sys.argv[3]) if len(sys.argv) > 3 else 10
            continuous_updates(interval, max_updates)
        else:
            print("Usage: python simulate_live_updates.py [continuous [interval_seconds [max_updates]]]")
    else:
        # Single update
        simulate_price_updates()


if __name__ == '__main__':
    main()
