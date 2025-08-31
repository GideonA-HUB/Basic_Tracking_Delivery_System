from celery import shared_task
from django.utils import timezone
from django.contrib.auth.models import User
from .models import AutoInvestmentPlan, RealTimePriceFeed, UserInvestment, InvestmentItem
from .price_services import PriceFeedService, CurrencyConversionService


@shared_task
def process_auto_investments():
    """Process auto-investment plans that are due"""
    due_plans = AutoInvestmentPlan.objects.filter(
        status='active',
        next_investment_date__lte=timezone.now().date()
    )
    
    processed_count = 0
    for plan in due_plans:
        try:
            # Check if user has sufficient funds (this would integrate with payment system)
            # For now, we'll just mark the plan as processed
            
            # Create investment record
            investment = UserInvestment.objects.create(
                user=plan.user,
                item=plan.target_asset,
                investment_amount_usd=plan.investment_amount,
                quantity=plan.investment_amount / plan.target_asset.current_price_usd,
                purchase_price_per_unit=plan.target_asset.current_price_usd,
                investment_type='hold',
                status='active'
            )
            
            # Update plan statistics
            plan.total_invested += plan.investment_amount
            plan.investments_count += 1
            plan.last_investment_at = timezone.now()
            plan.next_investment_date = plan.calculate_next_investment_date()
            plan.save()
            
            # Update user portfolio
            portfolio, created = plan.user.investment_portfolio_set.get_or_create(
                user=plan.user,
                defaults={
                    'total_invested': 0,
                    'current_value': 0,
                    'total_return': 0,
                    'total_return_percentage': 0,
                    'active_investments_count': 0,
                    'total_investments_count': 0
                }
            )
            portfolio.update_portfolio_summary()
            
            processed_count += 1
            print(f"Processed auto-investment for {plan.user.username}: ${plan.investment_amount}")
            
        except Exception as e:
            print(f"Error processing auto-investment for {plan.user.username}: {e}")
            continue
    
    return f"Processed {processed_count} auto-investments"


@shared_task
def update_price_feeds():
    """Update all price feeds"""
    try:
        # This would be called asynchronously
        # For now, we'll use the synchronous version
        PriceFeedService.update_all_price_feeds()
        return "Price feeds updated successfully"
    except Exception as e:
        print(f"Error updating price feeds: {e}")
        return f"Error: {e}"


@shared_task
def update_exchange_rates():
    """Update currency exchange rates"""
    try:
        # This would be called asynchronously
        # For now, we'll use the synchronous version
        CurrencyConversionService.update_exchange_rates()
        return "Exchange rates updated successfully"
    except Exception as e:
        print(f"Error updating exchange rates: {e}")
        return f"Error: {e}"


@shared_task
def create_sample_price_feeds():
    """Create sample price feeds for testing"""
    try:
        feeds = PriceFeedService.create_sample_price_feeds()
        return f"Created {len(feeds)} sample price feeds"
    except Exception as e:
        print(f"Error creating sample price feeds: {e}")
        return f"Error: {e}"


@shared_task
def update_user_portfolios():
    """Update all user portfolios with current values"""
    try:
        from .models import InvestmentPortfolio
        
        portfolios = InvestmentPortfolio.objects.all()
        updated_count = 0
        
        for portfolio in portfolios:
            try:
                portfolio.update_portfolio_summary()
                updated_count += 1
            except Exception as e:
                print(f"Error updating portfolio for {portfolio.user.username}: {e}")
                continue
        
        return f"Updated {updated_count} portfolios"
    except Exception as e:
        print(f"Error updating portfolios: {e}")
        return f"Error: {e}"
