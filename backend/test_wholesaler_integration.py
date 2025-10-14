"""Integration test for complete wholesaler workflow.

This test verifies the entire wholesaler journey from registration
through login to performing business operations.
"""

from __future__ import annotations

import pytest  # type: ignore


def test_complete_wholesaler_workflow(client, product_factory) -> None:
    """Test complete wholesaler workflow from registration to business operations.
    
    This integration test covers:
    1. Wholesaler registration
    2. Login with credentials
    3. Creating products
    4. Viewing dashboard
    5. Managing inventory
    6. Viewing analytics
    7. Logout
    """
    
    # Step 1: Register new wholesaler
    register_response = client.post(
        "/api/auth/register",
        json={
            "username": "integration_wholesaler",
            "email": "integration@wholesale.com",
            "password": "SecurePass123!",
            "role": "wholesaler",
        },
    )
    assert register_response.status_code == 201
    print("✅ Step 1: Wholesaler registered successfully")
    
    # Step 2: Login with new account
    login_response = client.post(
        "/api/auth/login",
        json={
            "email": "integration@wholesale.com",
            "password": "SecurePass123!",
        },
    )
    assert login_response.status_code == 200
    login_data = login_response.get_json()
    
    assert login_data["user"]["role"] == "wholesaler"
    assert login_data["redirect"] == "/dashboard/wholesaler"
    assert "access_token" in login_data
    
    wholesaler_id = login_data["user"]["id"]
    print(f"✅ Step 2: Logged in as wholesaler (ID: {wholesaler_id})")
    
    # Step 3: Create products (simulating inventory addition)
    products_created = []
    for i, (name, category, price, stock) in enumerate([
        ("Bulk Electronics Package", "electronics", 1500.00, 50),
        ("Office Furniture Set", "furniture", 2500.00, 30),
        ("Industrial Supplies Kit", "supplies", 800.00, 100),
    ]):
        product = product_factory(
            retailer_id=wholesaler_id,
            name=name,
            category=category,
            price=price,
            stock=stock,
            description=f"Wholesale product {i+1}",
        )
        products_created.append(product)
    
    print(f"✅ Step 3: Created {len(products_created)} products")
    
    # Step 4: View dashboard statistics
    dashboard_response = client.get("/api/wholesaler/dashboard")
    assert dashboard_response.status_code == 200
    dashboard_data = dashboard_response.get_json()
    
    assert dashboard_data["products"]["total"] == 3
    assert dashboard_data["products"]["in_stock"] == 3
    assert dashboard_data["products"]["total_stock_units"] == 180  # 50 + 30 + 100
    
    print(f"✅ Step 4: Dashboard shows {dashboard_data['products']['total']} products")
    
    # Step 5: List all products
    products_response = client.get("/api/wholesaler/products")
    assert products_response.status_code == 200
    products_list = products_response.get_json()
    
    assert len(products_list) == 3
    product_names = {p["name"] for p in products_list}
    assert "Bulk Electronics Package" in product_names
    assert "Office Furniture Set" in product_names
    
    print(f"✅ Step 5: Listed {len(products_list)} products")
    
    # Step 6: Filter products by category
    electronics_response = client.get("/api/wholesaler/products?category=electronics")
    assert electronics_response.status_code == 200
    electronics = electronics_response.get_json()
    
    assert len(electronics) == 1
    assert electronics[0]["category"] == "electronics"
    assert electronics[0]["price"] == 1500.00
    
    print(f"✅ Step 6: Filtered products (found {len(electronics)} electronics)")
    
    # Step 7: View specific product details
    product_id = products_created[0]["id"]
    product_response = client.get(f"/api/wholesaler/products/{product_id}")
    assert product_response.status_code == 200
    product_detail = product_response.get_json()
    
    assert product_detail["id"] == product_id
    assert product_detail["stock"] == 50
    
    print(f"✅ Step 7: Retrieved product details (ID: {product_id})")
    
    # Step 8: View analytics
    stats_response = client.get("/api/wholesaler/stats")
    assert stats_response.status_code == 200
    stats_data = stats_response.get_json()
    
    assert "category_sales" in stats_data
    assert "top_products" in stats_data
    assert "customer_count" in stats_data
    
    print("✅ Step 8: Viewed analytics successfully")
    
    # Step 9: Verify access to other wholesaler's products is denied
    # Create another wholesaler and their product
    other_register = client.post(
        "/api/auth/register",
        json={
            "username": "other_wholesaler",
            "email": "other@wholesale.com",
            "password": "OtherPass123!",
            "role": "wholesaler",
        },
    )
    assert other_register.status_code == 201
    
    # Login as other wholesaler temporarily
    other_login = client.post(
        "/api/auth/login",
        json={
            "email": "other@wholesale.com",
            "password": "OtherPass123!",
        },
    )
    other_id = other_login.get_json()["user"]["id"]
    
    other_product = product_factory(
        retailer_id=other_id,
        name="Other's Product",
    )
    
    # Logout and log back in as original wholesaler
    client.post("/api/auth/logout")
    client.post(
        "/api/auth/login",
        json={
            "email": "integration@wholesale.com",
            "password": "SecurePass123!",
        },
    )
    
    # Try to access other's product - should fail
    unauthorized_response = client.get(f"/api/wholesaler/products/{other_product['id']}")
    assert unauthorized_response.status_code == 404
    
    print("✅ Step 9: Access control verified (cannot access other's products)")
    
    # Step 10: Logout
    logout_response = client.post("/api/auth/logout")
    assert logout_response.status_code == 200
    
    # Verify cannot access protected routes after logout
    protected_response = client.get("/api/wholesaler/dashboard")
    assert protected_response.status_code == 401
    
    print("✅ Step 10: Logged out successfully")
    
    print("\n🎉 Complete wholesaler workflow test PASSED!")
    print("=" * 60)
    print("Summary:")
    print(f"  - Registered and logged in as wholesaler")
    print(f"  - Created {len(products_created)} products")
    print(f"  - Viewed dashboard and analytics")
    print(f"  - Filtered and managed inventory")
    print(f"  - Verified access controls")
    print(f"  - Logged out successfully")
    print("=" * 60)


def test_role_isolation(client, admin_user, retailer_user, wholesaler_user, product_factory) -> None:
    """Test that different roles cannot access each other's protected routes."""
    
    # Create a product owned by wholesaler
    wholesaler_product = product_factory(
        retailer_id=wholesaler_user["id"],
        name="Wholesaler Product",
    )
    
    # Test 1: Admin cannot access wholesaler routes
    client.post(
        "/api/auth/login",
        json={
            "email": admin_user["email"],
            "password": admin_user["password"],
        },
    )
    
    response = client.get("/api/wholesaler/dashboard")
    assert response.status_code == 403
    print("✅ Admin blocked from wholesaler routes")
    
    client.post("/api/auth/logout")
    
    # Test 2: Retailer cannot access wholesaler routes
    client.post(
        "/api/auth/login",
        json={
            "email": retailer_user["email"],
            "password": retailer_user["password"],
        },
    )
    
    response = client.get("/api/wholesaler/products")
    assert response.status_code == 403
    print("✅ Retailer blocked from wholesaler routes")
    
    client.post("/api/auth/logout")
    
    # Test 3: Wholesaler cannot access admin routes
    client.post(
        "/api/auth/login",
        json={
            "email": wholesaler_user["email"],
            "password": wholesaler_user["password"],
        },
    )
    
    response = client.get("/api/admin/users")
    assert response.status_code == 403
    print("✅ Wholesaler blocked from admin routes")
    
    print("\n🔒 Role isolation test PASSED!")
    print("All roles properly isolated from each other's protected routes")


if __name__ == "__main__":
    import sys
    
    raise SystemExit(pytest.main([__file__, "-v", "-s"] + sys.argv[1:]))
