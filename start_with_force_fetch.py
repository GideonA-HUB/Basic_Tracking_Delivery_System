#!/usr/bin/env python
"""
Startup script with force MarketAux fetch after server starts
"""
import os
import sys
import django
import subprocess
import threading
import time
from django.core.management import execute_from_command_line

def force_fetch_news():
    """Force fetch news after a delay"""
    print("⏰ Waiting 10 seconds for server to fully start...")
    time.sleep(10)
    
    print("🚀 FORCE FETCHING MARKETAUX NEWS...")
    try:
        # Run the force fetch command
        execute_from_command_line(['manage.py', 'force_marketaux_news', '--count=30'])
        print("✅ Force fetch completed!")
    except Exception as e:
        print(f"❌ Force fetch failed: {e}")

def main():
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
    
    # Initialize Django
    django.setup()
    
    print("🚀 Starting application with force MarketAux fetch...")
    
    try:
        # Run migrations first
        print("🔄 Running migrations...")
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])
        print("✅ Migrations completed successfully")
        
        # Collect static files
        print("📁 Collecting static files...")
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput', '--clear'])
        print("✅ Static files collected successfully")
        
        # Start force fetch in background thread
        print("🚀 Starting force fetch in background...")
        fetch_thread = threading.Thread(target=force_fetch_news)
        fetch_thread.daemon = True
        fetch_thread.start()
        
        # Start the server
        print("🚀 Starting Daphne server...")
        import subprocess
        
        # Get port from environment
        port = os.environ.get('PORT', '8080')
        
        # Start Daphne
        cmd = [
            'daphne', 
            '-b', '0.0.0.0', 
            '-p', port, 
            'delivery_tracker.asgi:application'
        ]
        
        print(f"🚀 Starting server on port {port}")
        subprocess.run(cmd)
        
    except Exception as e:
        print(f"❌ Error during startup: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
