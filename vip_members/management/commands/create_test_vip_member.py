from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from vip_members.models import VIPMember, VIPStaff, VIPActivity, VIPNotification


class Command(BaseCommand):
    help = 'Create a test VIP member for demonstration'

    def handle(self, *args, **options):
        self.stdout.write('Creating test VIP member...')
        
        # Get or create a test user
        test_user, created = User.objects.get_or_create(
            username='vip_test_user',
            defaults={
                'email': 'vip_test@example.com',
                'first_name': 'John',
                'last_name': 'VIP Member',
                'is_active': True
            }
        )
        
        if created:
            test_user.set_password('testpass123')
            test_user.save()
            self.stdout.write(f'Created test user: {test_user.username}')
        else:
            self.stdout.write(f'Test user already exists: {test_user.username}')
        
        # Get the first VIP staff member
        vip_staff = VIPStaff.objects.first()
        
        # Create VIP member
        vip_member, created = VIPMember.objects.get_or_create(
            customer=test_user,
            defaults={
                'member_id': f'VIP{test_user.id:06d}',
                'assigned_staff': vip_staff,
                'membership_tier': 'gold',
                'status': 'active',
                'phone': '+1-555-0123',
                'preferred_contact_method': 'email',
                'total_investments': 50000.00,
                'monthly_income': 10000.00,
                'net_worth': 250000.00,
                'priority_support': True,
                'dedicated_account_manager': True,
                'exclusive_investment_opportunities': True,
                'faster_processing': True,
                'notes': 'Test VIP member for demonstration purposes'
            }
        )
        
        if created:
            self.stdout.write(f'Created VIP member: {vip_member.full_name}')
            
            # Create some sample activities
            activities = [
                {
                    'activity_type': 'login',
                    'title': 'Dashboard Access',
                    'description': 'Logged into VIP dashboard',
                },
                {
                    'activity_type': 'investment',
                    'title': 'New Investment',
                    'description': 'Invested $10,000 in Bitcoin',
                },
                {
                    'activity_type': 'support',
                    'title': 'Support Contact',
                    'description': 'Contacted VIP support for account inquiry',
                },
                {
                    'activity_type': 'meeting',
                    'title': 'Account Review Meeting',
                    'description': 'Scheduled meeting with account manager',
                }
            ]
            
            for activity_data in activities:
                VIPActivity.objects.create(
                    member=vip_member,
                    staff_member=vip_staff,
                    **activity_data
                )
            
            # Create some sample notifications
            notifications = [
                {
                    'title': 'Welcome to VIP!',
                    'message': 'Congratulations on your Gold VIP membership. Enjoy exclusive benefits and priority support.',
                    'notification_type': 'success'
                },
                {
                    'title': 'Investment Opportunity',
                    'message': 'New exclusive investment opportunity available for Gold VIP members.',
                    'notification_type': 'info'
                },
                {
                    'title': 'Account Manager Assigned',
                    'message': f'Your dedicated account manager {vip_staff.full_name if vip_staff else "Sarah Johnson"} is ready to assist you.',
                    'notification_type': 'info'
                }
            ]
            
            for notification_data in notifications:
                VIPNotification.objects.create(
                    member=vip_member,
                    **notification_data
                )
            
            self.stdout.write('Created sample activities and notifications')
            
        else:
            self.stdout.write(f'VIP member already exists: {vip_member.full_name}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Test VIP member setup completed!')
        )
        self.stdout.write(
            self.style.SUCCESS(f'Username: {test_user.username}')
        )
        self.stdout.write(
            self.style.SUCCESS(f'Password: testpass123')
        )
        self.stdout.write(
            self.style.SUCCESS(f'Login URL: /accounts/login/')
        )
        self.stdout.write(
            self.style.SUCCESS(f'VIP Dashboard: /vip-members/dashboard/')
        )
