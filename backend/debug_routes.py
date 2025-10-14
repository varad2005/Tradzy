"""Debug script to see actual error for wholesaler.html route."""

from app import create_app
from config import Config

class DebugConfig(Config):
    DEBUG = True
    TESTING = True

app = create_app(DebugConfig)

with app.test_client() as client:
    try:
        response = client.get('/wholesaler.html')
        print(f"✅ Status: {response.status_code}")
        print(f"Content length: {len(response.data)}")
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

print("\nTesting admin.html...")
with app.test_client() as client:
    try:
        response = client.get('/admin.html')
        print(f"✅ Status: {response.status_code}")
        print(f"Content length: {len(response.data)}")
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
