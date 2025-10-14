"""Login endpoint tests executed with pytest and Flask's test client."""

from __future__ import annotations

from typing import Dict, Generator

import pytest  # type: ignore

from app import create_app
from config import TestingConfig
from db import init_db


def _register_user(client, *, username: str, email: str, password: str, role: str) -> None:
    response = client.post(
        "/api/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password,
            "role": role,
        },
    )
    assert response.status_code == 201
    assert response.get_json()["message"] == "Registration successful"


def _login(client, *, email: str, password: str) -> tuple[Dict[str, str], int]:
    response = client.post(
        "/api/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )
    return response.get_json(), response.status_code


@pytest.fixture(scope="function")
def app(tmp_path_factory) -> Generator:
    """Provide a Flask app configured with an isolated temp database."""

    database_path = tmp_path_factory.mktemp("data") / "tradzy_login.db"

    class ConfigUnderTest(TestingConfig):
        DATABASE = str(database_path)

    flask_app = create_app(ConfigUnderTest)

    with flask_app.app_context():
        init_db()

    yield flask_app


@pytest.fixture(scope="function")
def client(app):
    """Yield a Flask test client for the login tests."""

    return app.test_client()


def test_valid_login(client):
    """A valid user should receive a JWT and redirect target."""

    email = "retailer_login@tradzy.com"
    password = "retailer123"

    _register_user(
        client,
        username="retailer_login",
        email=email,
        password=password,
        role="retailer",
    )

    payload, status = _login(client, email=email, password=password)
    assert status == 200
    assert payload["message"] == "Login successful"
    assert payload["user"]["email"] == email
    assert payload["user"]["role"] == "retailer"
    assert payload["redirect"] == "/dashboard/retailer"
    assert "access_token" in payload


def test_invalid_login(client):
    """Invalid credentials should return a 401 error."""

    payload, status = _login(client, email="invalid@tradzy.com", password="wrong")
    assert status == 401
    assert payload["error"] == "Invalid credentials"


def test_role_based_redirects(client):
    """Different roles should be redirected to their respective dashboards."""

    users = [
        ("admin_user", "admin@tradzy.com", "admin123", "admin", "/dashboard/admin"),
        ("wholesaler_user", "wholesaler@tradzy.com", "wholesaler123", "wholesaler", "/dashboard/wholesaler"),
    ]

    for username, email, password, role, redirect in users:
        _register_user(
            client,
            username=username,
            email=email,
            password=password,
            role=role,
        )
        payload, status = _login(client, email=email, password=password)
        assert status == 200
        assert payload["user"]["role"] == role
        assert payload["redirect"] == redirect


def test_session_persistence(client):
    """After login, /api/auth/check-auth should reflect the current session."""

    email = "session_user@tradzy.com"
    password = "sessionpass"

    _register_user(
        client,
        username="session_user",
        email=email,
        password=password,
        role="retailer",
    )

    payload, status = _login(client, email=email, password=password)
    assert status == 200
    assert payload["user"]["username"] == "session_user"

    check_response = client.get("/api/auth/check-auth")
    assert check_response.status_code == 200
    session_info = check_response.get_json()
    assert session_info["authenticated"] is True
    assert session_info["user"]["email"] == email


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__]))
