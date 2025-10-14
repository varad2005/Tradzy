from __future__ import annotations

from typing import Any

from flask import Blueprint, jsonify, request, session

from db import get_db
from routes.auth import login_required, role_required


cart_bp = Blueprint("cart", __name__, url_prefix="/api/cart")


ALLOWED_CART_ROLES = {"retailer", "wholesaler"}


def _ensure_cart(user_id: int) -> int:
    db = get_db()
    cart = db.execute(
        "SELECT id FROM carts WHERE user_id = ?",
        (user_id,),
    ).fetchone()
    if cart:
        return cart["id"]

    cursor = db.execute(
        "INSERT INTO carts (user_id) VALUES (?)",
        (user_id,),
    )
    db.commit()
    return cursor.lastrowid


@cart_bp.get("")
@login_required
@role_required(ALLOWED_CART_ROLES)
def get_cart() -> tuple[Any, int]:
    user_id = session["user_id"]
    cart_id = _ensure_cart(user_id)
    db = get_db()

    items = db.execute(
        """
        SELECT ci.id, ci.product_id, ci.quantity, p.name, p.price, p.stock,
               (p.price * ci.quantity) AS total
        FROM cart_items ci
        JOIN products p ON ci.product_id = p.id
        WHERE ci.cart_id = ?
        ORDER BY ci.id DESC
        """,
        (cart_id,),
    ).fetchall()

    total_value = sum(item["total"] for item in items)

    return (
        jsonify(
            {
                "cart_id": cart_id,
                "items": [dict(item) for item in items],
                "total": total_value,
            }
        ),
        200,
    )


@cart_bp.post("/items")
@login_required
@role_required(ALLOWED_CART_ROLES)
def add_item() -> tuple[Any, int]:
    payload = request.get_json() or {}
    product_id = payload.get("product_id")
    quantity = int(payload.get("quantity", 1))

    if not product_id or quantity <= 0:
        return jsonify({"error": "Invalid product or quantity"}), 400

    db = get_db()
    product = db.execute(
        "SELECT id, stock FROM products WHERE id = ?",
        (product_id,),
    ).fetchone()
    if product is None:
        return jsonify({"error": "Product not found"}), 404

    if product["stock"] < quantity:
        return jsonify({"error": "Insufficient stock"}), 400

    cart_id = _ensure_cart(session["user_id"])

    existing_item = db.execute(
        "SELECT id, quantity FROM cart_items WHERE cart_id = ? AND product_id = ?",
        (cart_id, product_id),
    ).fetchone()

    if existing_item:
        new_quantity = existing_item["quantity"] + quantity
        db.execute(
            "UPDATE cart_items SET quantity = ? WHERE id = ?",
            (new_quantity, existing_item["id"]),
        )
    else:
        db.execute(
            "INSERT INTO cart_items (cart_id, product_id, quantity) VALUES (?, ?, ?)",
            (cart_id, product_id, quantity),
        )

    db.commit()
    return jsonify({"message": "Item added to cart"}), 201


@cart_bp.put("/items/<int:item_id>")
@login_required
@role_required(ALLOWED_CART_ROLES)
def update_item(item_id: int) -> tuple[Any, int]:
    payload = request.get_json() or {}
    quantity = int(payload.get("quantity", 0))

    if quantity <= 0:
        return jsonify({"error": "Quantity must be greater than zero"}), 400

    db = get_db()
    item = db.execute(
        """
        SELECT ci.id, ci.cart_id, ci.product_id, c.user_id, p.stock
        FROM cart_items ci
        JOIN carts c ON ci.cart_id = c.id
        JOIN products p ON ci.product_id = p.id
        WHERE ci.id = ?
        """,
        (item_id,),
    ).fetchone()

    if not item or item["user_id"] != session["user_id"]:
        return jsonify({"error": "Item not found"}), 404

    if item["stock"] < quantity:
        return jsonify({"error": "Insufficient stock"}), 400

    db.execute(
        "UPDATE cart_items SET quantity = ? WHERE id = ?",
        (quantity, item_id),
    )
    db.commit()

    return jsonify({"message": "Cart item updated"}), 200


@cart_bp.delete("/items/<int:item_id>")
@login_required
@role_required(ALLOWED_CART_ROLES)
def remove_item(item_id: int) -> tuple[Any, int]:
    db = get_db()
    item = db.execute(
        """
        SELECT ci.id, c.user_id
        FROM cart_items ci
        JOIN carts c ON ci.cart_id = c.id
        WHERE ci.id = ?
        """,
        (item_id,),
    ).fetchone()

    if not item or item["user_id"] != session["user_id"]:
        return jsonify({"error": "Item not found"}), 404

    db.execute("DELETE FROM cart_items WHERE id = ?", (item_id,))
    db.commit()

    return jsonify({"message": "Item removed from cart"}), 200
