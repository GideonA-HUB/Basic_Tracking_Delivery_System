#!/usr/bin/env python3
"""
Script to create investment data for the current user (Buchi Emma)
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


def find_or_create_buchi_emma():
    """Find or create the user 'Buchi Emma'"""
    print("Looking for user 'Buchi Emma'...")
    
    # Try to find existing user with similar name
    users = User.objects.all()
    for user in users:
        full_name = user.get_full_name()
        if 'buchi' in full_name.lower() or 'emma' in full_name.lower():
            print(f"Found user: {user.username} - {full_name}")
            return user
    
    # If not found, create the user
    print("Creating user 'Buchi Emma'...")
    user = User.objects.create_user(
        username='buchi_emma',
        email='buchi.emma@example.com',
        first_name='Buchi',
        last_name='Emma',
        is_staff=False
    )
    user.set_password('testpass123')
    user.save()
    
    # Create customer profile
    CustomerProfile.objects.get_or_create(
        user=user,
        defaults={
            'phone_number': '+2341234567890',
            'address': '123 Investment Street, Lagos, Nigeria',
            'city': 'Lagos',
            'state': 'Lagos',
            'country': 'Nigeria',
            'postal_code': '100001'
        }
    )
    
    print(f"✅ Created user: {user.get_full_name()} ({user.email})")
    return user


def create_investment_data_for_user(user):
    """Create comprehensive investment data for the specified user"""
    print(f"\nCreating investment data for {user.get_full_name()}...")
    
    # Get investment items
    items = InvestmentItem.objects.filter(is_active=True)[:5]
    
    if not items.exists():
        print("❌ No investment items found. Creating some items first...")
        create_sample_investment_items()
        items = InvestmentItem.objects.filter(is_active=True)[:5]
    
    investments_created = []
    
    for i, item in enumerate(items):
        # Create investment with realistic data
        investment_amount = Decimal(random.uniform(500, 3000))
        quantity = investment_amount / item.current_price_usd
        
        investment = UserInvestment.objects.create(
            user=user,
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


def create_sample_investment_items():
    """Create sample investment items if none exist"""
    print("Creating sample investment items...")
    
    # Create categories if they don't exist
    categories_data = [
        {'name': 'Precious Metals', 'description': 'Gold, Silver, Platinum'},
        {'name': 'Cryptocurrencies', 'description': 'Bitcoin, Ethereum, and other digital assets'},
        {'name': 'Real Estate', 'description': 'Real estate investment opportunities'},
        {'name': 'Diamonds & Gems', 'description': 'Precious stones and jewelry'},
        {'name': 'Art & Collectibles', 'description': 'Fine art and collectible items'},
    ]
    
    for cat_data in categories_data:
        category, created = InvestmentCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults={'description': cat_data['description']}
        )
        if created:
            print(f"✅ Created category: {category.name}")
    
    # Create investment items
    items_data = [
        {
            'name': 'Gold Bullion (1 oz)',
            'category': 'Precious Metals',
            'price': 1950.00,
            'description': 'Pure gold bullion bar, 1 troy ounce'
        },
        {
            'name': 'Silver Bullion (1 oz)',
            'category': 'Precious Metals',
            'price': 24.50,
            'description': 'Pure silver bullion bar, 1 troy ounce'
        },
        {
            'name': 'Bitcoin (BTC)',
            'category': 'Cryptocurrencies',
            'price': 45000.00,
            'description': 'Bitcoin cryptocurrency investment'
        },
        {
            'name': 'Ethereum (ETH)',
            'category': 'Cryptocurrencies',
            'price': 2800.00,
            'description': 'Ethereum cryptocurrency investment'
        },
        {
            'name': 'Investment Diamond (1 carat)',
            'category': 'Diamonds & Gems',
            'price': 8000.00,
            'description': 'High-quality investment diamond'
        },
    ]
    
    for item_data in items_data:
        category = InvestmentCategory.objects.get(name=item_data['category'])
        item, created = InvestmentItem.objects.get_or_create(
            name=item_data['name'],
            defaults={
                'category': category,
                'description': item_data['description'],
                'current_price_usd': item_data['price'],
                'minimum_investment': item_data['price'] * 0.1,  # 10% of price
                'investment_type': 'both',
                'is_active': True,
                'is_featured': True
            }
        )
        if created:
            print(f"✅ Created item: {item.name} - ${item.current_price_usd}")


def create_portfolio_for_user(user):
    """Create or update user portfolio"""
    print("\nCreating user portfolio...")
    
    portfolio, created = InvestmentPortfolio.objects.get_or_create(user=user)
    portfolio.update_portfolio_summary()
    
    print(f"✅ Portfolio created/updated:")
    print(f"   - Total Invested: ${portfolio.total_invested}")
    print(f"   - Current Value: ${portfolio.current_value}")
    print(f"   - Total Return: {portfolio.total_return_display}")
    print(f"   - Return %: {portfolio.total_return_percentage_display}")
    
    return portfolio


def create_transactions_for_user(user, investments):
    """Create transactions for user investments"""
    print("\nCreating transactions...")
    
    for investment in investments:
        transaction = InvestmentTransaction.objects.create(
            user=user,
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


def create_auto_investment_plans_for_user(user):
    """Create auto-investment plans for user"""
    print("\nCreating auto-investment plans...")
    
    items = InvestmentItem.objects.filter(is_active=True)[:2]
    
    for i, item in enumerate(items):
        plan = AutoInvestmentPlan.objects.create(
            user=user,
            name=f"Auto-Invest in {item.name}",
            description=f"Automatically invest ${200 + i * 100} in {item.name} every month",
            investment_amount=Decimal(200 + i * 100),
            frequency='monthly',
            target_asset=item,
            start_date=timezone.now().date(),
            next_investment_date=timezone.now().date() + timedelta(days=30),
            status='active'
        )
        print(f"✅ Created auto-investment plan: {plan.name}")


def create_cashout_request_for_user(user):
    """Create a cashout request for user"""
    print("\nCreating cashout request...")
    
    cashout = CustomerCashoutRequest.objects.create(
        user=user,
        amount_usd=Decimal('750.00'),
        requested_currency='USD',
        bank_account_details='Bank: First Bank Nigeria\nAccount: 1234567890\nRouting: 011234567',
        reason='Need funds for business expansion',
        status='pending'
    )
    print(f"✅ Created cashout request: ${cashout.amount_usd} - {cashout.get_status_display()}")


def main():
    """Main function"""
    print("🚀 CREATING INVESTMENT DATA FOR CURRENT USER")
    print("=" * 60)
    
    try:
        # Find or create the user
        user = find_or_create_buchi_emma()
        
        # Create investment data
        investments = create_investment_data_for_user(user)
        
        if investments:
            # Create portfolio
            portfolio = create_portfolio_for_user(user)
            
            # Create transactions
            create_transactions_for_user(user, investments)
            
            # Create auto-investment plans
            create_auto_investment_plans_for_user(user)
            
            # Create cashout request
            create_cashout_request_for_user(user)
        
        print("\n" + "=" * 60)
        print("🎉 INVESTMENT DATA CREATION COMPLETED!")
        print("\n📊 SUMMARY:")
        print(f"   - User: {user.get_full_name()} ({user.email})")
        print(f"   - Username: {user.username}")
        print(f"   - Password: testpass123")
        print(f"   - Investments created: {len(investments) if investments else 0}")
        print(f"   - Portfolio value: ${portfolio.current_value if 'portfolio' in locals() else 0}")
        
        print("\n🔑 LOGIN CREDENTIALS:")
        print(f"   Username: {user.username}")
        print(f"   Password: testpass123")
        
        print("\n🌐 NEXT STEPS:")
        print("   1. Login with the credentials above")
        print("   2. Check the investment dashboard")
        print("   3. Browse the marketplace")
        print("   4. Test the 'Add Funds' functionality")
        print("   5. View your portfolio")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
