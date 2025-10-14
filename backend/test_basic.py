"""
Basic smoke-test coverage for the Flask API using the built-in test client.

Historically this script relied on a running development server and the
``requests`` library.  The tests now execute in-process via ``app.test_client``
so they can run inside CI without extra setup.
"""

from __future__ import annotations

import pytest  # type: ignore

from db import get_db


def test_api_health_endpoint(client):
    """The API health check should respond without requiring a live server."""

    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_user_registration_flow(app, client):
    """Registering a new user should succeed and persist to the database."""

    payload = {
        "username": "test_user",
        "password": "test123",
        "email": "test_user@example.com",
        "role": "retailer",
    }

    response = client.post("/api/auth/register", json=payload)
    data = response.get_json()

    assert response.status_code == 201
    assert data["message"] == "Registration successful"

    with app.app_context():
        user = get_db().execute(
            "SELECT username, email, role, password FROM users WHERE username = ?",
            (payload["username"],),
        ).fetchone()

        assert user is not None
        assert user["email"] == payload["email"]
        assert user["role"] == payload["role"]
        # Passwords are hashed before storage; verify we did not persist raw text.
        assert user["password"] != payload["password"]


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__]))