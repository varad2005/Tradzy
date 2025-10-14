"""Legacy high-level API tests rewritten to use Flask's test client.

These tests exercise the happy-path flows that previously depended on a live
``flask run`` instance and the ``requests`` library.  They now run entirely
in-process with pytest fixtures, making them safe for CI/CD usage.
"""

from __future__ import annotations

from typing import Any, Dict

import pytest  # type: ignore


def _register_user(client, *, username: str, email: str, password: str, role: str) -> Dict[str, Any]:
    response = client.post(
        "/api/auth/register",
        json={
            "username": username,
            "password": password,
            "email": email,
            "role": role,
        },
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["message"] == "Registration successful"
    return data


def _login(client, *, email: str, password: str) -> Dict[str, Any]:
    response = client.post(
        "/api/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )
    assert response.status_code == 200
    return response.get_json()




def test_user_registration(client):
    """Register admin, retailer, and wholesaler accounts successfully."""

    for username, role in (
        ("admin_user", "admin"),
        ("retailer_user", "retailer"),
        ("wholesaler_user", "wholesaler"),
    ):
        _register_user(
            client,
            username=username,
            email=f"{username}@tradzy.com",
            password=f"{username}123",
            role=role,
        )


def test_login(client):
    """Logging in with valid credentials should establish a session."""

    admin_email = "admin_login@tradzy.com"
    retailer_email = "retailer_login@tradzy.com"

    _register_user(
        client,
        username="admin_login",
        email=admin_email,
        password="adminpass",
        role="admin",
    )
    _register_user(
        client,
        username="retailer_login",
        email=retailer_email,
        password="retailerpass",
        role="retailer",
    )

    admin_login = _login(client, email=admin_email, password="adminpass")
    assert admin_login["user"]["role"] == "admin"
    assert admin_login["redirect"] == "/dashboard/admin"

    retailer_login = _login(client, email=retailer_email, password="retailerpass")
    assert retailer_login["user"]["role"] == "retailer"
    assert retailer_login["redirect"] == "/dashboard/retailer"

    # Session should now reflect the retailer user.
    session_check = client.get("/api/auth/check-auth")
    assert session_check.status_code == 200
    assert session_check.get_json()["user"]["username"] == "retailer_login"


def test_product_management(client):
    """Retailers can create, update, and delete products via the API."""

    retailer_email = "retailer_products@tradzy.com"
    _register_user(
        client,
        username="retailer_products",
        email=retailer_email,
        password="retailerpass",
        role="retailer",
    )

    _login(client, email=retailer_email, password="retailerpass")

    create_response = client.post(
        "/api/products",
        json={
            "name": "Test Product",
            "description": "This is a test product",
            "price": 99.99,
            "stock": 10,
            "image_url": "https://example.com/test.jpg",
            "category": "electronics",
        },
    )
    assert create_response.status_code == 201

    list_response = client.get("/api/products")
    assert list_response.status_code == 200
    products = list_response.get_json()
    assert len(products) == 1
    product_id = products[0]["id"]

    update_response = client.put(
        f"/api/products/{product_id}",
        json={
            "name": "Updated Test Product",
            "description": "Updated description",
            "price": 149.99,
            "stock": 5,
            "image_url": "https://example.com/updated.jpg",
            "category": "gadgets",
        },
    )
    assert update_response.status_code == 200
    assert update_response.get_json()["message"] == "Product updated successfully"

    detail_response = client.get(f"/api/products/{product_id}")
    assert detail_response.status_code == 200
    detail = detail_response.get_json()
    assert detail["name"] == "Updated Test Product"
    assert detail["stock"] == 5

    delete_response = client.delete(f"/api/products/{product_id}")
    assert delete_response.status_code == 200
    assert delete_response.get_json()["message"] == "Product deleted successfully"

    final_list = client.get("/api/products")
    assert final_list.status_code == 200
    assert final_list.get_json() == []


def test_admin_functions(client):
    """Admin endpoints expose user listings and platform statistics."""

    admin_email = "admin_stats@tradzy.com"
    retailer_email = "retailer_stats@tradzy.com"

    _register_user(
        client,
        username="admin_stats",
        email=admin_email,
        password="adminpass",
        role="admin",
    )
    _register_user(
        client,
        username="retailer_stats",
        email=retailer_email,
        password="retailerpass",
        role="retailer",
    )

    # Seed at least one product so the stats endpoint has non-zero data.
    _login(client, email=retailer_email, password="retailerpass")
    client.post(
        "/api/products",
        json={
            "name": "Admin Visible Product",
            "price": 10.0,
            "stock": 3,
            "description": "Product for admin stats",
            "image_url": "https://example.com/product.jpg",
            "category": "misc",
        },
    )

    # Switch to the admin account for privileged endpoints.
    _login(client, email=admin_email, password="adminpass")

    users_response = client.get("/api/admin/users")
    assert users_response.status_code == 200
    users = users_response.get_json()
    roles = {user["role"] for user in users}
    assert roles.issuperset({"admin", "retailer"})

    stats_response = client.get("/api/admin/stats")
    assert stats_response.status_code == 200
    stats = stats_response.get_json()
    assert set(stats.keys()) == {"users", "products", "orders", "revenue"}
    assert stats["products"] >= 1


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__]))