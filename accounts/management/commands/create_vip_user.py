from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import CustomerProfile, VIPProfile, StaffProfile
import uuid


class Command(BaseCommand):
    help = 'Create a VIP user for testing'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Username for VIP user', default='vip_test')
        parser.add_argument('--email', type=str, help='Email for VIP user', default='vip@example.com')
        parser.add_argument('--password', type=str, help='Password for VIP user', default='vip123456')
        parser.add_argument('--first-name', type=str, help='First name', default='VIP')
        parser.add_argument('--last-name', type=str, help='Last name', default='User')
        parser.add_argument('--tier', type=str, default='gold', choices=['bronze', 'silver', 'gold', 'platinum', 'diamond'], help='VIP membership tier')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']
        first_name = options['first_name']
        last_name = options['last_name']
        tier = options['tier']

        # Create user
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'is_staff': False,
                'is_active': True,
            }
        )

        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created VIP user: {username}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'VIP user already exists: {username}')
            )

        # Create customer profile
        profile, profile_created = CustomerProfile.objects.get_or_create(
            user=user,
            defaults={
                'phone_number': '+1-555-0123',
                'address': 'VIP Address',
                'city': 'VIP City',
                'state': 'VIP State',
                'country': 'USA',
                'postal_code': '12345',
            }
        )

        if profile_created:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created customer profile for: {username}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Customer profile already exists for: {username}')
            )

        # Create VIP profile
        vip_profile, vip_created = VIPProfile.objects.get_or_create(
            user=user,
            defaults={
                'membership_tier': tier,
                'status': 'active',
                'total_investments': 50000.00,
                'monthly_income': 5000.00,
                'net_worth': 100000.00,
                'priority_support': True,
                'dedicated_account_manager': True,
                'exclusive_investment_opportunities': True,
                'faster_processing': True,
                'notes': 'Auto-generated VIP member for testing'
            }
        )
        
        if vip_created:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created VIP profile for: {username}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'VIP profile already exists for: {username}')
            )

        # Try to assign a staff member (get first available staff)
        if not vip_profile.assigned_staff:
            staff = StaffProfile.objects.filter(is_active_staff=True).first()
            if staff:
                vip_profile.assigned_staff = staff
                vip_profile.save()
                self.stdout.write(
                    self.style.SUCCESS(f'Assigned staff member: {staff.user.get_full_name()}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nVIP User Details:\n'
                f'Username: {username}\n'
                f'Email: {email}\n'
                f'Password: {password}\n'
                f'VIP Tier: {vip_profile.get_membership_tier_display()}\n'
                f'VIP Status: {vip_profile.get_status_display()}\n'
                f'Member ID: {vip_profile.member_id}\n'
                f'Login URL: /accounts/vip/login/\n'
            )
        )
