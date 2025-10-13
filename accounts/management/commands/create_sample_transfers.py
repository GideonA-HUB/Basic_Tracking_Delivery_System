from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import VIPProfile, LocalTransfer
from datetime import datetime, timedelta
import random


class Command(BaseCommand):
    help = 'Create sample local transfer data for VIP members'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=5,
            help='Number of sample transfers to create per VIP member',
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
        
        transfers_created = 0
        
        # Transfer types
        transfer_types = [
            ('online_banking', 'Online Banking'),
            ('joint_account', 'Joint Account'),
            ('checking', 'Checking'),
            ('savings', 'Savings Account'),
        ]
        
        # Currencies
        currencies = ['USD', 'EUR', 'GBP']
        
        # Status choices
        statuses = ['pending', 'processing', 'completed', 'failed']
        
        # Sample bank names
        bank_names = [
            'Chase Bank', 'Bank of America', 'Wells Fargo', 'Citibank',
            'US Bank', 'PNC Bank', 'Capital One', 'TD Bank',
            'HSBC Bank', 'Barclays Bank', 'Deutsche Bank', 'Santander Bank'
        ]
        
        # Sample beneficiary names
        beneficiary_names = [
            'John Smith', 'Sarah Johnson', 'Michael Brown', 'Emily Davis',
            'David Wilson', 'Lisa Anderson', 'Robert Taylor', 'Jennifer Thomas',
            'William Jackson', 'Mary White', 'James Harris', 'Linda Martin',
            'Christopher Thompson', 'Patricia Garcia', 'Daniel Martinez', 'Barbara Robinson'
        ]
        
        for vip_member in vip_members:
            self.stdout.write(f'Creating transfers for VIP member: {vip_member.user.username}')
            
            for i in range(count):
                # Random selections
                transfer_type, type_name = random.choice(transfer_types)
                currency = random.choice(currencies)
                status = random.choice(statuses)
                bank_name = random.choice(bank_names)
                beneficiary_name = random.choice(beneficiary_names)
                
                # Generate transfer amount
                amount = random.uniform(100, 5000)
                
                # Generate account number
                account_number = str(random.randint(10000000, 99999999))
                
                # Generate transfer date (within last 30 days)
                days_ago = random.randint(1, 30)
                transfer_date = datetime.now() - timedelta(days=days_ago)
                
                # Calculate transfer fee (1% of amount, minimum $5, maximum $50)
                fee_percentage = 0.01
                calculated_fee = amount * fee_percentage
                transfer_fee = max(5.00, min(calculated_fee, 50.00))
                
                # Generate description
                descriptions = [
                    f'Payment for {type_name}',
                    'Monthly bill payment',
                    'Transfer to savings',
                    'Emergency fund transfer',
                    'Investment allocation',
                    'Personal expense',
                    'Business payment',
                    'Family support'
                ]
                description = random.choice(descriptions)
                
                # Create the transfer
                transfer = LocalTransfer.objects.create(
                    vip_member=vip_member,
                    transfer_amount=amount,
                    currency=currency,
                    beneficiary_name=beneficiary_name,
                    beneficiary_account_number=account_number,
                    bank_name=bank_name,
                    transfer_type=transfer_type,
                    description=description,
                    status=status,
                    transfer_fee=transfer_fee,
                    transfer_date=transfer_date,
                    notes=f"Sample transfer created for testing purposes - {type_name}"
                )
                
                transfers_created += 1
                
                self.stdout.write(
                    f'  Created transfer: {transfer.reference_number} - ${amount:.2f} to {beneficiary_name} ({status})'
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {transfers_created} sample transfers!')
        )
