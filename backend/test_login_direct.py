"""Quick script to test login credentials directly."""

import requests
import json

BASE_URL = "http://localhost:5000/api/auth"

# Test credentials
test_users = [
    {"email": "admin@tradzy.com", "password": "AdminPass123!", "role": "admin"},
    {"email": "retail_nova@tradzy.com", "password": "RetailPass123!", "role": "retailer"},
    {"email": "wholesale_atlas@tradzy.com", "password": "WholePass123!", "role": "wholesaler"},
]

print("=" * 70)
print("🔐 TESTING LOGIN CREDENTIALS")
print("=" * 70)

for user in test_users:
    print(f"\n📧 Testing: {user['email']}")
    print(f"🔑 Password: {user['password']}")
    print(f"👤 Expected Role: {user['role']}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/login",
            json={"email": user["email"], "password": user["password"]},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ LOGIN SUCCESS!")
            print(f"   Username: {data['user']['username']}")
            print(f"   Role: {data['user']['role']}")
            print(f"   Token: {data['access_token'][:50]}...")
        else:
            print(f"❌ LOGIN FAILED: {response.status_code}")
            print(f"   Error: {response.json().get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ CONNECTION ERROR: {str(e)}")

print("\n" + "=" * 70)
print("✅ Test complete!")
print("=" * 70)
