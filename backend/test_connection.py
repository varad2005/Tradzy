import requests

def test_connection():
    try:
        response = requests.get('http://localhost:5000/api/products')
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to server")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_connection()