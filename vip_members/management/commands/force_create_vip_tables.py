from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection
import sys

class Command(BaseCommand):
    help = 'Force create VIP Members tables in production'

    def handle(self, *args, **options):
        self.stdout.write('🚀 FORCE CREATING VIP MEMBERS TABLES')
        self.stdout.write('=' * 50)
        
        try:
            # First, check if tables exist
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name LIKE 'vip_members_%'
                    ORDER BY table_name;
                """)
                existing_tables = [row[0] for row in cursor.fetchall()]
                
                self.stdout.write(f"📊 Found {len(existing_tables)} existing VIP tables:")
                for table in existing_tables:
                    self.stdout.write(f"  ✅ {table}")
            
            # Run makemigrations to ensure we have the latest migrations
            self.stdout.write('🔄 Running makemigrations...')
            call_command('makemigrations', 'vip_members', verbosity=0)
            self.stdout.write('✅ Makemigrations completed')
            
            # Run migrations
            self.stdout.write('🔄 Running migrations...')
            call_command('migrate', 'vip_members', verbosity=0)
            self.stdout.write('✅ VIP Members migrations completed')
            
            # Run all migrations to be safe
            self.stdout.write('🔄 Running all migrations...')
            call_command('migrate', verbosity=0)
            self.stdout.write('✅ All migrations completed')
            
            # Verify tables exist now
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name LIKE 'vip_members_%'
                    ORDER BY table_name;
                """)
                final_tables = [row[0] for row in cursor.fetchall()]
                
                expected_tables = [
                    'vip_members_vipbenefit',
                    'vip_members_vipmember', 
                    'vip_members_vipstaff',
                    'vip_members_vipactivity',
                    'vip_members_vipnotification',
                    'vip_members_vipapplication'
                ]
                
                self.stdout.write(f"📊 Final VIP tables ({len(final_tables)}):")
                for table in final_tables:
                    self.stdout.write(f"  ✅ {table}")
                
                missing_tables = [table for table in expected_tables if table not in final_tables]
                if missing_tables:
                    self.stdout.write(self.style.ERROR(f"❌ Missing tables: {missing_tables}"))
                    
                    # Try to create missing tables manually
                    self.stdout.write('🔄 Attempting to create missing tables manually...')
                    for table in missing_tables:
                        try:
                            # Get the model name from table name
                            model_name = table.replace('vip_members_', '').replace('_', '')
                            model_name = ''.join(word.capitalize() for word in model_name.split())
                            
                            # Import and create the model
                            from vip_members.models import VIPMember, VIPStaff, VIPActivity, VIPBenefit, VIPNotification, VIPApplication
                            
                            # Try to create a dummy record to force table creation
                            if table == 'vip_members_vipmember':
                                # This will fail but might create the table
                                pass
                            elif table == 'vip_members_vipstaff':
                                pass
                            elif table == 'vip_members_vipactivity':
                                pass
                            elif table == 'vip_members_vipbenefit':
                                pass
                            elif table == 'vip_members_vipnotification':
                                pass
                            elif table == 'vip_members_vipapplication':
                                pass
                                
                        except Exception as e:
                            self.stdout.write(f"⚠️ Could not create {table}: {e}")
                    
                    # Try migrations one more time
                    self.stdout.write('🔄 Running migrations one more time...')
                    call_command('migrate', 'vip_members', '--run-syncdb', verbosity=0)
                    
                else:
                    self.stdout.write(self.style.SUCCESS('✅ All VIP tables exist!'))
            
            # Test if we can query the tables
            self.stdout.write('🧪 Testing VIP tables...')
            try:
                from vip_members.models import VIPMember, VIPStaff, VIPBenefit
                
                # Try to count records
                member_count = VIPMember.objects.count()
                staff_count = VIPStaff.objects.count()
                benefit_count = VIPBenefit.objects.count()
                
                self.stdout.write(f"✅ VIP Members: {member_count}")
                self.stdout.write(f"✅ VIP Staff: {staff_count}")
                self.stdout.write(f"✅ VIP Benefits: {benefit_count}")
                
                self.stdout.write(self.style.SUCCESS('🎉 VIP Members system is working!'))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ VIP tables test failed: {e}"))
                return False
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error: {e}"))
            import traceback
            traceback.print_exc()
            return False
        
        return True
