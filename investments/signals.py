from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import UserInvestment, InvestmentTransaction, InvestmentPortfolio


@receiver(post_save, sender=UserInvestment)
def update_portfolio_on_investment_change(sender, instance, created, **kwargs):
    """Update user portfolio when investment changes"""
    try:
        if hasattr(instance.user, 'investment_portfolio'):
            instance.user.investment_portfolio.update_portfolio_summary()
    except Exception as e:
        # Log error but don't fail the save operation
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to update portfolio: {e}")


@receiver(post_delete, sender=UserInvestment)
def update_portfolio_on_investment_delete(sender, instance, **kwargs):
    """Update user portfolio when investment is deleted"""
    try:
        if hasattr(instance.user, 'investment_portfolio'):
            instance.user.investment_portfolio.update_portfolio_summary()
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to update portfolio after deletion: {e}")


@receiver(post_save, sender=InvestmentTransaction)
def update_portfolio_on_transaction_change(sender, instance, created, **kwargs):
    """Update user portfolio when transaction changes"""
    try:
        if hasattr(instance.user, 'investment_portfolio'):
            instance.user.investment_portfolio.update_portfolio_summary()
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to update portfolio after transaction: {e}")
