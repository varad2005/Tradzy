"""Comprehensive tests for wholesaler authentication and authorization.

This module tests the complete wholesaler login flow including:
- User registration with wholesaler role
- Login success and failure scenarios
- Role-based access control for wholesaler-specific routes
- JWT token generation and validation
- Protected endpoint access
"""

from __future__ import annotations

from typing import Any, Dict

import pytest  # type: ignore


def test_wholesaler_registration(client) -> None:
    """Test wholesaler user registration."""
    
    response = client.post(
        "/api/auth/register",
        json={
            "username": "new_wholesaler",
            "email": "newwholesaler@test.com",
            "password": "WholeSale123!",
            "role": "wholesaler",
        },
    )
    
    assert response.status_code == 201
    data = response.get_json()
    assert data["message"] == "Registration successful"


def test_wholesaler_registration_duplicate_email(client, wholesaler_user) -> None:
    """Test that duplicate email registration fails."""
    
    response = client.post(
        "/api/auth/register",
        json={
            "username": "another_wholesaler",
            "email": wholesaler_user["email"],
            "password": "Password123!",
            "role": "wholesaler",
        },
    )
    
    assert response.status_code == 400
    data = response.get_json()
    assert "email" in data["error"].lower()


def test_wholesaler_login_success(client, wholesaler_user) -> None:
    """Test successful wholesaler login with correct credentials."""
    
    response = client.post(
        "/api/auth/login",
        json={
            "email": wholesaler_user["email"],
            "password": wholesaler_user["password"],
        },
    )
    
    assert response.status_code == 200
    data = response.get_json()
    
    # Verify response structure
    assert "access_token" in data
    assert "user" in data
    assert "redirect" in data
    assert data["message"] == "Login successful"
    
    # Verify user data
    assert data["user"]["role"] == "wholesaler"
    assert data["user"]["email"] == wholesaler_user["email"]
    assert data["user"]["username"] == wholesaler_user["username"]
    
    # Verify redirect path
    assert data["redirect"] == "/dashboard/wholesaler"


def test_wholesaler_login_wrong_password(client, wholesaler_user) -> None:
    """Test login failure with incorrect password."""
    
    response = client.post(
        "/api/auth/login",
        json={
            "email": wholesaler_user["email"],
            "password": "WrongPassword123!",
        },
    )
    
    assert response.status_code == 401
    data = response.get_json()
    assert "error" in data
    assert "credentials" in data["error"].lower()


def test_wholesaler_login_nonexistent_user(client) -> None:
    """Test login failure with non-existent email."""
    
    response = client.post(
        "/api/auth/login",
        json={
            "email": "nonexistent@test.com",
            "password": "Password123!",
        },
    )
    
    assert response.status_code == 401
    data = response.get_json()
    assert "error" in data


def test_wholesaler_dashboard_access(client, wholesaler_user) -> None:
    """Test that authenticated wholesaler can access dashboard endpoint."""
    
    # Login first
    login_response = client.post(
        "/api/auth/login",
        json={
            "email": wholesaler_user["email"],
            "password": wholesaler_user["password"],
        },
    )
    assert login_response.status_code == 200
    
    # Access dashboard
    response = client.get("/api/wholesaler/dashboard")
    
    assert response.status_code == 200
    data = response.get_json()
    
    # Verify dashboard structure
    assert "products" in data
    assert "orders" in data
    assert "total" in data["products"]
    assert "total" in data["orders"]


def test_wholesaler_dashboard_access_denied_unauthenticated(client) -> None:
    """Test that unauthenticated users cannot access wholesaler dashboard."""
    
    response = client.get("/api/wholesaler/dashboard")
    
    assert response.status_code == 401
    data = response.get_json()
    assert "error" in data
    assert "authentication" in data["error"].lower()


def test_wholesaler_dashboard_access_denied_wrong_role(client, retailer_user) -> None:
    """Test that non-wholesaler users cannot access wholesaler dashboard."""
    
    # Login as retailer
    login_response = client.post(
        "/api/auth/login",
        json={
            "email": retailer_user["email"],
            "password": retailer_user["password"],
        },
    )
    assert login_response.status_code == 200
    
    # Try to access wholesaler dashboard
    response = client.get("/api/wholesaler/dashboard")
    
    assert response.status_code == 403
    data = response.get_json()
    assert "error" in data
    assert "permission" in data["error"].lower()


def test_wholesaler_products_list(client, wholesaler_user, product_factory) -> None:
    """Test wholesaler can list their own products."""
    
    # Create products owned by wholesaler
    product1 = product_factory(
        retailer_id=wholesaler_user["id"],
        name="Bulk Widget A",
        price=50.00,
        stock=100,
    )
    product2 = product_factory(
        retailer_id=wholesaler_user["id"],
        name="Bulk Widget B",
        price=75.00,
        stock=200,
    )
    
    # Login as wholesaler
    client.post(
        "/api/auth/login",
        json={
            "email": wholesaler_user["email"],
            "password": wholesaler_user["password"],
        },
    )
    
    # Get products list
    response = client.get("/api/wholesaler/products")
    
    assert response.status_code == 200
    products = response.get_json()
    
    assert len(products) == 2
    product_names = {p["name"] for p in products}
    assert "Bulk Widget A" in product_names
    assert "Bulk Widget B" in product_names


def test_wholesaler_products_filter_by_category(client, wholesaler_user, product_factory) -> None:
    """Test filtering products by category."""
    
    # Create products in different categories
    product_factory(
        retailer_id=wholesaler_user["id"],
        name="Electronics Widget",
        category="electronics",
    )
    product_factory(
        retailer_id=wholesaler_user["id"],
        name="Furniture Widget",
        category="furniture",
    )
    
    # Login
    client.post(
        "/api/auth/login",
        json={
            "email": wholesaler_user["email"],
            "password": wholesaler_user["password"],
        },
    )
    
    # Filter by electronics
    response = client.get("/api/wholesaler/products?category=electronics")
    
    assert response.status_code == 200
    products = response.get_json()
    
    assert len(products) == 1
    assert products[0]["category"] == "electronics"
    assert products[0]["name"] == "Electronics Widget"


def test_wholesaler_get_specific_product(client, wholesaler_user, product_factory) -> None:
    """Test wholesaler can get details of their specific product."""
    
    product = product_factory(
        retailer_id=wholesaler_user["id"],
        name="Test Product",
        description="Test description",
    )
    
    # Login
    client.post(
        "/api/auth/login",
        json={
            "email": wholesaler_user["email"],
            "password": wholesaler_user["password"],
        },
    )
    
    # Get product details
    response = client.get(f"/api/wholesaler/products/{product['id']}")
    
    assert response.status_code == 200
    data = response.get_json()
    
    assert data["id"] == product["id"]
    assert data["name"] == "Test Product"
    assert data["description"] == "Test description"


def test_wholesaler_cannot_access_other_wholesaler_product(
    client, wholesaler_user, user_factory, product_factory
) -> None:
    """Test wholesaler cannot access another wholesaler's product."""
    
    # Create another wholesaler
    other_wholesaler = user_factory(
        username="other_wholesaler",
        email="other@test.com",
        role="wholesaler",
    )
    
    # Create product owned by other wholesaler
    product = product_factory(
        retailer_id=other_wholesaler["id"],
        name="Other's Product",
    )
    
    # Login as first wholesaler
    client.post(
        "/api/auth/login",
        json={
            "email": wholesaler_user["email"],
            "password": wholesaler_user["password"],
        },
    )
    
    # Try to access other's product
    response = client.get(f"/api/wholesaler/products/{product['id']}")
    
    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data


def test_wholesaler_stats(client, wholesaler_user, product_factory) -> None:
    """Test wholesaler can view their statistics."""
    
    # Create some products for the wholesaler
    product_factory(
        retailer_id=wholesaler_user["id"],
        name="Product 1",
        category="electronics",
    )
    product_factory(
        retailer_id=wholesaler_user["id"],
        name="Product 2",
        category="furniture",
    )
    
    # Login
    client.post(
        "/api/auth/login",
        json={
            "email": wholesaler_user["email"],
            "password": wholesaler_user["password"],
        },
    )
    
    # Get stats
    response = client.get("/api/wholesaler/stats")
    
    assert response.status_code == 200
    data = response.get_json()
    
    assert "category_sales" in data
    assert "top_products" in data
    assert "customer_count" in data


def test_role_based_redirects(client, wholesaler_user, admin_user, retailer_user) -> None:
    """Test that different roles get correct redirect paths after login."""
    
    roles_and_redirects = [
        (wholesaler_user, "/dashboard/wholesaler"),
        (admin_user, "/dashboard/admin"),
        (retailer_user, "/dashboard/retailer"),
    ]
    
    for user, expected_redirect in roles_and_redirects:
        response = client.post(
            "/api/auth/login",
            json={
                "email": user["email"],
                "password": user["password"],
            },
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["redirect"] == expected_redirect
        assert data["user"]["role"] == user["role"]
        
        # Logout between tests
        client.post("/api/auth/logout")


def test_wholesaler_logout(client, wholesaler_user) -> None:
    """Test wholesaler can logout successfully."""
    
    # Login
    login_response = client.post(
        "/api/auth/login",
        json={
            "email": wholesaler_user["email"],
            "password": wholesaler_user["password"],
        },
    )
    assert login_response.status_code == 200
    
    # Logout
    response = client.post("/api/auth/logout")
    
    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "Logged out successfully"
    
    # Verify cannot access protected routes after logout
    dashboard_response = client.get("/api/wholesaler/dashboard")
    assert dashboard_response.status_code == 401


if __name__ == "__main__":
    import sys
    
    raise SystemExit(pytest.main([__file__, "-v"] + sys.argv[1:]))
