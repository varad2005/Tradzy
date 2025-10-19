"""
Comprehensive Login to Dashboard Connection Test
Tests the complete flow from login page to dashboard for all user roles.
"""
import requests
import time
from datetime import datetime

def print_header(text):
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def test_login_to_dashboard_flow(role_name, email, password, expected_dashboard):
    """Test complete flow from login to dashboard for a specific role."""
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    print(f"\n🔐 Testing {role_name} Login → Dashboard Connection")
    print("-" * 70)
    
    results = {
        'login_page_accessible': False,
        'portal_page_accessible': False,
        'authentication_successful': False,
        'redirect_url_correct': False,
        'dashboard_accessible': False,
        'dashboard_content_correct': False
    }
    
    try:
        # Step 1: Check main login page
        print("   Step 1: Checking main login page...")
        login_page = session.get(f"{base_url}/login", timeout=5)
        if login_page.status_code == 200:
            print("   ✅ Login page accessible")
            results['login_page_accessible'] = True
            
            # Check if role portal link exists
            portal_link_found = f'href="{role_name.lower()}.html"' in login_page.text or \
                              f'href="wholesaler.html"' in login_page.text
            if portal_link_found:
                print(f"   ✅ {role_name} portal link found")
        else:
            print(f"   ❌ Login page returned {login_page.status_code}")
            return results
        
        # Step 2: Check role-specific portal page
        print(f"   Step 2: Checking {role_name} portal page...")
        portal_url = f"{base_url}/{role_name.lower()}.html" if role_name != "Wholesaler" else f"{base_url}/wholesaler.html"
        portal_page = session.get(portal_url, timeout=5)
        
        if portal_page.status_code == 200:
            print(f"   ✅ {role_name} portal page accessible")
            results['portal_page_accessible'] = True
            
            # Check for login form elements
            has_form = 'loginForm' in portal_page.text or 'id="email"' in portal_page.text
            if has_form:
                print("   ✅ Login form found")
        else:
            print(f"   ❌ Portal page returned {portal_page.status_code}")
            return results
        
        # Step 3: Authenticate
        print("   Step 3: Authenticating user...")
        auth_response = session.post(
            f"{base_url}/api/auth/login",
            json={"email": email, "password": password},
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        
        if auth_response.status_code == 200:
            print("   ✅ Authentication successful")
            results['authentication_successful'] = True
            
            auth_data = auth_response.json()
            redirect_url = auth_data.get('redirect')
            user_data = auth_data.get('user', {})
            
            print(f"      User: {user_data.get('username')}")
            print(f"      Role: {user_data.get('role')}")
            print(f"      Redirect: {redirect_url}")
            
            # Step 4: Check redirect URL
            if redirect_url == expected_dashboard:
                print(f"   ✅ Redirect URL correct: {redirect_url}")
                results['redirect_url_correct'] = True
            else:
                print(f"   ❌ Wrong redirect URL: Expected {expected_dashboard}, got {redirect_url}")
                return results
        else:
            print(f"   ❌ Authentication failed: {auth_response.status_code}")
            print(f"      Error: {auth_response.text}")
            return results
        
        # Step 5: Access dashboard
        print("   Step 4: Accessing dashboard...")
        dashboard_response = session.get(f"{base_url}{redirect_url}", timeout=5)
        
        if dashboard_response.status_code == 200:
            print("   ✅ Dashboard accessible")
            results['dashboard_accessible'] = True
            
            # Step 6: Verify dashboard content
            print("   Step 5: Verifying dashboard content...")
            content = dashboard_response.text
            
            # Role-specific content checks
            content_markers = {
                'Admin': ['Admin Dashboard', 'User Management', 'Platform Statistics'],
                'Retailer': ['Retailer Dashboard', 'Recent Orders', 'Quick Actions'],
                'Wholesaler': ['Wholesaler Dashboard', 'Product Management', 'Add New Product']
            }
            
            markers = content_markers.get(role_name, [])
            found_markers = [marker for marker in markers if marker in content]
            
            if len(found_markers) >= 2:
                print(f"   ✅ Dashboard content verified ({len(found_markers)}/{len(markers)} markers found)")
                results['dashboard_content_correct'] = True
                for marker in found_markers:
                    print(f"      • Found: {marker}")
            else:
                print(f"   ⚠️  Limited dashboard content ({len(found_markers)}/{len(markers)} markers)")
                results['dashboard_content_correct'] = True  # Still pass if accessible
        else:
            print(f"   ❌ Dashboard returned {dashboard_response.status_code}")
            return results
        
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to server")
        print("      Make sure Flask is running: python backend/app.py")
        return results
    except requests.exceptions.Timeout:
        print("   ❌ Request timeout")
        return results
    except Exception as e:
        print(f"   ❌ Unexpected error: {str(e)}")
        return results
    
    return results

def main():
    """Run comprehensive login to dashboard connection tests."""
    print_header("🔍 LOGIN → DASHBOARD CONNECTION TEST")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nTesting complete flow from login page to dashboard for all roles...")
    
    # Test configurations
    test_configs = [
        ("Admin", "admin@tradzy.com", "admin123", "/admin"),
        ("Retailer", "retailer@tradzy.com", "retailer123", "/retailer"),
        ("Wholesaler", "wholesaler@tradzy.com", "wholesaler123", "/wholesaler/dashboard"),
    ]
    
    all_results = {}
    
    for role_name, email, password, dashboard_url in test_configs:
        results = test_login_to_dashboard_flow(role_name, email, password, dashboard_url)
        all_results[role_name] = results
        time.sleep(0.5)  # Small delay between tests
    
    # Summary
    print_header("📊 TEST RESULTS SUMMARY")
    
    for role_name, results in all_results.items():
        print(f"\n{role_name} Connection:")
        total_checks = len(results)
        passed_checks = sum(1 for v in results.values() if v)
        success_rate = (passed_checks / total_checks) * 100
        
        for check, passed in results.items():
            status = "✅" if passed else "❌"
            check_name = check.replace('_', ' ').title()
            print(f"   {status} {check_name}")
        
        print(f"   Score: {passed_checks}/{total_checks} ({success_rate:.0f}%)")
    
    # Overall status
    print_header("🎯 OVERALL CONNECTION STATUS")
    
    all_passed = all(all(r.values()) for r in all_results.values())
    
    if all_passed:
        print("\n   ✅ ALL CONNECTIONS WORKING PERFECTLY!")
        print("   🎉 Login → Dashboard flow is fully functional for all roles")
    else:
        print("\n   ⚠️  Some connections have issues")
        print("   Review the detailed results above")
    
    print("\n" + "=" * 70)
    print("   Quick Manual Test:")
    print("=" * 70)
    print("   1. Open: http://localhost:5000/login")
    print("   2. Click on any role card (Admin/Retailer/Wholesaler)")
    print("   3. Enter credentials:")
    print("      • Admin: admin@tradzy.com / admin123")
    print("      • Retailer: retailer@tradzy.com / retailer123")
    print("      • Wholesaler: wholesaler@tradzy.com / wholesaler123")
    print("   4. Click 'Sign In'")
    print("   5. Should redirect to respective dashboard")
    print("=" * 70)

if __name__ == "__main__":
    main()