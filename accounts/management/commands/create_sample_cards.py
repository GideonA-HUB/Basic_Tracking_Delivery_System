from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import VIPProfile, Card
from datetime import datetime, timedelta
import random


class Command(BaseCommand):
    help = 'Create sample card data for VIP members'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=5,
            help='Number of sample cards to create per VIP member',
        )

    def handle(self, *args, **options):
        count = options['count']
        
        # Get all VIP members
        vip_members = VIPProfile.objects.all()
        
        if not vip_members.exists():
            self.stdout.write(
                self.style.WARNING('No VIP members found. Please create VIP members first.')
            )
            return
        
        cards_created = 0
        
        # Card brands and their descriptions
        card_brands = [
            ('visa', 'Visa'),
            ('mastercard', 'Mastercard'),
            ('amex', 'American Express'),
        ]
        
        # Card levels and fees
        card_levels = [
            ('standard', 'Standard - $5.00'),
            ('gold', 'Gold - $15.00'),
            ('platinum', 'Platinum - $25.00'),
            ('black', 'Black - $50.00'),
        ]
        
        # Currencies
        currencies = ['USD', 'EUR', 'GBP']
        
        # Status choices
        statuses = ['active', 'pending', 'inactive', 'suspended']
        
        for vip_member in vip_members:
            self.stdout.write(f'Creating cards for VIP member: {vip_member.user.username}')
            
            for i in range(count):
                # Random selections
                card_brand, brand_name = random.choice(card_brands)
                card_level, level_name = random.choice(card_levels)
                currency = random.choice(currencies)
                status = random.choice(statuses)
                
                # Generate card number
                last_four = str(random.randint(1000, 9999))
                card_number = f"**** **** **** {last_four}"
                
                # Generate expiry date (1-3 years from now)
                expiry_months = random.randint(12, 36)
                expiry_date = datetime.now() + timedelta(days=expiry_months * 30)
                expiry_month = str(expiry_date.month).zfill(2)
                expiry_year = str(expiry_date.year)
                
                # Generate spending limits based on card level
                if card_level == 'standard':
                    daily_limit = random.randint(1000, 3000)
                    monthly_limit = daily_limit * 30
                elif card_level == 'gold':
                    daily_limit = random.randint(3000, 5000)
                    monthly_limit = daily_limit * 30
                elif card_level == 'platinum':
                    daily_limit = random.randint(5000, 8000)
                    monthly_limit = daily_limit * 30
                else:  # black
                    daily_limit = random.randint(8000, 10000)
                    monthly_limit = daily_limit * 30
                
                # Generate current balance (usually 0 for new cards)
                current_balance = random.randint(0, 1000) if status == 'active' else 0
                
                # Generate application fee based on card level
                fee_map = {
                    'standard': 5.00,
                    'gold': 15.00,
                    'platinum': 25.00,
                    'black': 50.00,
                }
                application_fee = fee_map[card_level]
                
                # Create the card
                card = Card.objects.create(
                    vip_member=vip_member,
                    card_number=card_number,
                    card_type='virtual',
                    card_brand=card_brand,
                    card_level=card_level,
                    status=status,
                    card_name=f"{vip_member.user.get_full_name()}",
                    expiry_month=expiry_month,
                    expiry_year=expiry_year,
                    spending_limit=monthly_limit,
                    daily_spending_limit=daily_limit,
                    current_balance=current_balance,
                    currency=currency,
                    cardholder_name=f"{vip_member.user.get_full_name()}",
                    billing_address=f"123 Main Street, New York, NY 10001, USA",
                    application_fee=application_fee,
                    terms_accepted=True,
                    expiry_date=expiry_date,
                    description=f"{brand_name} {level_name.split(' - ')[0]} Virtual Card",
                    notes=f"Sample card created for testing purposes - {brand_name} {level_name}"
                )
                
                cards_created += 1
                
                self.stdout.write(
                    f'  Created card: {card_number} ({brand_name} {level_name.split(" - ")[0]}) - Status: {status}'
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {cards_created} sample cards!')
        )
