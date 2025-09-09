#!/usr/bin/env python
"""
Daphne startup script for Railway deployment with proper port handling
"""

import os
import sys
import subprocess

def main():
    """Start the application with Daphne ASGI server"""
    try:
        # Set Django settings module
        os.environ['DJANGO_SETTINGS_MODULE'] = 'delivery_tracker.settings'
        print(f"✅ Django settings module set to: {os.environ['DJANGO_SETTINGS_MODULE']}")
        
        # Get port from environment (Railway provides this)
        port = os.environ.get('PORT', '8080')
        print(f"✅ Using port: {port}")
        
        # Debug environment variables
        print(f"🔍 PORT: {os.environ.get('PORT', 'Not set')}")
        print(f"🔍 REDIS_URL: {os.environ.get('REDIS_URL', 'Not set')}")
        
        # Import Django
        import django
        from django.core.management import execute_from_command_line
        
        # Initialize Django
        django.setup()
        print("✅ Django initialized successfully")
        
        # Run migrations first
        print("🔄 Running migrations...")
        try:
            execute_from_command_line(['manage.py', 'migrate', '--noinput'])
            print("✅ Migrations completed successfully")
        except Exception as migrate_error:
            print(f"⚠️ Migration failed: {migate_error}")
            print("🔄 Continuing without migrations...")
        
        # Collect static files
        print("📁 Collecting static files...")
        try:
            # Force collect static files without manifest
            execute_from_command_line(['manage.py', 'collectstatic', '--noinput', '--clear', '--ignore=*.map'])
            print("✅ Static files collected successfully")
            
            # Fix static files issue
            print("🔧 Fixing static files...")
            execute_from_command_line(['manage.py', 'collect_static_fix'])
            print("✅ Static files fixed successfully")
            
            # Emergency static files fix
            print("🚨 Emergency static files fix...")
            execute_from_command_line(['manage.py', 'emergency_static_fix'])
            print("✅ Emergency static files fix completed")
            
            # Verify critical files exist
            import os
            static_root = os.path.join(os.getcwd(), 'staticfiles')
            critical_files = [
                'js/live_price_dashboard.js',
                'js/delivery_tracking_map.js'
            ]
            
            for file_path in critical_files:
                full_path = os.path.join(static_root, file_path)
                if os.path.exists(full_path):
                    print(f"✅ {file_path} exists")
                else:
                    print(f"❌ {file_path} missing - copying from source")
                    source_path = os.path.join(os.getcwd(), 'static', file_path)
                    if os.path.exists(source_path):
                        import shutil
                        os.makedirs(os.path.dirname(full_path), exist_ok=True)
                        shutil.copy2(source_path, full_path)
                        print(f"✅ Copied {file_path}")
                    else:
                        print(f"❌ Source {file_path} not found")
                        
        except Exception as static_error:
            print(f"⚠️ Static files collection failed: {static_error}")
            print("🔄 Continuing without static files...")
        
        # Start Daphne ASGI server
        print(f"🚀 Starting Daphne ASGI server on port {port}...")
        
        daphne_cmd = [
            'daphne',
            '-b', '0.0.0.0',
            '-p', port,
            '--access-log', '-',
            '--proxy-headers',
            'delivery_tracker.asgi:application'
        ]
        
        print(f"🔧 Running: {' '.join(daphne_cmd)}")
        subprocess.run(daphne_cmd)
        
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
