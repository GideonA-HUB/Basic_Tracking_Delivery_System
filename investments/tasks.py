from celery import shared_task
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json
import logging

from .models import RealTimePriceFeed, InvestmentItem
from .price_services import price_service, get_live_price_updates

logger = logging.getLogger(__name__)

@shared_task
def update_real_time_prices():
    """Update real-time prices and broadcast updates"""
    try:
        # Update all prices
        updated_count = price_service.update_all_prices()
        
        if updated_count > 0:
            # Get live price updates for broadcasting
            price_updates = get_live_price_updates()
            
            # Broadcast updates via WebSocket
            broadcast_price_updates(price_updates)
            
            logger.info(f"Updated {updated_count} prices and broadcasted updates")
        
        return updated_count
        
    except Exception as e:
        logger.error(f"Error updating real-time prices: {e}")
        return 0

@shared_task
def broadcast_price_updates(price_updates):
    """Broadcast price updates to all connected WebSocket clients"""
    try:
        channel_layer = get_channel_layer()
        
        # Broadcast to price feeds group
        async_to_sync(channel_layer.group_send)(
            'price_feeds',
            {
                'type': 'price_update',
                'price_data': price_updates
            }
        )
        
        logger.info(f"Broadcasted {len(price_updates)} price updates")
        
    except Exception as e:
        logger.error(f"Error broadcasting price updates: {e}")

@shared_task
def update_investment_item_prices():
    """Update investment item prices based on price feeds"""
    try:
        # Map investment items to price feeds
        item_feed_mapping = {
            'Bitcoin (BTC)': 'BTC',
            'Ethereum (ETH)': 'ETH',
            'Cardano (ADA)': 'ADA',
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
                        
                        # Update item price
                        item.current_price_usd = new_price
                        item.price_change_24h = price_change
                        item.price_change_percentage_24h = price_change_percentage
                        item.last_price_update = timezone.now()
                        item.save()
                        
                        updated_count += 1
                        logger.info(f"Updated {item_name}: ${new_price} ({price_change_percentage:+.2f}%)")
                        
            except Exception as e:
                logger.error(f"Error updating {item_name}: {e}")
        
        return updated_count
        
    except Exception as e:
        logger.error(f"Error updating investment item prices: {e}")
        return 0

@shared_task
def cleanup_old_price_history():
    """Clean up old price history records"""
    try:
        from .models import PriceHistory, RealTimePriceHistory
        from datetime import timedelta
        
        # Keep only last 30 days of price history
        cutoff_date = timezone.now() - timedelta(days=30)
        
        # Clean up investment item price history
        deleted_item_history = PriceHistory.objects.filter(
            timestamp__lt=cutoff_date
        ).delete()
        
        # Clean up real-time price feed history
        deleted_feed_history = RealTimePriceHistory.objects.filter(
            timestamp__lt=cutoff_date
        ).delete()
        
        logger.info(f"Cleaned up {deleted_item_history[0]} item price history records")
        logger.info(f"Cleaned up {deleted_feed_history[0]} feed price history records")
        
        return deleted_item_history[0] + deleted_feed_history[0]
        
    except Exception as e:
        logger.error(f"Error cleaning up price history: {e}")
        return 0

@shared_task
def health_check_price_feeds():
    """Health check for price feeds"""
    try:
        feeds = RealTimePriceFeed.objects.filter(is_active=True)
        healthy_count = 0
        total_count = feeds.count()
        
        for feed in feeds:
            # Check if feed was updated in the last hour
            if feed.last_updated and (timezone.now() - feed.last_updated).total_seconds() < 3600:
                healthy_count += 1
            else:
                logger.warning(f"Price feed {feed.name} ({feed.symbol}) may be stale")
        
        health_percentage = (healthy_count / total_count * 100) if total_count > 0 else 0
        logger.info(f"Price feed health check: {healthy_count}/{total_count} feeds healthy ({health_percentage:.1f}%)")
        
        return {
            'healthy_count': healthy_count,
            'total_count': total_count,
            'health_percentage': health_percentage
        }
        
    except Exception as e:
        logger.error(f"Error in price feed health check: {e}")
        return {'error': str(e)}
