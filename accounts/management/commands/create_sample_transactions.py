import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from accounts.models import VIPProfile, Transaction


class Command(BaseCommand):
    help = 'Creates sample Transaction entries for a given VIP user or all VIP users.'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Username of the VIP member to create transactions for.')
        parser.add_argument('--count', type=int, default=20, help='Number of transactions to create per VIP member.')
        parser.add_argument('--clear', action='store_true', help='Clear existing transactions before creating new ones.')

    def handle(self, *args, **options):
        username = options['username']
        count = options['count']
        clear_existing = options['clear']

        if username:
            try:
                user = User.objects.get(username=username)
                vip_members = [VIPProfile.objects.get(user=user)]
            except (User.DoesNotExist, VIPProfile.DoesNotExist):
                self.stderr.write(self.style.ERROR(f"VIP user '{username}' not found."))
                return
        else:
            vip_members = VIPProfile.objects.all()
            if not vip_members.exists():
                self.stdout.write(self.style.WARNING("No VIP profiles found. Please create some VIP users first."))
                return

        for vip_member in vip_members:
            if clear_existing:
                vip_member.transactions.all().delete()
                self.stdout.write(self.style.SUCCESS(f"Cleared existing transactions for {vip_member.user.username}."))

            self.stdout.write(self.style.MIGRATE_HEADING(f"Creating {count} sample transactions for VIP member: {vip_member.user.username}"))

            for i in range(count):
                transaction_type = random.choice([
                    'deposit', 'withdrawal', 'transfer', 'investment', 'loan', 
                    'payment', 'refund', 'fee', 'interest', 'dividend', 'bonus', 'commission', 'other'
                ])
                
                status = random.choice(['completed', 'pending', 'failed', 'cancelled', 'processing', 'reversed'])
                scope = random.choice(['internal', 'external', 'international', 'local'])
                
                # Generate realistic amounts based on transaction type
                if transaction_type in ['deposit', 'investment', 'dividend', 'interest', 'bonus', 'commission', 'refund']:
                    amount = round(random.uniform(100.00, 50000.00), 2)
                elif transaction_type in ['withdrawal', 'fee', 'payment', 'loan']:
                    amount = round(random.uniform(-50000.00, -10.00), 2)
                else:
                    amount = round(random.uniform(-10000.00, 10000.00), 2)

                description_map = {
                    'deposit': 'Bank Deposit',
                    'withdrawal': 'Cash Withdrawal',
                    'transfer': 'Money Transfer',
                    'investment': 'Investment Purchase',
                    'loan': 'Loan Disbursement',
                    'payment': 'Bill Payment',
                    'refund': 'Purchase Refund',
                    'fee': 'Service Fee',
                    'interest': 'Interest Earned',
                    'dividend': 'Dividend Payment',
                    'bonus': 'Performance Bonus',
                    'commission': 'Sales Commission',
                    'other': 'Miscellaneous Transaction',
                }
                description = description_map.get(transaction_type, 'Transaction')

                transaction_date = timezone.now() - timedelta(days=random.randint(0, 90), hours=random.randint(0, 23))
                
                is_active = random.choice([True, True, True, False])  # Mostly active

                Transaction.objects.create(
                    vip_member=vip_member,
                    transaction_type=transaction_type,
                    amount=amount,
                    currency='USD',
                    status=status,
                    scope=scope,
                    description=description,
                    transaction_date=transaction_date,
                    is_active=is_active,
                )
                self.stdout.write(self.style.SUCCESS(f"  Created: {description} ({amount} USD) - {status}"))

        self.stdout.write(self.style.SUCCESS("Sample Transaction entries created successfully!"))
