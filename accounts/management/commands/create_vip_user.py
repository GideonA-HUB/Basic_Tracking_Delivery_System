from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import CustomerProfile
import uuid


class Command(BaseCommand):
    help = 'Create a VIP user for testing'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Username for VIP user', default='vip_test')
        parser.add_argument('--email', type=str, help='Email for VIP user', default='vip@example.com')
        parser.add_argument('--password', type=str, help='Password for VIP user', default='vip123456')
        parser.add_argument('--first-name', type=str, help='First name', default='VIP')
        parser.add_argument('--last-name', type=str, help='Last name', default='User')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']
        first_name = options['first_name']
        last_name = options['last_name']

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

        self.stdout.write(
            self.style.SUCCESS(
                f'\nVIP User Details:\n'
                f'Username: {username}\n'
                f'Email: {email}\n'
                f'Password: {password}\n'
                f'Login URL: /accounts/vip/login/\n'
            )
        )
