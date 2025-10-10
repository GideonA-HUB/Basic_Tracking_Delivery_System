from django.core.management.base import BaseCommand
from django.db import connection
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Ensure VIP members database tables exist'

    def handle(self, *args, **options):
        self.stdout.write('Checking VIP members database tables...')
        
        # Check if VIP tables exist
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name LIKE 'vip_members_%'
            """)
            existing_tables = [row[0] for row in cursor.fetchall()]
            
        required_tables = [
            'vip_members_vipstaff',
            'vip_members_vipmember', 
            'vip_members_vipactivity',
            'vip_members_vipbenefit',
            'vip_members_vipapplication',
            'vip_members_vipnotification'
        ]
        
        missing_tables = [table for table in required_tables if table not in existing_tables]
        
        if missing_tables:
            self.stdout.write(
                self.style.WARNING(f'Missing tables: {missing_tables}')
            )
            self.stdout.write('Running VIP members migrations...')
            
            try:
                # Run migrations for vip_members app
                call_command('migrate', 'vip_members', verbosity=2)
                self.stdout.write(
                    self.style.SUCCESS('VIP members migrations completed successfully!')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error running migrations: {e}')
                )
                raise
        else:
            self.stdout.write(
                self.style.SUCCESS('All VIP members tables exist!')
            )
        
        # Verify tables exist now
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name LIKE 'vip_members_%'
            """)
            final_tables = [row[0] for row in cursor.fetchall()]
            
        self.stdout.write(f'Final VIP tables: {final_tables}')
        
        if len(final_tables) >= len(required_tables):
            self.stdout.write(
                self.style.SUCCESS('✅ VIP members database setup complete!')
            )
        else:
            self.stdout.write(
                self.style.ERROR('❌ Some VIP tables are still missing!')
            )
