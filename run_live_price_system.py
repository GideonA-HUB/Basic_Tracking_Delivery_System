#!/usr/bin/env python3
"""
Run Live Price System
Simple script to start the live price system in production
"""

import os
import sys
import subprocess

def main():
    print("🚀 Starting Live Price System...")
    
    # Change to the correct directory
    os.chdir('Basic_Tracking_Delivery_System')
    
    # Run the production live price fixer
    try:
        subprocess.run([sys.executable, 'PRODUCTION_LIVE_PRICE_FIXER.py'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running live price system: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n🛑 Stopping live price system...")
        return 0
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
