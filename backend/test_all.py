import requests
import json
from time import sleep

BASE_URL = 'http://localhost:5000/api'

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

def print_test(message):
    print(f"\n{Colors.HEADER}=== {message} ==={Colors.ENDC}")

def print_response(response, expected_status=200):
    status = Colors.OKGREEN if response.status_code == expected_status else Colors.FAIL
    print(f"{status}Status: {response.status_code}{Colors.ENDC}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_api():
    session = requests.Session()
    
    try:
        # 1. Test API Connection
        print_test("Testing API Connection")
        response = session.get(f"{BASE_URL}/test")
        print_response(response)
        
        if response.status_code != 200:
            print(f"{Colors.FAIL}API not responding. Please make sure the Flask server is running.{Colors.ENDC}")
            return
        
        # 2. Register Users
        print_test("Registering Admin User")
        admin_data = {
            "username": "admin",
            "password": "admin123",
            "email": "admin@tradzy.com",
            "role": "admin"
        }
        response = session.post(f"{BASE_URL}/register", json=admin_data)
        print_response(response, 201)
        
        print_test("Registering Retailer")
        retailer_data = {
            "username": "shop1",
            "password": "shop123",
            "email": "shop@tradzy.com",
            "role": "retailer"
        }
        response = session.post(f"{BASE_URL}/register", json=retailer_data)
        print_response(response, 201)
        
        # 3. Test Login
        print_test("Testing Admin Login")
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        response = session.post(f"{BASE_URL}/login", json=login_data)
        print_response(response)
        
        # 4. Test Admin Functions
        print_test("Getting User List (Admin)")
        response = session.get(f"{BASE_URL}/admin/users")
        print_response(response)
        
        print_test("Getting System Stats (Admin)")
        response = session.get(f"{BASE_URL}/admin/stats")
        print_response(response)
        
        # 5. Login as Retailer
        print_test("Testing Retailer Login")
        login_data = {
            "username": "shop1",
            "password": "shop123"
        }
        response = session.post(f"{BASE_URL}/login", json=login_data)
        print_response(response)
        
        # 6. Test Product Management
        print_test("Adding New Product")
        product_data = {
            "name": "Test Product",
            "description": "This is a test product",
            "price": 99.99,
            "stock": 10,
            "image_url": "https://example.com/test.jpg"
        }
        response = session.post(f"{BASE_URL}/products", json=product_data)
        print_response(response, 201)
        
        # Get product list to get the ID
        response = session.get(f"{BASE_URL}/products")
        products = response.json()
        if products:
            product_id = products[0]['id']
            
            print_test("Updating Product")
            update_data = {
                "name": "Updated Product",
                "description": "This is an updated test product",
                "price": 149.99,
                "stock": 20,
                "image_url": "https://example.com/updated.jpg"
            }
            response = session.put(f"{BASE_URL}/products/{product_id}", json=update_data)
            print_response(response)
            
            print_test("Deleting Product")
            response = session.delete(f"{BASE_URL}/products/{product_id}")
            print_response(response)
        
        # 7. Test Logout
        print_test("Testing Logout")
        response = session.post(f"{BASE_URL}/logout")
        print_response(response)
        
        print(f"\n{Colors.OKGREEN}All tests completed successfully!{Colors.ENDC}")
        
    except requests.exceptions.ConnectionError:
        print(f"{Colors.FAIL}Error: Could not connect to server. Make sure the Flask application is running.{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.FAIL}Error occurred: {str(e)}{Colors.ENDC}")

if __name__ == "__main__":
    test_api()