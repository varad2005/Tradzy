from __future__ import annotations

from typing import Any

from flask import Blueprint, jsonify, request, session

from db import get_db
from routes.auth import login_required, role_required


wishlist_bp = Blueprint("wishlist", __name__, url_prefix="/api/wishlist")


ALLOWED_WISHLIST_ROLES = {"retailer", "wholesaler"}


def _ensure_wishlist(user_id: int) -> int:
    db = get_db()
    wishlist = db.execute(
        "SELECT id FROM wishlists WHERE user_id = ?",
        (user_id,),
    ).fetchone()
    if wishlist:
        return wishlist["id"]

    cursor = db.execute(
        "INSERT INTO wishlists (user_id) VALUES (?)",
        (user_id,),
    )
    db.commit()
    return cursor.lastrowid


@wishlist_bp.get("")
@login_required
@role_required(ALLOWED_WISHLIST_ROLES)
def get_wishlist() -> tuple[Any, int]:
    user_id = session["user_id"]
    wishlist_id = _ensure_wishlist(user_id)
    db = get_db()

    items = db.execute(
        """
        SELECT wi.id, wi.product_id, p.name, p.price, p.stock, p.image_url
        FROM wishlist_items wi
        JOIN products p ON wi.product_id = p.id
        WHERE wi.wishlist_id = ?
        ORDER BY wi.created_at DESC
        """,
        (wishlist_id,),
    ).fetchall()

    return (
        jsonify(
            {
                "wishlist_id": wishlist_id,
                "items": [dict(item) for item in items],
            }
        ),
        200,
    )


@wishlist_bp.post("/items")
@login_required
@role_required(ALLOWED_WISHLIST_ROLES)
def add_wishlist_item() -> tuple[Any, int]:
    payload = request.get_json() or {}
    product_id = payload.get("product_id")

    if not product_id:
        return jsonify({"error": "Product ID is required"}), 400

    db = get_db()
    product_exists = db.execute(
        "SELECT id FROM products WHERE id = ?",
        (product_id,),
    ).fetchone()
    if product_exists is None:
        return jsonify({"error": "Product not found"}), 404

    wishlist_id = _ensure_wishlist(session["user_id"])

    existing = db.execute(
        "SELECT id FROM wishlist_items WHERE wishlist_id = ? AND product_id = ?",
        (wishlist_id, product_id),
    ).fetchone()
    if existing:
        return jsonify({"message": "Product already in wishlist"}), 200

    db.execute(
        "INSERT INTO wishlist_items (wishlist_id, product_id) VALUES (?, ?)",
        (wishlist_id, product_id),
    )
    db.commit()

    return jsonify({"message": "Product added to wishlist"}), 201


@wishlist_bp.delete("/items/<int:item_id>")
@login_required
@role_required(ALLOWED_WISHLIST_ROLES)
def remove_wishlist_item(item_id: int) -> tuple[Any, int]:
    db = get_db()
    item = db.execute(
        """
        SELECT wi.id, w.user_id
        FROM wishlist_items wi
        JOIN wishlists w ON wi.wishlist_id = w.id
        WHERE wi.id = ?
        """,
        (item_id,),
    ).fetchone()

    if not item or item["user_id"] != session["user_id"]:
        return jsonify({"error": "Wishlist item not found"}), 404

    db.execute("DELETE FROM wishlist_items WHERE id = ?", (item_id,))
    db.commit()

    return jsonify({"message": "Wishlist item removed"}), 200
