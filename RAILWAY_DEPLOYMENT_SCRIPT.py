#!/usr/bin/env python3
"""
RAILWAY DEPLOYMENT SCRIPT - PERMANENT SOLUTION
This script ensures Railway deploys the price service as a separate background worker.
"""

import os
import sys
import subprocess
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def check_railway_environment():
    """Check if we're running on Railway"""
    railway_env = os.environ.get('RAILWAY_ENVIRONMENT')
    if railway_env:
        logger.info(f"✅ Railway environment detected: {railway_env}")
        return True
    else:
        logger.info("⚠️ Not running on Railway")
        return False

def start_price_service():
    """Start the price service"""
    try:
        logger.info("🚀 Starting Railway Price Service...")
        
        # Check if we're on Railway
        if check_railway_environment():
            logger.info("✅ Railway environment confirmed")
        
        # Start the price service
        logger.info("🔄 Launching price service...")
        subprocess.run([sys.executable, "RAILWAY_STARTUP_FIX.py"], check=True)
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Price service failed to start: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Error starting price service: {e}")
        sys.exit(1)

def main():
    """Main function"""
    try:
        logger.info("🚀 RAILWAY DEPLOYMENT SCRIPT STARTED")
        logger.info("=" * 50)
        
        # Start the price service
        start_price_service()
        
    except KeyboardInterrupt:
        logger.info("🛑 Deployment script stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
