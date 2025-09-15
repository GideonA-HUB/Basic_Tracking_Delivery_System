from django.core.management.base import BaseCommand
from chat.models import ChatSettings


class Command(BaseCommand):
    help = 'Initialize chat system settings'

    def handle(self, *args, **options):
        # Create default chat settings if they don't exist
        settings, created = ChatSettings.objects.get_or_create(
            pk=1,
            defaults={
                'is_enabled': True,
                'welcome_message': 'Hello! Welcome to Meridian Asset Logistics. How can we help you today?',
                'offline_message': "We're currently offline. Please leave a message and we'll get back to you soon!",
                'business_hours_enabled': True,
                'business_hours_start': '09:00',
                'business_hours_end': '17:00',
                'business_days': [0, 1, 2, 3, 4],  # Monday to Friday
                'auto_response_enabled': True,
                'auto_response_delay': 30,
                'auto_response_message': 'Thank you for your message. A staff member will be with you shortly.',
                'max_file_size': 10,  # MB
                'allowed_file_types': ['jpg', 'jpeg', 'png', 'gif', 'pdf', 'doc', 'docx', 'txt'],
                'email_notifications': True,
                'notification_email': 'support@meridianassetlogistics.com',
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('Chat settings initialized successfully!')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Chat settings already exist.')
            )
        
        # Display current settings
        self.stdout.write('\nCurrent Chat Settings:')
        self.stdout.write(f'  Enabled: {settings.is_enabled}')
        self.stdout.write(f'  Business Hours: {settings.business_hours_start} - {settings.business_hours_end}')
        self.stdout.write(f'  Business Days: {settings.business_days}')
        self.stdout.write(f'  Auto Response: {settings.auto_response_enabled}')
        self.stdout.write(f'  Notification Email: {settings.notification_email}')
