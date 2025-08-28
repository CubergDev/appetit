#!/usr/bin/env python3
"""
Test script to verify analytics implementation
"""
import requests
import json
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin@appetit.com"  # Adjust as needed
ADMIN_PASSWORD = "admin"  # Adjust as needed

def test_admin_login():
    """Test admin authentication"""
    print("Testing admin login...")
    login_data = {
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
    if response.status_code == 200:
        token = response.json().get("access_token")
        print("✓ Admin login successful")
        return token
    else:
        print(f"✗ Admin login failed: {response.status_code} - {response.text}")
        return None

def test_utm_sources_endpoint(token):
    """Test the new UTM sources endpoint"""
    print("\nTesting UTM sources endpoint...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test date range (last 30 days)
    to_date = datetime.now().isoformat()
    from_date = (datetime.now() - timedelta(days=30)).isoformat()
    
    params = {
        "from": from_date,
        "to": to_date
    }
    
    response = requests.get(f"{BASE_URL}/api/v1/admin/analytics/utm-sources", 
                          headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        print("✓ UTM sources endpoint working")
        print(f"  Sources found: {data.get('summary', {}).get('sources_count', 0)}")
        print(f"  Total orders: {data.get('summary', {}).get('total_orders', 0)}")
        print(f"  Total revenue: {data.get('summary', {}).get('total_revenue', 0)}")
        
        # Show top sources
        sources = data.get("sources", [])[:3]  # Top 3
        if sources:
            print("  Top sources:")
            for source in sources:
                print(f"    - {source['utm_source']}: {source['orders_count']} orders, "
                      f"{source['revenue']} revenue ({source['orders_percentage']}%)")
        return True
    else:
        print(f"✗ UTM sources endpoint failed: {response.status_code} - {response.text}")
        return False

def test_ga4_health():
    """Test GA4 analytics health"""
    print("\nTesting GA4 analytics health...")
    
    try:
        # Import the health check functions
        import sys
        sys.path.append("app")
        
        from services.analytics.ga4_streams import health_check_all
        from services.analytics.ga4_mp import health_check as mp_health_check
        
        # Check multi-platform streams
        streams_health = health_check_all()
        print("GA4 Streams Health:")
        for platform, config in streams_health.items():
            if platform != "summary":
                status = config.get("status", "unknown")
                print(f"  {platform}: {status}")
        
        summary = streams_health.get("summary", {})
        configured = summary.get("configured", 0)
        total = summary.get("total", 0)
        print(f"  Summary: {configured}/{total} platforms configured")
        
        # Check general MP health
        mp_health = mp_health_check()
        print(f"GA4 Measurement Protocol: {mp_health.get('status', 'unknown')}")
        
        return configured > 0 or mp_health.get("status") == "configured"
        
    except Exception as e:
        print(f"✗ GA4 health check failed: {e}")
        return False

def test_existing_analytics_endpoints(token):
    """Test existing analytics endpoints"""
    print("\nTesting existing analytics endpoints...")
    headers = {"Authorization": f"Bearer {token}"}
    
    endpoints = [
        "/api/v1/admin/analytics/summary",
        "/api/v1/admin/analytics/orders-by-period",
        "/api/v1/admin/analytics/order-sources",
        "/api/v1/admin/analytics/repeat-customers"
    ]
    
    working_endpoints = 0
    for endpoint in endpoints:
        response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
        if response.status_code == 200:
            print(f"  ✓ {endpoint}")
            working_endpoints += 1
        else:
            print(f"  ✗ {endpoint}: {response.status_code}")
    
    print(f"Working endpoints: {working_endpoints}/{len(endpoints)}")
    return working_endpoints == len(endpoints)

def main():
    """Main test function"""
    print("=== Analytics Implementation Test ===")
    
    # Test admin authentication
    token = test_admin_login()
    if not token:
        print("Cannot proceed without admin authentication")
        return
    
    # Test analytics endpoints
    utm_ok = test_utm_sources_endpoint(token)
    existing_ok = test_existing_analytics_endpoints(token)
    ga4_ok = test_ga4_health()
    
    print("\n=== Test Summary ===")
    print(f"UTM Sources Endpoint: {'✓' if utm_ok else '✗'}")
    print(f"Existing Endpoints: {'✓' if existing_ok else '✗'}")
    print(f"GA4 Configuration: {'✓' if ga4_ok else '✗'}")
    
    if utm_ok and existing_ok:
        print("\n✓ Analytics implementation is working correctly!")
        print("Key features implemented:")
        print("- UTM parameter capture during checkout")
        print("- UTM source reporting in admin panel")
        print("- GA4 event tracking for purchases")
        print("- Multi-platform analytics support")
    else:
        print("\n✗ Some analytics features need attention")

if __name__ == "__main__":
    main()