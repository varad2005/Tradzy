from __future__ import annotations

from typing import Any

from flask import Blueprint, jsonify, request, session

from db import get_db
from routes.auth import login_required, role_required

products_bp = Blueprint("products", __name__, url_prefix="/api/products")


@products_bp.get("")
def list_products() -> tuple[Any, int]:
    params = request.args
    search_term = params.get("search", "").strip().lower()
    category = params.get("category", "").strip().lower()

    db = get_db()
    query = [
        "SELECT p.id, p.name, p.description, p.price, p.stock, p.image_url,",
        "p.retailer_id AS owner_id,",
        "u.username AS owner_username, u.role AS owner_role, p.created_at",
        "FROM products p",
        "LEFT JOIN users u ON p.retailer_id = u.id",
        "WHERE 1=1",
    ]
    args: list[Any] = []

    if search_term:
        query.append("AND (LOWER(p.name) LIKE ? OR LOWER(p.description) LIKE ?)")
        wildcard = f"%{search_term}%"
        args.extend([wildcard, wildcard])

    if category:
        query.append("AND LOWER(p.category) = ?")
        args.append(category)

    query.append("ORDER BY p.created_at DESC")

    products = db.execute(" ".join(query), args).fetchall()
    return jsonify([dict(product) for product in products]), 200


@products_bp.post("")
@login_required
@role_required(["admin", "retailer", "wholesaler"])
def create_product() -> tuple[Any, int]:
    payload = request.get_json() or {}
    required = {"name", "price", "stock"}
    if not required.issubset(payload.keys()):
        return jsonify({"error": "Missing required fields"}), 400

    db = get_db()
    db.execute(
        """
        INSERT INTO products (name, description, price, stock, retailer_id, image_url, category)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            payload["name"],
            payload.get("description", ""),
            float(payload["price"]),
            int(payload["stock"]),
            session["user_id"],
            payload.get("image_url"),
            (payload.get("category") or "").lower() or None,
        ),
    )
    db.commit()

    return jsonify({"message": "Product created successfully"}), 201


def _ensure_product_permission(product_id: int) -> tuple[Any, int] | None:
    db = get_db()
    product = db.execute(
        "SELECT id, retailer_id FROM products WHERE id = ?",
        (product_id,),
    ).fetchone()

    if product is None:
        return jsonify({"error": "Product not found"}), 404

    if session.get("role") != "admin" and product["retailer_id"] != session.get("user_id"):
        return jsonify({"error": "Permission denied"}), 403

    return None


@products_bp.get("/<int:product_id>")
def retrieve_product(product_id: int) -> tuple[Any, int]:
    db = get_db()
    product = db.execute(
        """
        SELECT p.id, p.name, p.description, p.price, p.stock, p.image_url,
               p.category, p.created_at, u.username AS owner_username, u.role AS owner_role
        FROM products p
        LEFT JOIN users u ON p.retailer_id = u.id
        WHERE p.id = ?
        """,
        (product_id,),
    ).fetchone()

    if product is None:
        return jsonify({"error": "Product not found"}), 404

    return jsonify(dict(product)), 200


@products_bp.put("/<int:product_id>")
@login_required
def update_product(product_id: int) -> tuple[Any, int]:
    permission_error = _ensure_product_permission(product_id)
    if permission_error:
        return permission_error

    payload = request.get_json() or {}
    allowed_fields = {"name", "description", "price", "stock", "image_url", "category"}
    if not any(field in payload for field in allowed_fields):
        return jsonify({"error": "No fields to update"}), 400

    fields = []
    values: list[Any] = []
    for field in allowed_fields:
        if field in payload:
            fields.append(f"{field} = ?")
            value = payload[field]
            if field == "price":
                value = float(value)
            if field == "stock":
                value = int(value)
            if field == "category" and value:
                value = value.lower()
            values.append(value)

    values.append(product_id)

    db = get_db()
    fields.append("updated_at = CURRENT_TIMESTAMP")
    db.execute(
        f"UPDATE products SET {', '.join(fields)} WHERE id = ?",
        tuple(values),
    )
    db.commit()

    return jsonify({"message": "Product updated successfully"}), 200


@products_bp.delete("/<int:product_id>")
@login_required
def delete_product(product_id: int) -> tuple[Any, int]:
    permission_error = _ensure_product_permission(product_id)
    if permission_error:
        return permission_error

    db = get_db()
    db.execute("DELETE FROM products WHERE id = ?", (product_id,))
    db.commit()

    return jsonify({"message": "Product deleted successfully"}), 200