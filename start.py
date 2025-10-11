#!/usr/bin/env python
"""
Railway Production Startup Script
This script ensures the correct deployment process is used
"""
import os
import sys

def main():
    """Main startup function"""
    print("🚀 RAILWAY STARTUP SCRIPT")
    print("=" * 50)
    print("🔍 Checking deployment script...")
    
    # Check if we're using the correct deployment script
    if 'deploy_complete.py' in sys.argv or 'deploy_complete' in ' '.join(sys.argv):
        print("✅ Using deploy_complete.py - VIP Members will be included")
    else:
        print("❌ NOT using deploy_complete.py - VIP Members may not work!")
        print("🔧 Forcing use of deploy_complete.py...")
        
        # Import and run deploy_complete.py
        try:
            import deploy_complete
            deploy_complete.main()
            return
        except Exception as e:
            print(f"❌ Error running deploy_complete.py: {e}")
            sys.exit(1)
    
    # If we get here, we're already using the correct script
    print("✅ Deployment script verification complete")

if __name__ == '__main__':
    main()
