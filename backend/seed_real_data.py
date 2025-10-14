"""Seed the Tradzy development database with realistic data.

This module exposes a ``seed_database`` helper that can be imported by tests or
invoked as a script.  The fixture-driven tests call ``seed_database`` to create
consistent sample users, products, carts, wishlists, and orders for
end-to-end flows.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple

from werkzeug.security import generate_password_hash

from db import get_db


@dataclass(frozen=True)
class SeededUser:
    id: int
    username: str
    role: str


def _reset_tables(db) -> None:
    tables = [
        "order_items",
        "orders",
        "wishlist_items",
        "wishlists",
        "cart_items",
        "carts",
        "products",
        "users",
        "contact_messages",
    ]
    for table in tables:
        db.execute(f"DELETE FROM {table}")
    db.commit()


def seed_database(db=None) -> Dict[str, List[SeededUser]]:
    """Populate the database with realistic fixture data.

    Parameters
    ----------
    db: sqlite3.Connection | None
        Optional database connection.  When ``None`` the current Flask
        application context is used via :func:`get_db`.

    Returns
    -------
    dict
        Mapping of user categories (``admins``, ``retailers``, ``wholesalers``)
        to lists of :class:`SeededUser` records.
    """

    connection = db or get_db()
    _reset_tables(connection)

    users: Dict[str, List[SeededUser]] = {"admins": [], "retailers": [], "wholesalers": []}

    def _insert_user(username: str, email: str, role: str, password: str) -> SeededUser:
        cursor = connection.execute(
            "INSERT INTO users (username, password, email, role) VALUES (?, ?, ?, ?)",
            (username, generate_password_hash(password), email, role),
        )
        seeded = SeededUser(cursor.lastrowid, username, role)
        users[f"{role}s"].append(seeded)
        return seeded

    # Users
    admin = _insert_user("admin_master", "admin@tradzy.com", "admin", "AdminPass123!")
    retailer_a = _insert_user("retail_nova", "retail_nova@tradzy.com", "retailer", "RetailPass123!")
    retailer_b = _insert_user("retail_prism", "retail_prism@tradzy.com", "retailer", "RetailPass456!")
    wholesaler_a = _insert_user("wholesale_atlas", "wholesale_atlas@tradzy.com", "wholesaler", "WholePass123!")
    wholesaler_b = _insert_user("wholesale_vertex", "wholesale_vertex@tradzy.com", "wholesaler", "WholePass456!")

    # Carts and wishlists are created lazily when required by the API, but we
    # create empty shells for convenience.
    connection.execute("INSERT INTO carts (user_id) VALUES (?)", (retailer_a.id,))
    connection.execute("INSERT INTO wishlists (user_id) VALUES (?)", (retailer_a.id,))

    # Products owned by retailers (acting as wholesalers when selling to other retailers).
    products: List[Tuple[int, str]] = []
    product_rows = [
        ("Aurora Smart Speaker", "Voice-controlled smart speaker with premium sound", 129.99, 40, wholesaler_a.id, "electronics"),
        ("Evergreen Eco Bottle", "Insulated stainless steel bottle for daily hydration", 24.99, 200, wholesaler_a.id, "lifestyle"),
        ("Nimbus Office Chair", "Ergonomic office chair with lumbar support", 199.99, 65, wholesaler_b.id, "furniture"),
        ("Lumen LED Strip", "Smart colour changing LED strip lighting", 59.99, 150, wholesaler_b.id, "electronics"),
    ]

    for name, description, price, stock, owner_id, category in product_rows:
        cursor = connection.execute(
            """
            INSERT INTO products (name, description, price, stock, retailer_id, category)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (name, description, price, stock, owner_id, category),
        )
        products.append((cursor.lastrowid, name))

    # Seed a pending order for retailer_a with items supplied by wholesaler_a.
    cursor = connection.execute(
        "INSERT INTO orders (user_id, total_amount, status) VALUES (?, ?, ?)",
        (retailer_a.id, 129.99 + 24.99, "pending"),
    )
    order_id = cursor.lastrowid

    connection.execute(
        """
        INSERT INTO order_items (order_id, product_id, quantity, price)
        VALUES (?, ?, ?, ?)
        """,
        (order_id, products[0][0], 1, 129.99),
    )
    connection.execute(
        """
        INSERT INTO order_items (order_id, product_id, quantity, price)
        VALUES (?, ?, ?, ?)
        """,
        (order_id, products[1][0], 3, 24.99),
    )

    connection.commit()
    return users


def main() -> None:
    """Entry point for manual seeding via ``python seed_real_data.py``."""

    from app import create_app
    from config import DevelopmentConfig

    app = create_app(DevelopmentConfig)
    with app.app_context():
        from db import init_db

        init_db()
        summary = seed_database()
        total_users = sum(len(group) for group in summary.values())
        print(f"Seeded database with {total_users} users and sample catalog data.")


if __name__ == "__main__":
    main()
