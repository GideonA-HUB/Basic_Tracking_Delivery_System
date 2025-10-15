from django.core.management.base import BaseCommand
from accounts.models import VIPProfile, VIPFinancialMetrics
import random


class Command(BaseCommand):
    help = 'Create financial metrics for existing VIP members'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset existing financial metrics',
        )

    def handle(self, *args, **options):
        if options['reset']:
            VIPFinancialMetrics.objects.all().delete()
            self.stdout.write(
                self.style.WARNING('All existing financial metrics have been deleted.')
            )

        vip_members = VIPProfile.objects.all()
        created_count = 0
        updated_count = 0

        for vip_member in vip_members:
            # Check if financial metrics already exist
            financial_metrics, created = VIPFinancialMetrics.objects.get_or_create(
                vip_member=vip_member,
                defaults={
                    'current_balance': round(random.uniform(1000, 50000), 2),
                    'available_balance': round(random.uniform(1000, 50000), 2),
                    'pending_balance': round(random.uniform(0, 5000), 2),
                    'monthly_income': round(random.uniform(5000, 25000), 2),
                    'monthly_outgoing': round(random.uniform(2000, 15000), 2),
                    'monthly_savings': round(random.uniform(1000, 8000), 2),
                    'total_investments': round(random.uniform(10000, 100000), 2),
                    'net_worth': round(random.uniform(50000, 500000), 2),
                    'investment_growth': round(random.uniform(0, 15), 2),
                    'transaction_limit': round(random.uniform(10000, 100000), 2),
                    'monthly_transaction_limit': round(random.uniform(50000, 500000), 2),
                    'pending_transactions': round(random.uniform(0, 10000), 2),
                    'transaction_volume': round(random.uniform(5000, 50000), 2),
                    'account_status': random.choice(['active', 'inactive', 'under_review']),
                    'credit_score': random.randint(600, 850),
                    'risk_level': random.choice(['low', 'medium', 'high']),
                    'primary_currency': random.choice(['USD', 'EUR', 'GBP']),
                    'exchange_rate': round(random.uniform(0.8, 1.2), 6),
                }
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created financial metrics for {vip_member.full_name}')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Financial metrics already exist for {vip_member.full_name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully processed {len(vip_members)} VIP members. '
                f'Created: {created_count}, Already existed: {updated_count}'
            )
        )
