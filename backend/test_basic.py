import requests

def test_api():
    try:
        # Test basic API connection
        response = requests.get('http://localhost:5000/api/test')
        print("\nTesting basic API connection:")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("\nAPI is working! Now testing user registration...")
            
            # Test user registration
            user_data = {
                "username": "test_user",
                "password": "test123",
                "email": "test@tradzy.com",
                "role": "customer"
            }
            
            response = requests.post('http://localhost:5000/api/register', json=user_data)
            print("\nUser Registration Test:")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.json()}")
            
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to server. Make sure the Flask application is running.")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_api()