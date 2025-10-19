"""
Quick test script to check login redirects while Flask is running.
Run this in a separate terminal while the Flask server is active.
"""
import requests
import time

base_url = "http://localhost:5000"

print("🔍 Quick Login Redirect Check\n")
print("=" * 60)

# Test cases
tests = [
    ("Admin", "admin@tradzy.com", "admin123", "/admin"),
    ("Retailer", "retailer@tradzy.com", "retailer123", "/retailer"),
    ("Wholesaler", "wholesaler@tradzy.com", "wholesaler123", "/wholesaler/dashboard"),
]

results = []

for role, email, password, expected_url in tests:
    print(f"\n📝 Testing {role}...")
    try:
        session = requests.Session()
        
        # Login
        response = session.post(
            f"{base_url}/api/auth/login",
            json={"email": email, "password": password},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            actual_url = data.get('redirect', 'No redirect URL')
            
            if actual_url == expected_url:
                print(f"   ✅ PASS: Redirects to {actual_url}")
                results.append(True)
            else:
                print(f"   ❌ FAIL: Expected {expected_url}, got {actual_url}")
                results.append(False)
                
            # Try accessing the dashboard
            dash_response = session.get(f"{base_url}{actual_url}", timeout=5)
            if dash_response.status_code == 200:
                print(f"   ✅ Dashboard accessible")
            else:
                print(f"   ❌ Dashboard returned {dash_response.status_code}")
        else:
            print(f"   ❌ Login failed: {response.status_code}")
            results.append(False)
            
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Cannot connect - Is server running?")
        results.append(False)
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results.append(False)
    
    time.sleep(0.5)

print("\n" + "=" * 60)
print(f"Results: {sum(results)}/{len(results)} passed")
print("=" * 60)

if all(results):
    print("✅ All login redirects working correctly!")
else:
    print("⚠️  Some tests failed - check above for details")