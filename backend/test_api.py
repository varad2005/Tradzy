import requests
import json

BASE_URL = 'http://localhost:5000/api'

def test_user_registration():
    print("\nTesting User Registration...")
    
    # Test admin registration
    admin_data = {
        "username": "admin_user",
        "password": "admin123",
        "email": "admin@tradzy.com",
        "role": "admin"
    }
    response = requests.post(f"{BASE_URL}/register", json=admin_data)
    print(f"Admin Registration: {response.status_code}")
    print(response.json())

    # Test retailer registration
    retailer_data = {
        "username": "retailer_user",
        "password": "retailer123",
        "email": "retailer@tradzy.com",
        "role": "retailer"
    }
    response = requests.post(f"{BASE_URL}/register", json=retailer_data)
    print(f"Retailer Registration: {response.status_code}")
    print(response.json())

    # Test customer registration
    customer_data = {
        "username": "customer_user",
        "password": "customer123",
        "email": "customer@tradzy.com",
        "role": "customer"
    }
    response = requests.post(f"{BASE_URL}/register", json=customer_data)
    print(f"Customer Registration: {response.status_code}")
    print(response.json())

def test_login():
    print("\nTesting Login...")
    
    # Test admin login
    login_data = {
        "username": "admin_user",
        "password": "admin123"
    }
    response = requests.post(f"{BASE_URL}/login", json=login_data)
    print(f"Admin Login: {response.status_code}")
    print(response.json())
    
    # Store the session cookie if needed for future requests
    admin_cookies = response.cookies

    # Test retailer login
    login_data = {
        "username": "retailer_user",
        "password": "retailer123"
    }
    response = requests.post(f"{BASE_URL}/login", json=login_data)
    print(f"Retailer Login: {response.status_code}")
    print(response.json())
    
    retailer_cookies = response.cookies

    return admin_cookies, retailer_cookies

def test_product_management(retailer_cookies):
    print("\nTesting Product Management...")
    
    # Add a product
    product_data = {
        "name": "Test Product",
        "description": "This is a test product",
        "price": 99.99,
        "stock": 10,
        "image_url": "https://example.com/test.jpg"
    }
    response = requests.post(f"{BASE_URL}/products", json=product_data, cookies=retailer_cookies)
    print(f"Add Product: {response.status_code}")
    print(response.json())

    # Get all products
    response = requests.get(f"{BASE_URL}/products")
    print(f"Get Products: {response.status_code}")
    products = response.json()
    print(f"Number of products: {len(products)}")

    if len(products) > 0:
        product_id = products[0]['id']
        
        # Update product
        update_data = {
            "name": "Updated Test Product",
            "description": "This is an updated test product",
            "price": 149.99,
            "stock": 20,
            "image_url": "https://example.com/updated.jpg"
        }
        response = requests.put(f"{BASE_URL}/products/{product_id}", json=update_data, cookies=retailer_cookies)
        print(f"Update Product: {response.status_code}")
        print(response.json())

        # Delete product
        response = requests.delete(f"{BASE_URL}/products/{product_id}", cookies=retailer_cookies)
        print(f"Delete Product: {response.status_code}")
        print(response.json())

def test_admin_functions(admin_cookies):
    print("\nTesting Admin Functions...")
    
    # Get all users
    response = requests.get(f"{BASE_URL}/admin/users", cookies=admin_cookies)
    print(f"Get Users: {response.status_code}")
    print(response.json())

    # Get statistics
    response = requests.get(f"{BASE_URL}/admin/stats", cookies=admin_cookies)
    print(f"Get Stats: {response.status_code}")
    print(response.json())

def main():
    try:
        # Test registration
        test_user_registration()
        
        # Test login and get cookies
        admin_cookies, retailer_cookies = test_login()
        
        # Test product management with retailer account
        test_product_management(retailer_cookies)
        
        # Test admin functions
        test_admin_functions(admin_cookies)
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server. Make sure the Flask application is running.")
    except Exception as e:
        print(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    main()