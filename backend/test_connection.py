"""Connection smoke test refactored to use Flask's test client and pytest."""

from __future__ import annotations

from typing import Generator

import pytest  # type: ignore

from app import create_app
from config import TestingConfig
from db import init_db


@pytest.fixture(scope="function")
def app(tmp_path_factory) -> Generator:
    """Yield a Flask application backed by a temporary database."""

    database_path = tmp_path_factory.mktemp("data") / "tradzy_connection.db"

    class ConfigUnderTest(TestingConfig):
        DATABASE = str(database_path)

    flask_app = create_app(ConfigUnderTest)

    with flask_app.app_context():
        init_db()

    yield flask_app


@pytest.fixture(scope="function")
def client(app):
    """Return a Flask test client for the app fixture."""

    return app.test_client()


def test_connection(client):
    """Products endpoint should respond successfully without a live server."""

    response = client.get("/api/products")
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__]))