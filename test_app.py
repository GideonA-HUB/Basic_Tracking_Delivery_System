#!/usr/bin/env python
"""
Test script to verify the application can start properly
"""

import os
import sys
import django

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')

# Initialize Django
django.setup()

# Test imports
try:
    from delivery_tracker.asgi import application
    print("✅ ASGI application imported successfully")
    
    from investments.models import InvestmentItem
    print("✅ Models imported successfully")
    
    from investments.views import investment_dashboard
    print("✅ Views imported successfully")
    
    print("🎉 Application test completed successfully!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
