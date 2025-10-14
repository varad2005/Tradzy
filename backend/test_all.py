"""End-to-end smoke tests executed in-process via Flask's test client.

The legacy version of this module depended on ``requests`` and a running
development server.  The tests now run entirely inside pytest and mirror the
structure introduced in ``test_basic.py``.
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


def _logout(client) -> None:
    response = client.post("/api/auth/logout")
    assert response.status_code == 200
    assert response.get_json()["message"] == "Logged out successfully"




def test_api_connection(client):
    """API health endpoint should respond with a 200 status."""

    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_full_flow(client):
    """Replicate the legacy end-to-end flow using in-process requests."""

    admin_email = "admin@tradzy.com"
    retailer_email = "shop@tradzy.com"

    _register_user(
        client,
        username="admin",
        email=admin_email,
        password="admin123",
        role="admin",
    )
    _register_user(
        client,
        username="shop1",
        email=retailer_email,
        password="shop123",
        role="retailer",
    )

    admin_login = _login(client, email=admin_email, password="admin123")
    assert admin_login["user"]["role"] == "admin"
    assert admin_login["redirect"] == "/dashboard/admin"

    users_response = client.get("/api/admin/users")
    assert users_response.status_code == 200
    users = users_response.get_json()
    roles = {user["role"] for user in users}
    assert roles.issuperset({"admin", "retailer"})

    stats_response = client.get("/api/admin/stats")
    assert stats_response.status_code == 200
    stats = stats_response.get_json()
    assert set(stats.keys()) == {"users", "products", "orders", "revenue"}

    # Logging in a different user implicitly clears the previous session.
    retailer_login = _login(client, email=retailer_email, password="shop123")
    assert retailer_login["user"]["role"] == "retailer"
    assert retailer_login["redirect"] == "/dashboard/retailer"

    create_response = client.post(
        "/api/products",
        json={
            "name": "Test Product",
            "description": "This is a test product",
            "price": 99.99,
            "stock": 10,
            "image_url": "https://example.com/test.jpg",
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
            "name": "Updated Product",
            "description": "This is an updated test product",
            "price": 149.99,
            "stock": 20,
            "image_url": "https://example.com/updated.jpg",
        },
    )
    assert update_response.status_code == 200
    assert update_response.get_json()["message"] == "Product updated successfully"

    delete_response = client.delete(f"/api/products/{product_id}")
    assert delete_response.status_code == 200
    assert delete_response.get_json()["message"] == "Product deleted successfully"

    final_list = client.get("/api/products")
    assert final_list.status_code == 200
    assert final_list.get_json() == []

    _logout(client)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__]))