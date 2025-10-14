from __future__ import annotations

from typing import Any

from flask import Blueprint, jsonify, request

from db import get_db
from routes.auth import login_required, role_required

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


@admin_bp.get("/users")
@login_required
@role_required(["admin"])
def list_users() -> tuple[Any, int]:
    db = get_db()
    users = db.execute(
        "SELECT id, username, email, role, created_at FROM users ORDER BY created_at DESC"
    ).fetchall()
    return jsonify([dict(user) for user in users]), 200


@admin_bp.delete("/users/<int:user_id>")
@login_required
@role_required(["admin"])
def remove_user(user_id: int) -> tuple[Any, int]:
    db = get_db()
    if db.execute("SELECT id FROM users WHERE id = ?", (user_id,)).fetchone() is None:
        return jsonify({"error": "User not found"}), 404

    db.execute("DELETE FROM users WHERE id = ?", (user_id,))
    db.commit()
    return jsonify({"message": "User deleted successfully"}), 200


@admin_bp.get("/stats")
@login_required
@role_required(["admin"])
def platform_stats() -> tuple[Any, int]:
    db = get_db()

    user_totals = db.execute(
        "SELECT role, COUNT(*) AS count FROM users GROUP BY role"
    ).fetchall()

    total_products = db.execute("SELECT COUNT(*) AS total FROM products").fetchone()
    total_orders = db.execute("SELECT COUNT(*) AS total FROM orders").fetchone()
    total_revenue = db.execute(
        "SELECT COALESCE(SUM(total_amount), 0) AS revenue FROM orders"
    ).fetchone()

    return (
        jsonify(
            {
                "users": [dict(row) for row in user_totals],
                "products": total_products["total"] if total_products else 0,
                "orders": total_orders["total"] if total_orders else 0,
                "revenue": total_revenue["revenue"] if total_revenue else 0,
            }
        ),
        200,
    )


@admin_bp.get("/orders")
@login_required
@role_required(["admin"])
def list_orders() -> tuple[Any, int]:
    db = get_db()
    orders = db.execute(
        """
        SELECT o.id, o.user_id AS buyer_id, u.username AS buyer_username, o.total_amount,
               o.status, o.created_at, COUNT(oi.id) AS item_count
        FROM orders o
        LEFT JOIN users u ON o.user_id = u.id
        LEFT JOIN order_items oi ON oi.order_id = o.id
        GROUP BY o.id
        ORDER BY o.created_at DESC
        """
    ).fetchall()

    return jsonify([dict(order) for order in orders]), 200


@admin_bp.patch("/orders/<int:order_id>")
@login_required
@role_required(["admin"])
def update_order_status(order_id: int) -> tuple[Any, int]:
    payload = request.get_json() or {}
    status = payload.get("status")
    if status not in {"pending", "confirmed", "shipped", "delivered", "cancelled"}:
        return jsonify({"error": "Invalid status"}), 400

    db = get_db()
    if db.execute("SELECT id FROM orders WHERE id = ?", (order_id,)).fetchone() is None:
        return jsonify({"error": "Order not found"}), 404

    db.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
    db.commit()

    return jsonify({"message": "Order status updated"}), 200