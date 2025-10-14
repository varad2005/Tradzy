from __future__ import annotations

import itertools
from typing import Callable, Dict, Generator

import pytest  # type: ignore

from app import create_app
from config import TestingConfig
from db import get_db, init_db
from seed_real_data import seed_database
from werkzeug.security import generate_password_hash


@pytest.fixture(scope="function")
def app(tmp_path_factory) -> Generator:
    """Provide a Flask application configured with an isolated test database."""

    database_path = tmp_path_factory.mktemp("data") / "tradzy_test.sqlite"

    class ConfigUnderTest(TestingConfig):
        DATABASE = str(database_path)
        TESTING = True
        WTF_CSRF_ENABLED = False

    flask_app = create_app(ConfigUnderTest)

    with flask_app.app_context():
        init_db()

    yield flask_app


@pytest.fixture(scope="function")
def client(app):
    """Yield a Flask test client bound to the isolated application."""

    return app.test_client()


@pytest.fixture(scope="function")
def seed_data(app) -> Dict[str, list]:
    """Seed the database with realistic data and return a summary map."""

    with app.app_context():
        return seed_database()


@pytest.fixture(scope="function")
def user_factory(app) -> Callable[..., Dict[str, str]]:
    """Factory fixture for creating users with custom attributes."""

    sequence = itertools.count(1)

    def factory(**overrides) -> Dict[str, str]:
        index = next(sequence)
        defaults = {
            "username": f"user_{index}",
            "email": f"user_{index}@tradzy.com",
            "password": "Password123!",
            "role": "retailer",
        }
        payload = {**defaults, **overrides}
        raw_password = payload["password"]
        with app.app_context():
            db = get_db()
            cursor = db.execute(
                "INSERT INTO users (username, password, email, role) VALUES (?, ?, ?, ?)",
                (
                    payload["username"],
                    generate_password_hash(raw_password),
                    payload["email"],
                    payload["role"],
                ),
            )
            db.commit()
            payload["id"] = cursor.lastrowid
            payload["password"] = raw_password
        return payload

    return factory


@pytest.fixture(scope="function")
def product_factory(app, user_factory) -> Callable[..., Dict[str, str]]:
    """Factory fixture for creating products owned by a user."""

    sequence = itertools.count(1)

    def factory(**overrides) -> Dict[str, str]:
        index = next(sequence)
        owner_id = overrides.get("retailer_id")
        if owner_id is None:
            owner = user_factory(role="wholesaler")
            owner_id = owner["id"]
        defaults = {
            "name": f"Sample Product {index}",
            "description": "Sample description",
            "price": 19.99,
            "stock": 10,
            "retailer_id": owner_id,
            "category": "general",
        }
        payload = {**defaults, **overrides}
        with app.app_context():
            db = get_db()
            cursor = db.execute(
                """
                INSERT INTO products (name, description, price, stock, retailer_id, category)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    payload["name"],
                    payload["description"],
                    payload["price"],
                    payload["stock"],
                    payload["retailer_id"],
                    payload.get("category"),
                ),
            )
            db.commit()
            payload["id"] = cursor.lastrowid
        return payload

    return factory


@pytest.fixture(scope="function")
def wholesaler_user(user_factory) -> Dict[str, str]:
    """Create a single wholesaler user for testing.
    
    Returns:
        Dict with user data including plaintext password for login tests.
    """
    return user_factory(
        username="test_wholesaler",
        email="wholesaler@test.com",
        password="WholeTest123!",
        role="wholesaler",
    )


@pytest.fixture(scope="function")
def admin_user(user_factory) -> Dict[str, str]:
    """Create a single admin user for testing.
    
    Returns:
        Dict with user data including plaintext password for login tests.
    """
    return user_factory(
        username="test_admin",
        email="admin@test.com",
        password="AdminTest123!",
        role="admin",
    )


@pytest.fixture(scope="function")
def retailer_user(user_factory) -> Dict[str, str]:
    """Create a single retailer user for testing.
    
    Returns:
        Dict with user data including plaintext password for login tests.
    """
    return user_factory(
        username="test_retailer",
        email="retailer@test.com",
        password="RetailTest123!",
        role="retailer",
    )
