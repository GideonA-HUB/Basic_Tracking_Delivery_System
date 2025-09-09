from django.core.management.base import BaseCommand
from django.core.management import call_command
import os

class Command(BaseCommand):
    help = 'Fix static files collection for Railway deployment'

    def handle(self, *args, **options):
        self.stdout.write('🔧 Fixing static files collection...')
        
        try:
            # Collect static files
            call_command('collectstatic', '--noinput', '--clear')
            self.stdout.write(self.style.SUCCESS('✅ Static files collected successfully'))
            
            # Check if required JS files exist
            static_root = os.path.join(os.getcwd(), 'staticfiles')
            required_js_files = [
                'js/delivery_tracking_map.js',
                'js/live_price_dashboard.js'
            ]
            
            for js_file_path in required_js_files:
                js_file = os.path.join(static_root, js_file_path)
                
                if os.path.exists(js_file):
                    self.stdout.write(self.style.SUCCESS(f'✅ {js_file_path} found in staticfiles'))
                else:
                    self.stdout.write(self.style.WARNING(f'⚠️ {js_file_path} not found in staticfiles'))
                    
                    # Try to copy it manually
                    source_file = os.path.join(os.getcwd(), 'static', js_file_path)
                    if os.path.exists(source_file):
                        import shutil
                        os.makedirs(os.path.dirname(js_file), exist_ok=True)
                        shutil.copy2(source_file, js_file)
                        self.stdout.write(self.style.SUCCESS(f'✅ Copied {js_file_path} to staticfiles'))
                    else:
                        self.stdout.write(self.style.ERROR(f'❌ {js_file_path} not found in source'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error collecting static files: {e}'))
