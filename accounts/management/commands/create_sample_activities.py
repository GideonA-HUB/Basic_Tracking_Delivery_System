from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from accounts.models import VIPProfile, RecentActivity


class Command(BaseCommand):
    help = 'Create sample recent activities for VIP members'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Username of the VIP member to create activities for',
            default='vip_demo'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing activities before creating new ones',
        )

    def handle(self, *args, **options):
        username = options['username']
        clear_existing = options['clear']
        
        try:
            # Get VIP profile
            vip_profile = VIPProfile.objects.get(user__username=username)
            self.stdout.write(f'Found VIP member: {vip_profile.user.get_full_name()}')
            
            # Clear existing activities if requested
            if clear_existing:
                deleted_count = vip_profile.recent_activities.count()
                vip_profile.recent_activities.all().delete()
                self.stdout.write(f'Deleted {deleted_count} existing activities')
            
            # Create sample activities
            now = timezone.now()
            activities_data = [
                {
                    'title': 'Investment Return',
                    'activity_type': 'investment_return',
                    'amount': 5420.00,
                    'status': 'completed',
                    'activity_date': now - timedelta(days=1),
                    'display_order': 100,
                    'is_featured': False,
                },
                {
                    'title': 'International Wire Transfer',
                    'activity_type': 'wire_transfer',
                    'amount': -12500.00,
                    'status': 'completed',
                    'activity_date': now - timedelta(days=2),
                    'display_order': 90,
                    'is_featured': True,
                },
                {
                    'title': 'Dividend Payment',
                    'activity_type': 'dividend_payment',
                    'amount': 2100.00,
                    'status': 'completed',
                    'activity_date': now - timedelta(days=3),
                    'display_order': 80,
                    'is_featured': False,
                },
                {
                    'title': 'Service Fee',
                    'activity_type': 'service_fee',
                    'amount': -25.00,
                    'status': 'pending',
                    'activity_date': now - timedelta(days=4),
                    'display_order': 70,
                    'is_featured': False,
                },
                {
                    'title': 'Deposit',
                    'activity_type': 'deposit',
                    'amount': 5000.00,
                    'status': 'completed',
                    'activity_date': now - timedelta(days=5),
                    'display_order': 60,
                    'is_featured': False,
                },
                {
                    'title': 'Loan Payment',
                    'activity_type': 'loan_payment',
                    'amount': -1500.00,
                    'status': 'completed',
                    'activity_date': now - timedelta(days=7),
                    'display_order': 50,
                    'is_featured': False,
                },
                {
                    'title': 'Interest Payment',
                    'activity_type': 'interest_payment',
                    'amount': 750.00,
                    'status': 'completed',
                    'activity_date': now - timedelta(days=10),
                    'display_order': 40,
                    'is_featured': False,
                },
                {
                    'title': 'Commission',
                    'activity_type': 'commission',
                    'amount': 320.00,
                    'status': 'completed',
                    'activity_date': now - timedelta(days=12),
                    'display_order': 30,
                    'is_featured': False,
                },
            ]
            
            created_count = 0
            for activity_data in activities_data:
                activity = RecentActivity.objects.create(
                    vip_member=vip_profile,
                    **activity_data
                )
                created_count += 1
                self.stdout.write(f'Created: {activity.title} - {activity.formatted_amount}')
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created {created_count} sample activities for {username}'
                )
            )
            
            # Show current activities
            total_activities = vip_profile.recent_activities.count()
            active_activities = vip_profile.recent_activities.filter(is_active=True).count()
            self.stdout.write(f'Total activities: {total_activities}')
            self.stdout.write(f'Active activities: {active_activities}')
            
        except VIPProfile.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'VIP profile not found for username: {username}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating sample activities: {str(e)}')
            )
