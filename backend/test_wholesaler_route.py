"""Test script to diagnose wholesaler.html route error."""

from app import app

app.config['TESTING'] = True

with app.test_client() as client:
    try:
        response = client.get('/wholesaler.html')
        print(f"Status Code: {response.status_code}")
        if response.status_code != 200:
            print(f"Response Data: {response.data.decode('utf-8')[:500]}")
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
