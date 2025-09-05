#!/usr/bin/env python
"""
Script to check the current state of the investment database
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
django.setup()

from investments.models import InvestmentItem, RealTimePriceFeed, PriceHistory, PriceMovementStats

def check_database_state():
    print("=== INVESTMENT DATABASE STATE CHECK ===")
    
    # Check investment items
    total_items = InvestmentItem.objects.count()
    featured_items = InvestmentItem.objects.filter(is_featured=True).count()
    active_items = InvestmentItem.objects.filter(is_active=True).count()
    items_with_symbols = InvestmentItem.objects.exclude(symbol__isnull=True).exclude(symbol='').count()
    
    print(f"📊 Investment Items:")
    print(f"   Total: {total_items}")
    print(f"   Active: {active_items}")
    print(f"   Featured: {featured_items}")
    print(f"   With Symbols: {items_with_symbols}")
    
    # Check price feeds
    total_feeds = RealTimePriceFeed.objects.count()
    active_feeds = RealTimePriceFeed.objects.filter(is_active=True).count()
    
    print(f"\n📈 Price Feeds:")
    print(f"   Total: {total_feeds}")
    print(f"   Active: {active_feeds}")
    
    # Check price history
    total_history = PriceHistory.objects.count()
    recent_history = PriceHistory.objects.filter(timestamp__gte=django.utils.timezone.now() - django.utils.timezone.timedelta(days=1)).count()
    
    print(f"\n📋 Price History:")
    print(f"   Total Records: {total_history}")
    print(f"   Last 24h: {recent_history}")
    
    # Check movement stats
    total_stats = PriceMovementStats.objects.count()
    today_stats = PriceMovementStats.objects.filter(date=django.utils.timezone.now().date()).count()
    
    print(f"\n📊 Movement Stats:")
    print(f"   Total Records: {total_stats}")
    print(f"   Today: {today_stats}")
    
    # Sample featured items
    print(f"\n⭐ Featured Items Sample:")
    featured_sample = InvestmentItem.objects.filter(is_featured=True)[:5]
    for item in featured_sample:
        print(f"   - {item.name} (Price: ${item.current_price_usd}, Symbol: {item.symbol or 'None'})")
    
    # Sample price feeds
    print(f"\n🔄 Price Feeds Sample:")
    feeds_sample = RealTimePriceFeed.objects.filter(is_active=True)[:5]
    for feed in feeds_sample:
        print(f"   - {feed.name} ({feed.symbol}): ${feed.current_price} ({feed.price_change_percentage_24h:+.2f}%)")
    
    # Check for mismatched items
    print(f"\n🔍 Checking for Issues:")
    
    # Items without symbols
    items_without_symbols = InvestmentItem.objects.filter(symbol__isnull=True).count()
    if items_without_symbols > 0:
        print(f"   ⚠️  {items_without_symbols} items without symbols")
    
    # Items with outdated prices
    from django.utils import timezone
    from datetime import timedelta
    outdated_threshold = timezone.now() - timedelta(hours=24)
    outdated_items = InvestmentItem.objects.filter(last_price_update__lt=outdated_threshold).count()
    if outdated_items > 0:
        print(f"   ⚠️  {outdated_items} items with outdated prices (24h+)")
    
    # Missing price feeds for items
    items_with_feeds = 0
    for item in InvestmentItem.objects.filter(is_active=True):
        if RealTimePriceFeed.objects.filter(symbol=item.symbol).exists() or RealTimePriceFeed.objects.filter(name=item.name).exists():
            items_with_feeds += 1
    
    missing_feeds = active_items - items_with_feeds
    if missing_feeds > 0:
        print(f"   ⚠️  {missing_feeds} active items without matching price feeds")
    
    print(f"\n✅ Database check completed!")

if __name__ == "__main__":
    check_database_state()
