#!/usr/bin/env python
"""
Comprehensive fix for the real-time investment system
This script addresses all the issues with live price updates, charts, and real-time functionality
"""
import os
import sys
import django
import logging
from decimal import Decimal
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
django.setup()

from investments.models import (
    InvestmentItem, RealTimePriceFeed, PriceHistory, 
    PriceMovementStats, InvestmentCategory
)
from investments.price_services import price_service
from django.utils import timezone

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_price_feeds():
    """Fix and update price feeds with real market data"""
    logger.info("=== FIXING PRICE FEEDS ===")
    
    # Update all price feeds with real data
    try:
        updated_count = price_service.update_all_prices()
        logger.info(f"Updated {updated_count} price feeds with real market data")
    except Exception as e:
        logger.error(f"Error updating price feeds: {e}")
    
    # Ensure all investment items have proper symbols and are linked to price feeds
    items = InvestmentItem.objects.filter(is_active=True)
    for item in items:
        if not item.symbol:
            # Generate symbol from name
            symbol = item.name.upper().replace(' ', '_').replace('(', '').replace(')', '').replace('-', '_')
            # Clean up symbol
            symbol = ''.join(c for c in symbol if c.isalnum() or c == '_')
            if len(symbol) > 20:
                symbol = symbol[:20]
            item.symbol = symbol
            item.save()
            logger.info(f"Added symbol '{symbol}' to {item.name}")
        
        # Create or update price feed if it doesn't exist
        feed, created = RealTimePriceFeed.objects.get_or_create(
            symbol=item.symbol,
            defaults={
                'name': item.name,
                'asset_type': 'crypto' if 'bitcoin' in item.name.lower() or 'ethereum' in item.name.lower() else 'other',
                'current_price': item.current_price_usd,
                'base_currency': 'USD',
                'is_active': True
            }
        )
        
        if not created:
            # Update existing feed with current item price
            feed.current_price = item.current_price_usd
            feed.name = item.name
            feed.save()
        
        logger.info(f"Ensured price feed exists for {item.name} ({item.symbol})")

def fix_price_history():
    """Fix price history and movement statistics"""
    logger.info("=== FIXING PRICE HISTORY ===")
    
    # Create price history for items that don't have recent history
    items = InvestmentItem.objects.filter(is_active=True)
    for item in items:
        # Check if item has recent price history
        recent_history = PriceHistory.objects.filter(
            item=item,
            timestamp__gte=timezone.now() - timedelta(hours=24)
        ).exists()
        
        if not recent_history:
            # Create a price history entry
            PriceHistory.objects.create(
                item=item,
                price=item.current_price_usd,
                change_amount=item.price_change_24h or Decimal('0'),
                change_percentage=item.price_change_percentage_24h or Decimal('0'),
                movement_type='unchanged',
                timestamp=timezone.now()
            )
            logger.info(f"Created price history for {item.name}")
        
        # Ensure movement stats exist
        try:
            stats = PriceMovementStats.get_or_create_today_stats(item)
            logger.info(f"Ensured movement stats exist for {item.name}")
        except Exception as e:
            logger.error(f"Error creating movement stats for {item.name}: {e}")

def fix_featured_items():
    """Ensure featured items are properly configured"""
    logger.info("=== FIXING FEATURED ITEMS ===")
    
    # Get all active items
    items = InvestmentItem.objects.filter(is_active=True)
    
    # Ensure we have at least 6 featured items
    featured_count = items.filter(is_featured=True).count()
    
    if featured_count < 6:
        # Add more featured items
        non_featured = items.filter(is_featured=False).order_by('-created_at')[:6-featured_count]
        for item in non_featured:
            item.is_featured = True
            item.save()
            logger.info(f"Made {item.name} featured")
    
    logger.info(f"Total featured items: {items.filter(is_featured=True).count()}")

def update_investment_item_prices():
    """Update investment item prices from price feeds"""
    logger.info("=== UPDATING INVESTMENT ITEM PRICES ===")
    
    # Map investment items to price feeds
    item_feed_mapping = {
        'Bitcoin (BTC)': 'BTC',
        'Ethereum (ETH)': 'ETH',
        'Cardano (ADA)': 'ADA',
        'Solana (SOL)': 'SOL',
        'Chainlink (LINK)': 'LINK',
        'Polkadot (DOT)': 'DOT',
        'Avalanche (AVAX)': 'AVAX',
        'Polygon (MATIC)': 'MATIC',
        'Gold Bullion (1 oz)': 'XAU',
        'Silver Bullion (1 oz)': 'XAG',
        'Platinum Bullion (1 oz)': 'XPT',
    }
    
    updated_count = 0
    for item_name, feed_symbol in item_feed_mapping.items():
        try:
            item = InvestmentItem.objects.filter(name=item_name).first()
            feed = RealTimePriceFeed.objects.filter(symbol=feed_symbol).first()
            
            if item and feed:
                old_price = item.current_price_usd
                new_price = feed.current_price
                
                if old_price != new_price:
                    # Calculate price change
                    price_change = new_price - old_price
                    price_change_percentage = (price_change / old_price * 100) if old_price > 0 else 0
                    
                    # Update item price using the enhanced method
                    item.update_price(
                        new_price,
                        price_change,
                        price_change_percentage,
                        volume_24h=feed.volume_24h if hasattr(feed, 'volume_24h') else None,
                        market_cap=feed.market_cap if hasattr(feed, 'market_cap') else None
                    )
                    
                    updated_count += 1
                    logger.info(f"Updated {item_name}: ${new_price} ({price_change_percentage:+.2f}%)")
                    
        except Exception as e:
            logger.error(f"Error updating {item_name}: {e}")
    
    logger.info(f"Updated {updated_count} investment items with real-time prices")

def create_sample_price_data():
    """Create sample price data for demonstration"""
    logger.info("=== CREATING SAMPLE PRICE DATA ===")
    
    # Create some sample price movements for demonstration
    items = InvestmentItem.objects.filter(is_active=True)[:10]
    
    for item in items:
        # Create some price history for the last 7 days
        base_price = float(item.current_price_usd)
        
        for days_ago in range(7, 0, -1):
            # Simulate price movement
            change_percent = (days_ago - 3.5) * 0.5  # Some trend
            price = base_price * (1 + change_percent / 100)
            
            # Create price history entry
            PriceHistory.objects.get_or_create(
                item=item,
                timestamp=timezone.now() - timedelta(days=days_ago),
                defaults={
                    'price': Decimal(str(price)),
                    'change_amount': Decimal(str(price - base_price)),
                    'change_percentage': Decimal(str(change_percent)),
                    'movement_type': 'increase' if change_percent > 0 else 'decrease'
                }
            )
        
        logger.info(f"Created sample price data for {item.name}")

def fix_all_issues():
    """Run all fixes"""
    logger.info("=== STARTING COMPREHENSIVE FIX ===")
    
    try:
        # Fix price feeds
        fix_price_feeds()
        
        # Fix price history
        fix_price_history()
        
        # Fix featured items
        fix_featured_items()
        
        # Update investment item prices
        update_investment_item_prices()
        
        # Create sample data
        create_sample_price_data()
        
        logger.info("=== ALL FIXES COMPLETED SUCCESSFULLY ===")
        
        # Print summary
        print("\n=== SYSTEM STATUS SUMMARY ===")
        print(f"Total investment items: {InvestmentItem.objects.filter(is_active=True).count()}")
        print(f"Total price feeds: {RealTimePriceFeed.objects.filter(is_active=True).count()}")
        print(f"Total featured items: {InvestmentItem.objects.filter(is_featured=True, is_active=True).count()}")
        print(f"Total price history records: {PriceHistory.objects.count()}")
        print(f"Total movement stats: {PriceMovementStats.objects.count()}")
        
        print("\n=== RECENT PRICE UPDATES ===")
        recent_prices = InvestmentItem.objects.filter(is_active=True).order_by('-last_price_update')[:5]
        for item in recent_prices:
            print(f"- {item.name}: ${item.current_price_usd} (Updated: {item.last_price_update})")
        
    except Exception as e:
        logger.error(f"Error in comprehensive fix: {e}")
        raise

if __name__ == "__main__":
    fix_all_issues()
