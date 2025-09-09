from django.core.management.base import BaseCommand
import os
import shutil

class Command(BaseCommand):
    help = 'Emergency fix for static files - force copy all JS files'

    def handle(self, *args, **options):
        self.stdout.write('🚨 EMERGENCY STATIC FILES FIX...')
        
        try:
            # Get paths
            source_dir = os.path.join(os.getcwd(), 'static')
            target_dir = os.path.join(os.getcwd(), 'staticfiles')
            
            # Ensure target directory exists
            os.makedirs(target_dir, exist_ok=True)
            
            # Copy entire static directory
            if os.path.exists(source_dir):
                self.stdout.write(f'📁 Copying from {source_dir} to {target_dir}')
                
                # Copy all files recursively
                for root, dirs, files in os.walk(source_dir):
                    for file in files:
                        source_path = os.path.join(root, file)
                        relative_path = os.path.relpath(source_path, source_dir)
                        target_path = os.path.join(target_dir, relative_path)
                        
                        # Create target directory if needed
                        os.makedirs(os.path.dirname(target_path), exist_ok=True)
                        
                        # Copy file
                        shutil.copy2(source_path, target_path)
                        self.stdout.write(f'✅ Copied {relative_path}')
                
                self.stdout.write(self.style.SUCCESS('✅ Emergency static files fix completed'))
            else:
                self.stdout.write(self.style.ERROR('❌ Source static directory not found'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Emergency fix failed: {e}'))
