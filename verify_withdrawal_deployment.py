#!/usr/bin/env python
"""
Verification script for withdrawal functionality deployment
Run this after deployment to ensure everything is working
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

def verify_withdrawal_system():
    """Verify withdrawal system is working properly"""
    print("🔍 VERIFYING WITHDRAWAL SYSTEM DEPLOYMENT")
    print("=" * 60)
    
    try:
        # Set Django settings
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
        django.setup()
        
        from investments.models import CryptoWithdrawal
        
        # Check withdrawal data
        total_withdrawals = CryptoWithdrawal.objects.count()
        public_withdrawals = CryptoWithdrawal.objects.filter(is_public=True).count()
        fast_track_withdrawals = CryptoWithdrawal.objects.filter(priority='fast').count()
        
        print(f"📊 WITHDRAWAL DATA STATS:")
        print(f"   Total withdrawals: {total_withdrawals}")
        print(f"   Public withdrawals: {public_withdrawals}")
        print(f"   Fast track withdrawals: {fast_track_withdrawals}")
        
        if total_withdrawals == 0:
            print("❌ No withdrawal data found! Running populate command...")
            execute_from_command_line(['manage.py', 'populate_withdrawals'])
            
            # Recheck
            total_withdrawals = CryptoWithdrawal.objects.count()
            print(f"✅ After population: {total_withdrawals} withdrawals")
        
        # Check dashboard data (first 20)
        dashboard_withdrawals = CryptoWithdrawal.objects.filter(
            is_public=True
        ).order_by('order_position', '-created_at')[:20]
        
        print(f"📱 DASHBOARD DATA:")
        print(f"   Withdrawals for dashboard: {len(dashboard_withdrawals)}")
        
        # Show sample data
        print(f"📋 SAMPLE WITHDRAWAL DATA:")
        for i, withdrawal in enumerate(dashboard_withdrawals[:5]):
            print(f"   {i+1}. {withdrawal.name} - {withdrawal.estimated_delivery_display} - ${withdrawal.amount}")
        
        # Check API endpoints
        print(f"🔗 API ENDPOINTS:")
        print(f"   Fast track payment: /investments/api/fast-track-payment/")
        print(f"   Payment status check: /investments/api/check-payment-status/")
        print(f"   Withdrawal list: /investments/withdrawal-list/")
        print(f"   Withdrawal list all: /investments/withdrawal-list-all/")
        
        print(f"✅ WITHDRAWAL SYSTEM VERIFICATION COMPLETE!")
        return True
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    verify_withdrawal_system()
