"""
Django management command to test email configuration.
"""
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from tracking.email_utils import test_email_configuration


class Command(BaseCommand):
    help = 'Test email configuration by sending a test email'

    def add_arguments(self, parser):
        parser.add_argument(
            '--recipient',
            type=str,
            help='Email address to send test email to (defaults to DEFAULT_FROM_EMAIL)',
            default=settings.DEFAULT_FROM_EMAIL
        )

    def handle(self, *args, **options):
        recipient = options['recipient']
        
        self.stdout.write(
            self.style.SUCCESS(f'Testing email configuration...')
        )
        
        # Display current email settings
        self.stdout.write(f'Email Host: {settings.EMAIL_HOST}')
        self.stdout.write(f'Email Port: {settings.EMAIL_PORT}')
        self.stdout.write(f'Email User: {settings.EMAIL_HOST_USER}')
        self.stdout.write(f'From Email: {settings.DEFAULT_FROM_EMAIL}')
        self.stdout.write(f'Recipient: {recipient}')
        self.stdout.write('')
        
        try:
            # Test email configuration
            success = test_email_configuration()
            
            if success:
                self.stdout.write(
                    self.style.SUCCESS('✅ Email configuration test PASSED!')
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Test email sent successfully to {recipient}')
                )
            else:
                self.stdout.write(
                    self.style.ERROR('❌ Email configuration test FAILED!')
                )
                self.stdout.write(
                    self.style.ERROR('Please check your email settings and credentials.')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error testing email configuration: {str(e)}')
            )
            self.stdout.write(
                self.style.ERROR('Please verify your email settings in settings.py and .env file.')
            )
