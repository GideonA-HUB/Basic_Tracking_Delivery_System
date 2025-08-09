#!/usr/bin/env python3
"""
Meridian Asset Logistics - Testing Interactive Cost Calculation Page
"""
import requests
from bs4 import BeautifulSoup
import time

def test_calculate_cost_interactive():
    """Test the interactive functionality of the cost calculation page"""
    print("=" * 70)
    print("Meridian Asset Logistics - Testing Interactive Cost Calculation Page")
    print("=" * 70)
    base_url = "http://localhost:8000"
    
    try:
        print("\n1. Testing cost calculation page...")
        response = requests.get(f"{base_url}/calculate-cost/")
        if response.status_code == 200:
            print("✅ Cost calculation page loads successfully")
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Test required HTML elements
            print("\n2. Testing required HTML elements...")
            required_elements = [
                ("package-tab", "Package tab"),
                ("freight-tab", "Freight tab"),
                ("from-country", "From country select"),
                ("to-country", "To country select"),
                ("from-locality", "From locality input"),
                ("to-locality", "To locality input"),
                ("package-weight", "Package weight input"),
                ("freight-weight", "Freight weight input"),
                ("shipment-date", "Shipment date input"),
                ("calculate-btn", "Calculate button"),
                ("clear-btn", "Clear button"),
                ("loading-state", "Loading state"),
                ("results-table", "Results table"),
                ("results-body", "Results body"),
                ("route-display", "Route display")
            ]
            
            for element_id, description in required_elements:
                element = soup.find(id=element_id)
                if element:
                    print(f"✅ {description} found")
                else:
                    print(f"❌ {description} not found")
            
            # Test JavaScript functionality indicators
            print("\n3. Testing JavaScript functionality indicators...")
            js_indicators = [
                ("shipment-tab", "Shipment tab class"),
                ("required-field", "Required field class"),
                ("hidden", "Hidden class for freight section"),
                ("animate-spin", "Loading animation class"),
                ("DOMContentLoaded", "DOM ready event listener"),
                ("addEventListener", "Event listener setup"),
                ("classList", "Class manipulation"),
                ("querySelector", "Element selection"),
                ("setTimeout", "Async functionality")
            ]
            
            for indicator, description in js_indicators:
                if indicator in response.text:
                    print(f"✅ {description} found")
                else:
                    print(f"❌ {description} not found")
            
            # Test form structure
            print("\n4. Testing form structure...")
            form_checks = [
                ("Package Weight", "Package weight section"),
                ("Freight Details", "Freight details section"),
                ("Weight ★", "Required weight field"),
                ("Country or Territory", "Country selection"),
                ("Locality ★", "Required locality field"),
                ("Postcode", "Postcode field"),
                ("Residential Address", "Residential checkbox"),
                ("When are you shipping? ★", "Required date field")
            ]
            
            for text, description in form_checks:
                if text in response.text:
                    print(f"✅ {description} found")
                else:
                    print(f"❌ {description} not found")
            
            # Test results table structure
            print("\n5. Testing results table structure...")
            table_checks = [
                ("Meridian Asset Logistics Express", "Express service"),
                ("Meridian Asset Logistics Express Saver", "Express Saver service"),
                ("Meridian Asset Logistics Standard", "Standard service"),
                ("Latest Pickup Time: 5:00 PM", "Pickup time info"),
                ("Schedule by: 3:00 PM", "Schedule info"),
                ("Days In Transit: --", "Transit time placeholder"),
                ("Delivered By: --", "Delivery date placeholder"),
                ("Cost", "Cost column header")
            ]
            
            for text, description in table_checks:
                if text in response.text:
                    print(f"✅ {description} found")
                else:
                    print(f"❌ {description} not found")
            
            # Test interactive features
            print("\n6. Testing interactive features...")
            interactive_checks = [
                ("data-type=\"package\"", "Package tab data attribute"),
                ("data-type=\"freight\"", "Freight tab data attribute"),
                ("onclick", "Click handlers"),
                ("hover:", "Hover effects"),
                ("transition-colors", "Color transitions"),
                ("focus:ring-2", "Focus effects"),
                ("required-field", "Required field validation")
            ]
            
            for text, description in interactive_checks:
                if text in response.text:
                    print(f"✅ {description} found")
                else:
                    print(f"❌ {description} not found")
            
            # Test branding
            print("\n7. Testing branding...")
            branding_checks = [
                ("Meridian Asset Logistics", "Company name"),
                ("Calculate Time and Cost", "Page title"),
                ("MAL", "Company acronym"),
                ("Nigeria", "Country options"),
                ("United States", "Country options"),
                ("United Kingdom", "Country options"),
                ("Canada", "Country options")
            ]
            
            for text, description in branding_checks:
                if text in response.text:
                    print(f"✅ {description} found")
                else:
                    print(f"❌ {description} not found")
            
        else:
            print(f"❌ Cost calculation page failed: {response.status_code}")
            
        print("\n" + "=" * 70)
        print("Interactive Cost Calculation Page Test completed!")
        print("=" * 70)
        
        # Provide usage instructions
        print("\n📋 Usage Instructions:")
        print("1. Open the cost calculation page in your browser")
        print("2. Switch between Package and Freight tabs")
        print("3. Fill in required fields (marked with ★)")
        print("4. Click 'Calculate' to see shipping options")
        print("5. Use 'Clear' to reset the form")
        print("6. Watch for loading states and dynamic results")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the Django server is running.")
    except Exception as e:
        print(f"❌ Error during testing: {e}")

if __name__ == "__main__":
    test_calculate_cost_interactive()
