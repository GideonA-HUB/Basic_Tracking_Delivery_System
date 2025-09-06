#!/usr/bin/env python3
"""
RAILWAY PRICE SERVICE STARTER
=============================
Starts the live price service on Railway with proper environment handling.
"""

import os
import sys
import subprocess
import time

def main():
    """Start the Railway live price service"""
    print("🚀 Starting Railway Live Price Service...")
    
    # Set environment variables for Railway
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings_production')
    
    # Check if we're on Railway
    if os.getenv('RAILWAY_ENVIRONMENT'):
        print("✅ Running on Railway environment")
    else:
        print("⚠️ Not running on Railway - using production settings anyway")
    
    try:
        # Start the price service
        print("📡 Starting live price service...")
        subprocess.run([sys.executable, 'RAILWAY_LIVE_PRICE_SERVICE.py'], check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting price service: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("🛑 Service stopped by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
