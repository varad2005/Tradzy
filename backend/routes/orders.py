from __future__ import annotations

from typing import Any, Iterable

from flask import Blueprint, jsonify, request, session

from db import get_db
from routes.auth import login_required, role_required
from email_utils import send_order_confirmation_email


def _fetch_order_items(order_ids: Iterable[int]) -> dict[int, list[dict[str, Any]]]:
    if not order_ids:
        return {}
    placeholders = ",".join("?" for _ in order_ids)
    db = get_db()
    rows = db.execute(
        f"""
        SELECT oi.order_id,
               oi.id,
               oi.product_id,
               oi.quantity,
               oi.price,
               p.name,
               p.retailer_id AS owner_id,
               u.username AS owner_username,
               u.role AS owner_role
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        LEFT JOIN users u ON p.retailer_id = u.id
        WHERE oi.order_id IN ({placeholders})
        ORDER BY oi.id ASC
        """,
        tuple(order_ids),
    ).fetchall()

    grouped: dict[int, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(row["order_id"], []).append(dict(row))
    return grouped


orders_bp = Blueprint("orders", __name__, url_prefix="/api/orders")


@orders_bp.get("")
@login_required
def list_orders() -> tuple[Any, int]:
    role = session.get("role")
    user_id = session.get("user_id")
    if role not in {"admin", "retailer", "wholesaler"}:
        return jsonify({"error": "Permission denied"}), 403
    db = get_db()

    if role == "retailer":
        orders = db.execute(
            """
            SELECT id, user_id, total_amount, status, created_at
            FROM orders
            WHERE user_id = ?
            ORDER BY created_at DESC
            """,
            (user_id,),
        ).fetchall()
    elif role == "wholesaler":
        orders = db.execute(
            """
            SELECT DISTINCT o.id, o.user_id, o.total_amount, o.status, o.created_at
            FROM orders o
            JOIN order_items oi ON oi.order_id = o.id
            JOIN products p ON oi.product_id = p.id
            WHERE p.retailer_id = ?
            ORDER BY o.created_at DESC
            """,
            (user_id,),
        ).fetchall()
    else:  # admin or other privileged role
        orders = db.execute(
            """
            SELECT id, user_id, total_amount, status, created_at
            FROM orders
            ORDER BY created_at DESC
            """
        ).fetchall()

    order_ids = [order["id"] for order in orders]
    items = _fetch_order_items(order_ids)

    payload = []
    for order in orders:
        payload.append(
            {
                "id": order["id"],
                "buyer_id": order["user_id"],
                "total_amount": order["total_amount"],
                "status": order["status"],
                "created_at": order["created_at"],
                "items": items.get(order["id"], []),
            }
        )

    return jsonify(payload), 200


def _resolve_items(raw_items: list[dict[str, Any]] | None, user_id: int) -> list[dict[str, Any]]:
    db = get_db()

    if raw_items is None:
        cart = db.execute("SELECT id FROM carts WHERE user_id = ?", (user_id,)).fetchone()
        if not cart:
            return []
        cart_items = db.execute(
            "SELECT product_id, quantity FROM cart_items WHERE cart_id = ?",
            (cart["id"],),
        ).fetchall()
        return [dict(item) for item in cart_items]

    return [{"product_id": item["product_id"], "quantity": int(item["quantity"]) } for item in raw_items if item.get("product_id") and int(item.get("quantity", 0)) > 0]


def _clear_cart(user_id: int) -> None:
    db = get_db()
    cart = db.execute("SELECT id FROM carts WHERE user_id = ?", (user_id,)).fetchone()
    if cart:
        db.execute("DELETE FROM cart_items WHERE cart_id = ?", (cart["id"],))
        db.commit()


@orders_bp.post("")
@login_required
@role_required(["retailer"])
def create_order() -> tuple[Any, int]:
    payload = request.get_json() or {}
    user_id = session["user_id"]

    # Get email from payload or fetch from user profile
    order_email = payload.get("email", "").strip()
    
    db = get_db()
    user = db.execute(
        "SELECT username, email FROM users WHERE id = ?",
        (user_id,),
    ).fetchone()
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Use provided email or fall back to user's registered email
    if not order_email:
        order_email = user["email"]
    
    # Validate email is provided
    if not order_email:
        return jsonify({"error": "Email is required for order confirmation"}), 400

    items_payload = payload.get("items")
    items = _resolve_items(items_payload, user_id)
    if not items:
        return jsonify({"error": "No items to order"}), 400

    order_items: list[tuple[int, float, int, str]] = []  # product_id, price, quantity, name
    total_amount = 0.0

    for item in items:
        product = db.execute(
            "SELECT id, price, stock, name FROM products WHERE id = ?",
            (item["product_id"],),
        ).fetchone()
        if product is None:
            return jsonify({"error": f"Product {item['product_id']} not found"}), 404
        if product["stock"] < item["quantity"]:
            return jsonify({"error": f"Insufficient stock for {product['name']}"}), 400

        total_amount += product["price"] * item["quantity"]
        order_items.append((product["id"], product["price"], item["quantity"], product["name"]))

    cursor = db.execute(
        "INSERT INTO orders (user_id, total_amount, status) VALUES (?, ?, ?)",
        (user_id, total_amount, payload.get("status", "pending")),
    )
    order_id = cursor.lastrowid

    for product_id, price, quantity, _ in order_items:
        db.execute(
            "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (?, ?, ?, ?)",
            (order_id, product_id, quantity, price),
        )
        db.execute(
            "UPDATE products SET stock = stock - ? WHERE id = ?",
            (quantity, product_id),
        )

    db.commit()
    if items_payload is None:
        _clear_cart(user_id)

    order_detail = {
        "id": order_id,
        "buyer_id": user_id,
        "total_amount": total_amount,
        "status": payload.get("status", "pending"),
        "items": [
            {
                "product_id": product_id,
                "price": price,
                "quantity": quantity,
                "name": name,
            }
            for product_id, price, quantity, name in order_items
        ],
    }

    # Send order confirmation email
    email_sent = send_order_confirmation_email(
        to_email=order_email,
        username=user["username"],
        order_data=order_detail,
    )

    response_data = {
        "message": "Order created successfully",
        "order": order_detail,
        "email_sent": email_sent,
        "email": order_email,
    }
    
    return jsonify(response_data), 201


_ALLOWED_STATUSES = {"pending", "confirmed", "shipped", "delivered", "cancelled"}


@orders_bp.patch("/<int:order_id>")
@login_required
def update_order(order_id: int) -> tuple[Any, int]:
    payload = request.get_json() or {}
    new_status = payload.get("status")
    if new_status not in _ALLOWED_STATUSES:
        return jsonify({"error": "Invalid status"}), 400

    db = get_db()
    order = db.execute(
        "SELECT id, user_id, status FROM orders WHERE id = ?",
        (order_id,),
    ).fetchone()
    if order is None:
        return jsonify({"error": "Order not found"}), 404

    role = session.get("role")
    user_id = session.get("user_id")

    if role == "retailer":
        if order["user_id"] != user_id:
            return jsonify({"error": "Permission denied"}), 403
        if new_status not in {"cancelled"} or order["status"] != "pending":
            return jsonify({"error": "Retailers may only cancel pending orders"}), 400
    elif role == "wholesaler":
        owns_items = db.execute(
            """
            SELECT 1
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id = ? AND p.retailer_id = ?
            LIMIT 1
            """,
            (order_id, user_id),
        ).fetchone()
        if not owns_items:
            return jsonify({"error": "Permission denied"}), 403
        if new_status not in {"confirmed", "shipped", "delivered"}:
            return jsonify({"error": "Wholesalers may only progress order fulfilment"}), 400
    elif role != "admin":
        return jsonify({"error": "Permission denied"}), 403

    db.execute(
        "UPDATE orders SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (new_status, order_id),
    )
    db.commit()

    return jsonify({"message": "Order updated", "status": new_status}), 200


@orders_bp.get("/<int:order_id>")
@login_required
def get_order(order_id: int) -> tuple[Any, int]:
    db = get_db()
    order = db.execute(
        "SELECT id, user_id, total_amount, status, created_at FROM orders WHERE id = ?",
        (order_id,),
    ).fetchone()
    if order is None:
        return jsonify({"error": "Order not found"}), 404

    role = session.get("role")
    user_id = session.get("user_id")
    if role == "retailer" and order["user_id"] != user_id:
        return jsonify({"error": "Permission denied"}), 403
    if role == "wholesaler":
        owns_items = db.execute(
            """
            SELECT 1
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id = ? AND p.retailer_id = ?
            LIMIT 1
            """,
            (order_id, user_id),
        ).fetchone()
        if not owns_items:
            return jsonify({"error": "Permission denied"}), 403

    items = _fetch_order_items([order["id"]]).get(order["id"], [])
    return (
        jsonify(
            {
                "id": order["id"],
                "buyer_id": order["user_id"],
                "total_amount": order["total_amount"],
                "status": order["status"],
                "created_at": order["created_at"],
                "items": items,
            }
        ),
        200,
    )
