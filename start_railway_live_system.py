#!/usr/bin/env python3
"""
Start Railway Live System
Script to start the live price system on Railway with proper environment setup
"""

import os
import sys
import subprocess
import time

def setup_railway_environment():
    """Setup Railway environment variables"""
    print("🔧 Setting up Railway environment...")
    
    # Set Railway environment variables if not already set
    if not os.environ.get('DATABASE_URL'):
        print("⚠️  DATABASE_URL not set - this is required for Railway")
        return False
    
    # Set other required environment variables
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings_production')
    os.environ.setdefault('DEBUG', 'False')
    os.environ.setdefault('ALLOWED_HOSTS', 'meridianassetlogistics.com,*.railway.app')
    
    print("✅ Railway environment configured")
    return True

def start_live_price_system():
    """Start the live price system"""
    print("🚀 Starting Railway Live Price System...")
    
    try:
        # Run the Railway live price fixer
        subprocess.run([sys.executable, 'RAILWAY_LIVE_PRICE_FIXER.py'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running live price system: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n🛑 Stopping live price system...")
        return 0

def main():
    """Main function"""
    print("🚀 RAILWAY LIVE PRICE SYSTEM STARTER")
    print("=" * 50)
    
    # Setup environment
    if not setup_railway_environment():
        print("❌ Failed to setup Railway environment")
        return 1
    
    # Start the system
    return start_live_price_system()

if __name__ == "__main__":
    sys.exit(main())
