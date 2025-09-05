#!/usr/bin/env python
"""
Complete system startup script for Meridian Asset Logistics
This script starts all components of the real-time investment system
"""
import os
import sys
import subprocess
import time
import threading
from datetime import datetime

def print_banner():
    """Print system startup banner"""
    print("=" * 80)
    print("🚀 MERIDIAN ASSET LOGISTICS - REAL-TIME INVESTMENT SYSTEM")
    print("=" * 80)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🌐 Website: https://meridianassetlogistics.com")
    print("📊 Features:")
    print("   • Real-time cryptocurrency prices")
    print("   • Live precious metals prices")
    print("   • Real estate indices")
    print("   • WebSocket live updates")
    print("   • Investment portfolio tracking")
    print("   • Live charts and analytics")
    print("   • Featured items display")
    print("=" * 80)

def start_django_server():
    """Start Django development server"""
    print("🔄 Starting Django server...")
    try:
        subprocess.run([
            sys.executable, "manage.py", "runserver", "0.0.0.0:8000"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Django server failed to start: {e}")
    except KeyboardInterrupt:
        print("🛑 Django server stopped")

def start_real_time_service():
    """Start real-time price service"""
    print("🔄 Starting real-time price service...")
    try:
        subprocess.run([
            sys.executable, "start_real_time_service.py"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Real-time service failed to start: {e}")
    except KeyboardInterrupt:
        print("🛑 Real-time service stopped")

def main():
    """Main function"""
    print_banner()
    
    print("\n🚀 Starting complete system...")
    print("📋 Components:")
    print("   1. Django web server (port 8000)")
    print("   2. Real-time price service")
    print("   3. WebSocket server")
    print("   4. Live price updates")
    print("   5. Investment analytics")
    
    print("\n🌐 Access URLs:")
    print("   • Main Website: http://localhost:8000/")
    print("   • Investment Marketplace: http://localhost:8000/investments/")
    print("   • Enhanced Dashboard: http://localhost:8000/investments/enhanced-dashboard/")
    print("   • User Portfolio: http://localhost:8000/investments/portfolio/")
    
    print("\n📊 Real-time Features:")
    print("   • Live price updates every 60 seconds")
    print("   • WebSocket real-time connections")
    print("   • Live charts and analytics")
    print("   • Price movement tracking")
    print("   • Featured items display")
    
    print("\n🔄 Starting services...")
    
    # Start real-time service in a separate thread
    real_time_thread = threading.Thread(target=start_real_time_service, daemon=True)
    real_time_thread.start()
    
    # Give real-time service time to start
    time.sleep(2)
    
    # Start Django server (this will block)
    try:
        start_django_server()
    except KeyboardInterrupt:
        print("\n🛑 System shutdown requested")
    finally:
        print("✅ System stopped")

if __name__ == "__main__":
    main()
