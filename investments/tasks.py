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
            
            # Try to broadcast updates via WebSocket (non-blocking)
            try:
                broadcast_price_updates(price_updates)
            except Exception as ws_error:
                logger.warning(f"WebSocket broadcast failed: {ws_error}")
            
            # Update user portfolio values
            try:
                update_user_portfolio_values.delay()
            except Exception as portfolio_error:
                logger.warning(f"Portfolio update failed: {portfolio_error}")
            
            logger.info(f"Updated {updated_count} prices")
        
        return updated_count
        
    except Exception as e:
        logger.error(f"Error updating real-time prices: {e}")
        return 0


@shared_task
def update_user_portfolio_values():
    """Update all user portfolio values based on current prices"""
    try:
        from .models import UserInvestment, InvestmentPortfolio
        
        # Get all active investments
        active_investments = UserInvestment.objects.filter(status='active')
        updated_count = 0
        
        for investment in active_investments:
            try:
                # Calculate current value based on latest item price
                current_value = investment.quantity * investment.item.current_price_usd
                total_return = current_value - investment.investment_amount_usd
                total_return_percentage = (total_return / investment.investment_amount_usd * 100) if investment.investment_amount_usd > 0 else 0
                
                # Update investment values
                investment.current_value_usd = current_value
                investment.total_return_usd = total_return
                investment.total_return_percentage = total_return_percentage
                investment.save()
                
                updated_count += 1
                
            except Exception as e:
                logger.error(f"Error updating investment {investment.id}: {e}")
        
        # Update portfolio summaries
        portfolios = InvestmentPortfolio.objects.all()
        for portfolio in portfolios:
            try:
                portfolio.update_portfolio_summary()
            except Exception as e:
                logger.error(f"Error updating portfolio {portfolio.id}: {e}")
        
        logger.info(f"Updated {updated_count} user investments")
        return updated_count
        
    except Exception as e:
        logger.error(f"Error updating user portfolio values: {e}")
        return 0

@shared_task
def broadcast_price_updates(price_updates):
    """Broadcast price updates to all connected WebSocket clients"""
    try:
        channel_layer = get_channel_layer()
        
        if channel_layer:
            # Broadcast to price feeds group
            async_to_sync(channel_layer.group_send)(
                'price_feeds',
                {
                    'type': 'price_update',
                    'price_data': price_updates
                }
            )
            
            logger.info(f"Broadcasted {len(price_updates)} price updates")
        else:
            logger.warning("Channel layer not available - skipping WebSocket broadcast")
        
    except Exception as e:
        logger.error(f"Error broadcasting price updates: {e}")
        # Don't fail the entire task if WebSocket broadcasting fails

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


@shared_task
def generate_price_alerts():
    """Generate alerts for significant price movements"""
    try:
        from .models import PriceMovementStats, InvestmentItem
        
        alerts = []
        
        # Check for significant daily movements
        items = InvestmentItem.objects.filter(is_active=True)
        for item in items:
            try:
                stats = PriceMovementStats.get_or_create_today_stats(item)
                
                # Alert if more than 10 price changes in a day
                if stats.total_movements_today > 10:
                    alerts.append({
                        'type': 'high_activity',
                        'item': item.name,
                        'movements': stats.total_movements_today,
                        'message': f"{item.name} has had {stats.total_movements_today} price movements today"
                    })
                
                # Alert if significant net movement
                if abs(stats.net_movement_today) > 5:
                    direction = "increased" if stats.net_movement_today > 0 else "decreased"
                    alerts.append({
                        'type': 'significant_movement',
                        'item': item.name,
                        'net_movement': stats.net_movement_today,
                        'message': f"{item.name} has {direction} {abs(stats.net_movement_today)} times today"
                    })
                    
            except Exception as e:
                logger.error(f"Error checking alerts for {item.name}: {e}")
        
        if alerts:
            logger.info(f"Generated {len(alerts)} price alerts")
            # Here you could send notifications, emails, etc.
        
        return alerts
        
    except Exception as e:
        logger.error(f"Error generating price alerts: {e}")
        return []


@shared_task
def update_price_statistics():
    """Update daily, weekly, and monthly price statistics"""
    try:
        from .models import PriceMovementStats, InvestmentItem
        from datetime import timedelta
        
        items = InvestmentItem.objects.filter(is_active=True)
        updated_count = 0
        
        for item in items:
            try:
                stats = PriceMovementStats.get_or_create_today_stats(item)
                
                # Update weekly and monthly counters
                # This is a simplified version - in production you'd want more sophisticated logic
                stats.increases_this_week = stats.increases_today
                stats.decreases_this_week = stats.decreases_today
                stats.unchanged_this_week = stats.unchanged_today
                
                stats.increases_this_month = stats.increases_today
                stats.decreases_this_month = stats.decreases_today
                stats.unchanged_this_month = stats.unchanged_today
                
                stats.save()
                updated_count += 1
                
            except Exception as e:
                logger.error(f"Error updating statistics for {item.name}: {e}")
        
        logger.info(f"Updated statistics for {updated_count} items")
        return updated_count
        
    except Exception as e:
        logger.error(f"Error updating price statistics: {e}")
        return 0
