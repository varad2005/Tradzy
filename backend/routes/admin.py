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

    # Count wholesalers and retailers
    wholesalers = db.execute(
        "SELECT COUNT(*) AS count FROM users WHERE role = 'wholesaler'"
    ).fetchone()
    
    retailers = db.execute(
        "SELECT COUNT(*) AS count FROM users WHERE role = 'retailer'"
    ).fetchone()

    total_products = db.execute("SELECT COUNT(*) AS total FROM products").fetchone()
    total_orders = db.execute("SELECT COUNT(*) AS total FROM orders").fetchone()
    total_revenue = db.execute(
        "SELECT COALESCE(SUM(total_amount), 0) AS revenue FROM orders"
    ).fetchone()

    return (
        jsonify(
            {
                "wholesalers": wholesalers["count"] if wholesalers else 0,
                "retailers": retailers["count"] if retailers else 0,
                "products": total_products["total"] if total_products else 0,
                "orders": total_orders["total"] if total_orders else 0,
                "revenue": total_revenue["revenue"] if total_revenue else 0,
            }
        ),
        200,
    )


@admin_bp.get("/wholesalers")
@login_required
@role_required(["admin"])
def list_wholesalers() -> tuple[Any, int]:
    db = get_db()
    wholesalers = db.execute(
        """
        SELECT u.id, u.username, u.email, u.created_at, 
               COUNT(DISTINCT p.id) AS products_count,
               1 AS is_active
        FROM users u
        LEFT JOIN products p ON p.retailer_id = u.id
        WHERE u.role = 'wholesaler'
        GROUP BY u.id
        ORDER BY u.created_at DESC
        """
    ).fetchall()
    
    return jsonify([{
        "id": w["id"],
        "username": w["username"],
        "email": w["email"],
        "company": w["username"],  # Using username as company for now
        "products_count": w["products_count"],
        "is_active": w["is_active"],
        "created_at": w["created_at"]
    } for w in wholesalers]), 200


@admin_bp.get("/retailers")
@login_required
@role_required(["admin"])
def list_retailers() -> tuple[Any, int]:
    db = get_db()
    retailers = db.execute(
        """
        SELECT u.id, u.username, u.email, u.created_at,
               COUNT(DISTINCT o.id) AS orders_count,
               1 AS is_active
        FROM users u
        LEFT JOIN orders o ON o.user_id = u.id
        WHERE u.role = 'retailer'
        GROUP BY u.id
        ORDER BY u.created_at DESC
        """
    ).fetchall()
    
    return jsonify([{
        "id": r["id"],
        "username": r["username"],
        "email": r["email"],
        "orders_count": r["orders_count"],
        "is_active": r["is_active"],
        "created_at": r["created_at"]
    } for r in retailers]), 200


@admin_bp.get("/orders")
@login_required
@role_required(["admin"])
def list_orders() -> tuple[Any, int]:
    db = get_db()
    orders = db.execute(
        """
        SELECT o.id, o.user_id AS buyer_id, 
               retailer.username AS retailer_name,
               wholesaler.username AS wholesaler_name,
               o.total_amount, o.status, o.created_at,
               COUNT(oi.id) AS item_count
        FROM orders o
        LEFT JOIN users retailer ON o.user_id = retailer.id
        LEFT JOIN order_items oi ON oi.order_id = o.id
        LEFT JOIN products p ON oi.product_id = p.id
        LEFT JOIN users wholesaler ON p.retailer_id = wholesaler.id
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