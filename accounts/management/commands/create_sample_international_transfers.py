from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import VIPProfile, InternationalTransfer
import random
from decimal import Decimal


class Command(BaseCommand):
    help = 'Create sample international transfers for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=5,
            help='Number of international transfers to create per VIP member'
        )

    def handle(self, *args, **options):
        count = options['count']
        
        # Get all VIP profiles
        vip_profiles = VIPProfile.objects.all()
        
        if not vip_profiles.exists():
            self.stdout.write(
                self.style.WARNING('No VIP profiles found. Please create VIP profiles first.')
            )
            return
        
        # Sample data for international transfers
        transfer_methods = [
            'wire_transfer', 'cryptocurrency', 'paypal', 'wise_transfer', 
            'cash_app', 'skrill', 'venmo', 'zelle', 'revolut', 'alipay', 'wechat_pay'
        ]
        
        currencies = ['USD', 'EUR', 'GBP', 'CAD', 'AUD', 'JPY', 'CHF', 'CNY']
        
        statuses = ['pending', 'processing', 'completed', 'failed', 'cancelled', 'on_hold']
        
        recipient_names = [
            'John Smith', 'Maria Garcia', 'David Johnson', 'Sarah Wilson',
            'Michael Brown', 'Emily Davis', 'Christopher Miller', 'Jessica Taylor',
            'Daniel Anderson', 'Ashley Thomas', 'Matthew Jackson', 'Amanda White',
            'James Harris', 'Jennifer Martin', 'Robert Thompson', 'Lisa Garcia'
        ]
        
        bank_names = [
            'Chase Bank', 'Bank of America', 'Wells Fargo', 'Citibank',
            'HSBC Bank', 'Barclays Bank', 'Deutsche Bank', 'BNP Paribas',
            'Royal Bank of Canada', 'Commonwealth Bank', 'Mizuho Bank', 'UBS'
        ]
        
        purposes = [
            'Business Payment', 'Family Support', 'Education Fees', 'Medical Expenses',
            'Investment', 'Property Purchase', 'Travel Expenses', 'Emergency Fund',
            'Charity Donation', 'Loan Repayment', 'Salary Payment', 'Consulting Fees'
        ]
        
        wallet_types = [
            'Bitcoin', 'Ethereum', 'Litecoin', 'Ripple', 'Bitcoin Cash', 'Cardano'
        ]
        
        created_count = 0
        
        for vip_profile in vip_profiles:
            self.stdout.write(f'Creating international transfers for VIP member: {vip_profile.user.username}')
            
            for i in range(count):
                transfer_method = random.choice(transfer_methods)
                currency = random.choice(currencies)
                status = random.choice(statuses)
                recipient_name = random.choice(recipient_names)
                
                # Generate random amount
                transfer_amount = Decimal(str(round(random.uniform(100, 50000), 2)))
                
                # Calculate fees based on method
                if transfer_method == 'wire_transfer':
                    transfer_fee = max(Decimal('25.00'), transfer_amount * Decimal('0.005'))
                elif transfer_method == 'cryptocurrency':
                    transfer_fee = transfer_amount * Decimal('0.02')
                elif transfer_method in ['paypal', 'wise_transfer']:
                    transfer_fee = transfer_amount * Decimal('0.03')
                elif transfer_method in ['cash_app', 'venmo', 'zelle']:
                    transfer_fee = transfer_amount * Decimal('0.015')
                else:
                    transfer_fee = transfer_amount * Decimal('0.025')
                
                # Cap fees at $100
                transfer_fee = min(transfer_fee, Decimal('100.00'))
                total_amount = transfer_amount + transfer_fee
                
                # Create transfer
                transfer = InternationalTransfer.objects.create(
                    vip_member=vip_profile,
                    transfer_amount=transfer_amount,
                    currency=currency,
                    transfer_method=transfer_method,
                    recipient_name=recipient_name,
                    recipient_email=f"{recipient_name.lower().replace(' ', '.')}@example.com",
                    recipient_phone=f"+1-{random.randint(200, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                    bank_name=random.choice(bank_names) if transfer_method == 'wire_transfer' else None,
                    bank_address=f"{random.randint(100, 9999)} Main Street, City, Country" if transfer_method == 'wire_transfer' else None,
                    account_number=f"{random.randint(10000000, 99999999)}" if transfer_method == 'wire_transfer' else None,
                    routing_number=f"{random.randint(100000000, 999999999)}" if transfer_method == 'wire_transfer' else None,
                    swift_code=f"SWIFT{random.randint(1000000, 9999999)}" if transfer_method == 'wire_transfer' else None,
                    iban=f"IBAN{random.randint(100000000000000000000, 999999999999999999999)}" if transfer_method == 'wire_transfer' else None,
                    wallet_address=f"{random.choice(wallet_types)[:3].upper()}{random.randint(10000000, 99999999)}" if transfer_method == 'cryptocurrency' else None,
                    wallet_type=random.choice(wallet_types) if transfer_method == 'cryptocurrency' else None,
                    purpose_of_transfer=random.choice(purposes),
                    description=f"International transfer via {transfer_method.replace('_', ' ').title()}",
                    status=status,
                    transfer_fee=transfer_fee,
                    exchange_rate=Decimal(str(round(random.uniform(0.8, 1.2), 6))),
                    total_amount=total_amount,
                    notes=f"Sample international transfer #{i+1} for {vip_profile.user.username}",
                    compliance_notes="Compliance review completed" if status == 'completed' else None,
                    requires_approval=random.choice([True, False]),
                    is_active=True
                )
                
                self.stdout.write(f'  Created transfer: {transfer.reference_number} - {transfer.formatted_amount} via {transfer.get_transfer_method_display()} ({status})')
                created_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} sample international transfers!')
        )
