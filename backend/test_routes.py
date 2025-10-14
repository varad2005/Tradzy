"""Test all routes to ensure no TemplateNotFound errors."""

from app import create_app
from config import Config

class TestConfig(Config):
    TESTING = True

app = create_app(TestConfig)

routes_to_test = [
    ('/', 'Homepage'),
    ('/login', 'Login page'),
    ('/contact', 'Contact page'),
    ('/products', 'Products page'),
    ('/admin.html', 'Admin login'),
    ('/retailer.html', 'Retailer login'),
    ('/wholesaler.html', 'Wholesaler login'),
    ('/api/health', 'API health'),
]

print("Testing all routes...\n")
print("=" * 60)

with app.test_client() as client:
    for route, description in routes_to_test:
        try:
            response = client.get(route)
            status = "✅" if response.status_code == 200 else f"⚠️  ({response.status_code})"
            print(f"{status} {route:25} - {description}")
        except Exception as e:
            print(f"❌ {route:25} - ERROR: {e}")

print("=" * 60)
print("\nTesting error handlers...\n")

# Test 404 handler
with app.test_client() as client:
    response = client.get('/nonexistent-page')
    print(f"404 Handler: {'✅' if response.status_code == 404 else '❌'} (Status: {response.status_code})")

# Test API 404
with app.test_client() as client:
    response = client.get('/api/nonexistent')
    print(f"API 404 Handler: {'✅' if response.status_code == 404 else '❌'} (Status: {response.status_code})")
    data = response.get_json()
    print(f"  Response: {data}")

print("\n" + "=" * 60)
print("✅ All route tests completed!")
