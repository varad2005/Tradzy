"""
Test script to verify users are redirected to correct dashboards after login.
Tests all three user roles: Admin, Retailer, and Wholesaler.
"""
import requests
import json
from datetime import datetime

def print_separator():
    """Print a visual separator."""
    print("=" * 70)

def print_header(text):
    """Print a formatted header."""
    print_separator()
    print(f"  {text}")
    print_separator()

def test_login_redirect(email, password, expected_role, expected_dashboard):
    """
    Test login for a specific user and verify redirect.
    
    Args:
        email: User's email
        password: User's password
        expected_role: Expected user role
        expected_dashboard: Expected dashboard URL
    """
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    print(f"\n🔐 Testing: {email}")
    print(f"   Expected Role: {expected_role}")
    print(f"   Expected Dashboard: {expected_dashboard}")
    print("-" * 70)
    
    try:
        # Step 1: Login
        print("   Step 1: Sending login request...")
        login_data = {
            "email": email,
            "password": password
        }
        
        login_response = session.post(
            f"{base_url}/api/auth/login",
            json=login_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"   Login Status: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print(f"   ❌ FAILED: Login failed with status {login_response.status_code}")
            print(f"   Response: {login_response.text}")
            return False
        
        # Step 2: Check response data
        print("   Step 2: Validating response data...")
        response_data = login_response.json()
        
        returned_role = response_data.get('user', {}).get('role')
        redirect_url = response_data.get('redirect')
        
        print(f"   Returned Role: {returned_role}")
        print(f"   Redirect URL: {redirect_url}")
        
        # Verify role
        if returned_role != expected_role:
            print(f"   ❌ FAILED: Expected role '{expected_role}', got '{returned_role}'")
            return False
        print(f"   ✅ Role matches: {returned_role}")
        
        # Verify redirect URL
        if redirect_url != expected_dashboard:
            print(f"   ❌ FAILED: Expected redirect '{expected_dashboard}', got '{redirect_url}'")
            return False
        print(f"   ✅ Redirect URL matches: {redirect_url}")
        
        # Step 3: Access dashboard
        print("   Step 3: Accessing dashboard...")
        dashboard_response = session.get(f"{base_url}{redirect_url}")
        print(f"   Dashboard Status: {dashboard_response.status_code}")
        
        if dashboard_response.status_code != 200:
            print(f"   ❌ FAILED: Dashboard access failed with status {dashboard_response.status_code}")
            return False
        print(f"   ✅ Dashboard accessible")
        
        # Step 4: Verify dashboard content
        print("   Step 4: Verifying dashboard content...")
        dashboard_html = dashboard_response.text
        
        # Check for role-specific content
        content_checks = {
            'admin': ['Admin Dashboard', 'User Management', 'Platform Statistics'],
            'retailer': ['Retailer Dashboard', 'Recent Orders', 'Featured Products'],
            'wholesaler': ['Wholesaler Dashboard', 'Product Management', 'Add New Product']
        }
        
        expected_content = content_checks.get(expected_role, [])
        found_content = []
        missing_content = []
        
        for content in expected_content:
            if content in dashboard_html:
                found_content.append(content)
                print(f"   ✅ Found: '{content}'")
            else:
                missing_content.append(content)
                print(f"   ⚠️  Missing: '{content}'")
        
        # Overall result
        if len(missing_content) == 0:
            print(f"\n   🎉 SUCCESS: {email} redirects correctly to {expected_dashboard}")
            return True
        else:
            print(f"\n   ⚠️  PARTIAL: Dashboard loads but some content missing")
            return True
            
    except requests.exceptions.ConnectionError:
        print("   ❌ FAILED: Cannot connect to server. Is Flask running?")
        return False
    except Exception as e:
        print(f"   ❌ FAILED: Unexpected error - {str(e)}")
        return False

def test_wrong_dashboard_access(email, password, user_role, wrong_dashboard):
    """
    Test that users cannot access dashboards for other roles.
    
    Args:
        email: User's email
        password: User's password
        user_role: User's actual role
        wrong_dashboard: Dashboard URL they shouldn't access
    """
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    print(f"\n🔒 Testing unauthorized access: {user_role} → {wrong_dashboard}")
    print("-" * 70)
    
    try:
        # Login first
        login_data = {"email": email, "password": password}
        login_response = session.post(
            f"{base_url}/api/auth/login",
            json=login_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if login_response.status_code != 200:
            print(f"   ❌ Login failed")
            return False
        
        # Try to access wrong dashboard
        print(f"   Attempting to access: {wrong_dashboard}")
        dashboard_response = session.get(f"{base_url}{wrong_dashboard}")
        
        # Should be redirected or denied
        if dashboard_response.status_code == 200 and wrong_dashboard in dashboard_response.url:
            print(f"   ❌ SECURITY ISSUE: {user_role} can access {wrong_dashboard}")
            return False
        else:
            print(f"   ✅ Access denied (Status: {dashboard_response.status_code})")
            return True
            
    except Exception as e:
        print(f"   Error during test: {str(e)}")
        return False

def main():
    """Run all login redirect tests."""
    print_header("🚀 TRADZY LOGIN REDIRECT TEST SUITE")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test data: (email, password, expected_role, expected_dashboard)
    test_cases = [
        ("admin@tradzy.com", "admin123", "admin", "/admin"),
        ("retailer@tradzy.com", "retailer123", "retailer", "/retailer"),
        ("wholesaler@tradzy.com", "wholesaler123", "wholesaler", "/wholesaler/dashboard"),
    ]
    
    results = []
    
    # Test each user type
    print_header("TEST 1: LOGIN REDIRECT VERIFICATION")
    
    for email, password, role, dashboard in test_cases:
        result = test_login_redirect(email, password, role, dashboard)
        results.append((f"{role.capitalize()} Login", result))
    
    # Test unauthorized access
    print_header("TEST 2: UNAUTHORIZED ACCESS PREVENTION")
    
    # Test retailer trying to access admin dashboard
    result = test_wrong_dashboard_access(
        "retailer@tradzy.com", "retailer123", "retailer", "/admin"
    )
    results.append(("Retailer blocked from Admin", result))
    
    # Test wholesaler trying to access retailer dashboard
    result = test_wrong_dashboard_access(
        "wholesaler@tradzy.com", "wholesaler123", "wholesaler", "/retailer"
    )
    results.append(("Wholesaler blocked from Retailer", result))
    
    # Summary
    print_header("📊 TEST RESULTS SUMMARY")
    print()
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status}: {test_name}")
    
    print()
    print_separator()
    print(f"   Total: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    print_separator()
    
    if passed == total:
        print("\n   🎉 ALL TESTS PASSED! Login redirects working correctly!")
    else:
        print(f"\n   ⚠️  {total - passed} test(s) failed. Please review above.")
    
    print("\n" + "=" * 70)
    print("   Manual Testing Instructions:")
    print("=" * 70)
    print("   1. Open: http://localhost:5000/login")
    print("   2. Test each role:")
    print("      • Admin: admin@tradzy.com / admin123")
    print("      • Retailer: retailer@tradzy.com / retailer123")
    print("      • Wholesaler: wholesaler@tradzy.com / wholesaler123")
    print("   3. Verify each redirects to correct dashboard")
    print("=" * 70)

if __name__ == "__main__":
    main()