#!/usr/bin/env python
"""
Script to check the current state of the investment system
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
django.setup()

from investments.models import (
    InvestmentItem, RealTimePriceFeed, PriceHistory, 
    PriceMovementStats, InvestmentCategory
)
from django.utils import timezone

def check_investment_system():
    print("=== INVESTMENT SYSTEM DIAGNOSTIC ===\n")
    
    # Check categories
    print("1. INVESTMENT CATEGORIES:")
    categories = InvestmentCategory.objects.filter(is_active=True)
    print(f"   Total active categories: {categories.count()}")
    for cat in categories:
        print(f"   - {cat.name}")
    print()
    
    # Check investment items
    print("2. INVESTMENT ITEMS:")
    items = InvestmentItem.objects.filter(is_active=True)
    print(f"   Total active items: {items.count()}")
    
    print("\n   Sample items:")
    for item in items[:10]:
        print(f"   - {item.name}: ${item.current_price_usd} (Symbol: {item.symbol or 'None'})")
        print(f"     Featured: {item.is_featured}, Last update: {item.last_price_update}")
    
    # Check featured items
    print(f"\n3. FEATURED ITEMS:")
    featured = InvestmentItem.objects.filter(is_featured=True, is_active=True)
    print(f"   Featured items count: {featured.count()}")
    for item in featured:
        print(f"   - {item.name}: ${item.current_price_usd}")
    print()
    
    # Check price feeds
    print("4. REAL-TIME PRICE FEEDS:")
    feeds = RealTimePriceFeed.objects.filter(is_active=True)
    print(f"   Total active feeds: {feeds.count()}")
    for feed in feeds[:10]:
        print(f"   - {feed.name} ({feed.symbol}): ${feed.current_price}")
        print(f"     Change 24h: {feed.price_change_percentage_24h}%, Last update: {feed.last_updated}")
    print()
    
    # Check price history
    print("5. PRICE HISTORY:")
    history_count = PriceHistory.objects.count()
    print(f"   Total price history records: {history_count}")
    if history_count > 0:
        recent_history = PriceHistory.objects.order_by('-timestamp')[:5]
        print("   Recent price updates:")
        for h in recent_history:
            print(f"   - {h.item.name}: ${h.price} at {h.timestamp}")
    print()
    
    # Check movement stats
    print("6. PRICE MOVEMENT STATISTICS:")
    stats_count = PriceMovementStats.objects.count()
    print(f"   Total movement stats records: {stats_count}")
    if stats_count > 0:
        recent_stats = PriceMovementStats.objects.order_by('-date')[:5]
        print("   Recent movement stats:")
        for s in recent_stats:
            print(f"   - {s.item.name} ({s.date}): ↑{s.increases_today} ↓{s.decreases_today}")
    print()
    
    # Check for issues
    print("7. POTENTIAL ISSUES:")
    issues = []
    
    # Check for items without symbols
    items_without_symbols = InvestmentItem.objects.filter(is_active=True, symbol__isnull=True).count()
    if items_without_symbols > 0:
        issues.append(f"   - {items_without_symbols} items without symbols (can't get live prices)")
    
    # Check for items with old price updates
    old_updates = InvestmentItem.objects.filter(
        is_active=True,
        last_price_update__lt=timezone.now() - timezone.timedelta(hours=24)
    ).count()
    if old_updates > 0:
        issues.append(f"   - {old_updates} items with prices older than 24 hours")
    
    # Check for missing price feeds
    items_with_symbols = InvestmentItem.objects.filter(is_active=True, symbol__isnull=False)
    missing_feeds = 0
    for item in items_with_symbols:
        if not RealTimePriceFeed.objects.filter(symbol=item.symbol, is_active=True).exists():
            missing_feeds += 1
    if missing_feeds > 0:
        issues.append(f"   - {missing_feeds} items with symbols but no matching price feeds")
    
    if issues:
        for issue in issues:
            print(issue)
    else:
        print("   - No obvious issues detected")
    
    print("\n=== DIAGNOSTIC COMPLETE ===")

if __name__ == "__main__":
    check_investment_system()
