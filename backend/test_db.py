"""Database connectivity and schema checks using pytest and Flask test client."""

from __future__ import annotations

import secrets
import sqlite3
from pathlib import Path
from typing import Generator

import pytest  # type: ignore

from app import create_app
from config import TestingConfig
from db import get_db, init_db

_REQUIRED_TABLES = {
    "users",
    "products",
    "orders",
    "order_items",
    "carts",
    "cart_items",
    "wishlists",
    "wishlist_items",
    "contact_messages",
}


@pytest.fixture(scope="function")
def app(tmp_path_factory) -> Generator:
    """Provide a Flask application wired to an isolated SQLite database."""

    database_path = tmp_path_factory.mktemp("data") / "tradzy_db.sqlite"

    class ConfigUnderTest(TestingConfig):
        DATABASE = str(database_path)

    flask_app = create_app(ConfigUnderTest)

    with flask_app.app_context():
        init_db()

    yield flask_app


@pytest.fixture(scope="function")
def db_connection(app):
    """Return a raw sqlite3 connection for schema assertions."""

    database_path = Path(app.config["DATABASE"])
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
    finally:
        connection.close()


def test_schema_contains_required_tables(db_connection):
    """The schema initialisation should create all core tables."""

    cursor = db_connection.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table'"
    )
    existing_tables = {row["name"] for row in cursor.fetchall()}
    missing = _REQUIRED_TABLES.difference(existing_tables)

    assert not missing, f"Expected tables missing from schema: {missing}"


def test_user_and_product_insertion(app):
    """Users and products can be inserted using the application database helper."""

    with app.app_context():
        db = get_db()

        cursor = db.execute(
            "INSERT INTO users (username, password, email, role) VALUES (?, ?, ?, ?)",
            ("admin_test", "hashed-password", "admin_test@tradzy.com", "admin"),
        )
        user_id = cursor.lastrowid
        db.execute(
            "INSERT INTO products (name, price, stock, retailer_id) VALUES (?, ?, ?, ?)",
            ("Sample Product", 19.99, 5, user_id),
        )
        db.commit()

        user = db.execute(
            "SELECT username, role FROM users WHERE username = ?",
            ("admin_test",),
        ).fetchone()
        product = db.execute(
            "SELECT name, stock FROM products WHERE name = ?",
            ("Sample Product",),
        ).fetchone()

        assert user is not None
        assert user["role"] == "admin"
        assert product is not None
        assert product["stock"] == 5


def test_env_file_generation(tmp_path):
    """Generating an application .env file should include required secrets."""

    env_path = tmp_path / ".env"
    secret_key = secrets.token_hex(24)
    contents = (
        "DB_HOST=localhost\n"
        "DB_USER=test_user\n"
        "DB_PASSWORD=test_password\n"
        "DB_NAME=tradzy\n"
        f"SECRET_KEY={secret_key}\n"
    )
    env_path.write_text(contents, encoding="utf-8")

    stored = env_path.read_text(encoding="utf-8")
    assert f"SECRET_KEY={secret_key}" in stored
    assert stored.count("\n") >= 4


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__]))