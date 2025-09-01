#!/usr/bin/env python3
"""
Comprehensive script to populate the investment system with sample data
This will create user investments, portfolios, and demonstrate all features
"""

import os
import sys
import django
from decimal import Decimal
from datetime import datetime, timedelta
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from investments.models import (
    InvestmentCategory, InvestmentItem, UserInvestment, InvestmentPortfolio,
    InvestmentTransaction, RealTimePriceFeed, RealTimePriceHistory,
    AutoInvestmentPlan, CurrencyConversion, CustomerCashoutRequest
)
from accounts.models import CustomerProfile, StaffProfile


def create_sample_users():
    """Create sample users for testing"""
    print("Creating sample users...")
    
    # Create a customer user
    customer, created = User.objects.get_or_create(
        username='testcustomer',
        defaults={
            'email': 'customer@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'is_staff': False
        }
    )
    if created:
        customer.set_password('testpass123')
        customer.save()
        print(f"✅ Created customer: {customer.get_full_name()}")
    
    # Create a staff user (customer care)
    staff, created = User.objects.get_or_create(
        username='customercare',
        defaults={
            'email': 'care@example.com',
            'first_name': 'Sarah',
            'last_name': 'Johnson',
            'is_staff': True
        }
    )
    if created:
        staff.set_password('testpass123')
        staff.save()
        print(f"✅ Created staff: {staff.get_full_name()}")
    
    return customer, staff


def create_sample_investments(customer):
    """Create sample user investments"""
    print("\nCreating sample user investments...")
    
    # Get some investment items
    items = InvestmentItem.objects.filter(is_active=True)[:5]
    
    if not items.exists():
        print("❌ No investment items found. Please create some items first.")
        return
    
    investments_created = []
    
    for i, item in enumerate(items):
        # Create investment with realistic data
        investment_amount = Decimal(random.uniform(100, 5000))
        quantity = investment_amount / item.current_price_usd
        
        investment = UserInvestment.objects.create(
            user=customer,
            item=item,
            investment_amount_usd=investment_amount,
            quantity=quantity,
            purchase_price_per_unit=item.current_price_usd,
            investment_type='hold' if i % 2 == 0 else 'delivery',
            status='active'
        )
        
        # Update current value based on current price
        investment.current_value_usd = quantity * item.current_price_usd
        investment.total_return_usd = investment.current_value_usd - investment_amount
        if investment_amount > 0:
            investment.total_return_percentage = (investment.total_return_usd / investment_amount) * 100
        investment.save()
        
        investments_created.append(investment)
        print(f"✅ Created investment: {item.name} - ${investment_amount}")
    
    return investments_created


def create_sample_portfolio(customer):
    """Create or update user portfolio"""
    print("\nCreating user portfolio...")
    
    portfolio, created = InvestmentPortfolio.objects.get_or_create(user=customer)
    portfolio.update_portfolio_summary()
    
    print(f"✅ Portfolio created/updated:")
    print(f"   - Total Invested: ${portfolio.total_invested}")
    print(f"   - Current Value: ${portfolio.current_value}")
    print(f"   - Total Return: {portfolio.total_return_display}")
    print(f"   - Return %: {portfolio.total_return_percentage_display}")
    
    return portfolio


def create_sample_transactions(customer, investments):
    """Create sample transactions"""
    print("\nCreating sample transactions...")
    
    for investment in investments:
        # Create purchase transaction
        transaction = InvestmentTransaction.objects.create(
            user=customer,
            investment=investment,
            item=investment.item,
            transaction_type='purchase',
            amount_usd=investment.investment_amount_usd,
            quantity=investment.quantity,
            price_per_unit=investment.purchase_price_per_unit,
            payment_method='nowpayments',
            payment_status='completed',
            description=f"Purchase of {investment.item.name}",
            completed_at=timezone.now()
        )
        print(f"✅ Created transaction: {transaction.transaction_type} - ${transaction.amount_usd}")


def create_sample_auto_investment_plans(customer):
    """Create sample auto-investment plans"""
    print("\nCreating sample auto-investment plans...")
    
    items = InvestmentItem.objects.filter(is_active=True)[:2]
    
    for i, item in enumerate(items):
        plan = AutoInvestmentPlan.objects.create(
            user=customer,
            name=f"Auto-Invest in {item.name}",
            description=f"Automatically invest ${100 + i * 50} in {item.name} every month",
            investment_amount=Decimal(100 + i * 50),
            frequency='monthly',
            target_asset=item,
            start_date=timezone.now().date(),
            next_investment_date=timezone.now().date() + timedelta(days=30),
            status='active'
        )
        print(f"✅ Created auto-investment plan: {plan.name}")


def create_sample_cashout_requests(customer):
    """Create sample cashout requests"""
    print("\nCreating sample cashout requests...")
    
    # Create a pending cashout request
    cashout = CustomerCashoutRequest.objects.create(
        user=customer,
        amount_usd=Decimal('500.00'),
        requested_currency='USD',
        bank_account_details='Bank: Test Bank\nAccount: 1234567890\nRouting: 987654321',
        reason='Need funds for emergency expenses',
        status='pending'
    )
    print(f"✅ Created cashout request: ${cashout.amount_usd} - {cashout.get_status_display()}")


def update_real_time_prices():
    """Update real-time price feeds with realistic data"""
    print("\nUpdating real-time price feeds...")
    
    price_feeds = RealTimePriceFeed.objects.filter(is_active=True)
    
    for feed in price_feeds:
        # Simulate price changes
        current_price = float(feed.current_price)
        price_change_amount = random.uniform(-current_price * 0.05, current_price * 0.05)
        new_price = current_price + price_change_amount
        price_change_percentage = (price_change_amount / current_price) * 100 if current_price > 0 else 0
        
        feed.update_price(
            Decimal(str(new_price)), 
            Decimal(str(price_change_amount)), 
            Decimal(str(price_change_percentage))
        )
        print(f"✅ Updated {feed.name}: ${new_price:.2f} ({price_change_percentage:+.2f}%)")


def create_currency_conversions():
    """Create sample currency conversion rates"""
    print("\nCreating currency conversion rates...")
    
    conversions = [
        ('USD', 'EUR', Decimal('0.85')),
        ('USD', 'GBP', Decimal('0.73')),
        ('USD', 'NGN', Decimal('460.50')),
        ('USD', 'BTC', Decimal('0.000022')),
        ('USD', 'ETH', Decimal('0.000357')),
        ('EUR', 'USD', Decimal('1.18')),
        ('GBP', 'USD', Decimal('1.37')),
        ('NGN', 'USD', Decimal('0.00217')),
    ]
    
    for from_curr, to_curr, rate in conversions:
        conversion, created = CurrencyConversion.objects.get_or_create(
            from_currency=from_curr,
            to_currency=to_curr,
            defaults={'exchange_rate': rate, 'api_source': 'manual'}
        )
        if created:
            print(f"✅ Created conversion: {from_curr} to {to_curr}: {rate}")


def create_price_history():
    """Create sample price history data"""
    print("\nCreating price history data...")
    
    price_feeds = RealTimePriceFeed.objects.filter(is_active=True)
    
    for feed in price_feeds:
        # Create historical data for the last 30 days
        base_price = float(feed.current_price)
        for i in range(30):
            date = timezone.now() - timedelta(days=30-i)
            # Simulate realistic price movements
            price_change_amount = random.uniform(-base_price * 0.02, base_price * 0.02)
            price = base_price + price_change_amount
            change_percentage = (price_change_amount / base_price) * 100 if base_price > 0 else 0
            
            RealTimePriceHistory.objects.create(
                price_feed=feed,
                price=Decimal(str(price)),
                change_amount=Decimal(str(price_change_amount)),
                change_percentage=Decimal(str(change_percentage)),
                timestamp=date
            )
        
        print(f"✅ Created price history for {feed.name}")


def main():
    """Main function to populate all data"""
    print("🚀 POPULATING INVESTMENT SYSTEM WITH SAMPLE DATA")
    print("=" * 60)
    
    try:
        # Create users
        customer, staff = create_sample_users()
        
        # Create investments
        investments = create_sample_investments(customer)
        
        if investments:
            # Create portfolio
            portfolio = create_sample_portfolio(customer)
            
            # Create transactions
            create_sample_transactions(customer, investments)
            
            # Create auto-investment plans
            create_sample_auto_investment_plans(customer)
            
            # Create cashout requests
            create_sample_cashout_requests(customer)
        
        # Update real-time prices
        update_real_time_prices()
        
        # Create currency conversions
        create_currency_conversions()
        
        # Create price history
        create_price_history()
        
        print("\n" + "=" * 60)
        print("🎉 SAMPLE DATA POPULATION COMPLETED!")
        print("\n📊 SUMMARY:")
        print(f"   - Customer: {customer.get_full_name()} ({customer.email})")
        print(f"   - Staff: {staff.get_full_name()} ({staff.email})")
        print(f"   - Investments created: {len(investments) if investments else 0}")
        print(f"   - Portfolio value: ${portfolio.current_value if 'portfolio' in locals() else 0}")
        
        print("\n🔑 LOGIN CREDENTIALS:")
        print(f"   Customer: username='testcustomer', password='testpass123'")
        print(f"   Staff: username='customercare', password='testpass123'")
        
        print("\n🌐 NEXT STEPS:")
        print("   1. Login as customer to see the populated dashboard")
        print("   2. Check the investment marketplace for items")
        print("   3. View the portfolio with real data")
        print("   4. Login as staff to approve cashout requests")
        print("   5. Test real-time price updates")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
