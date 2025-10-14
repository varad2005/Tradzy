"""Wholesaler-specific routes for the TRADZY platform.

This module provides endpoints for wholesaler users to manage their
wholesale operations, including product catalog management, bulk order
processing, and sales analytics.
"""

from __future__ import annotations

from typing import Any

from flask import Blueprint, jsonify, request, session

from db import get_db
from routes.auth import wholesaler_required

wholesaler_bp = Blueprint("wholesaler", __name__, url_prefix="/api/wholesaler")


@wholesaler_bp.route("/dashboard", methods=["GET"])
@wholesaler_required
def get_dashboard() -> tuple[Any, int]:
    """Get wholesaler dashboard statistics and overview.
    
    Returns:
        JSON response with dashboard data including:
        - Total products listed
        - Total orders received
        - Revenue statistics
        - Recent activity
    """
    db = get_db()
    user_id = session["user_id"]
    
    # Get wholesaler's product statistics
    products_stats = db.execute(
        """
        SELECT 
            COUNT(*) as total_products,
            COALESCE(SUM(stock), 0) as total_stock,
            COUNT(CASE WHEN stock > 0 THEN 1 END) as in_stock_products
        FROM products 
        WHERE retailer_id = ?
        """,
        (user_id,),
    ).fetchone()
    
    # Get order statistics (orders containing wholesaler's products)
    orders_stats = db.execute(
        """
        SELECT 
            COUNT(DISTINCT o.id) as total_orders,
            COALESCE(SUM(oi.quantity * oi.price), 0) as total_revenue
        FROM orders o
        JOIN order_items oi ON o.id = oi.order_id
        JOIN products p ON oi.product_id = p.id
        WHERE p.retailer_id = ?
        """,
        (user_id,),
    ).fetchone()
    
    return jsonify({
        "products": {
            "total": products_stats["total_products"],
            "in_stock": products_stats["in_stock_products"],
            "total_stock_units": products_stats["total_stock"],
        },
        "orders": {
            "total": orders_stats["total_orders"],
            "revenue": float(orders_stats["total_revenue"]),
        },
    }), 200


@wholesaler_bp.route("/products", methods=["GET"])
@wholesaler_required
def get_products() -> tuple[Any, int]:
    """Get all products listed by this wholesaler.
    
    Query Parameters:
        category (optional): Filter by product category
        in_stock (optional): If 'true', only return products with stock > 0
    
    Returns:
        JSON array of product objects
    """
    db = get_db()
    user_id = session["user_id"]
    
    # Build query with optional filters
    query = """
        SELECT 
            id, name, description, price, stock, category, 
            image_url, created_at, updated_at
        FROM products 
        WHERE retailer_id = ?
    """
    params = [user_id]
    
    # Add category filter if provided
    category = request.args.get("category")
    if category:
        query += " AND category = ?"
        params.append(category)
    
    # Add stock filter if provided
    in_stock = request.args.get("in_stock")
    if in_stock and in_stock.lower() == "true":
        query += " AND stock > 0"
    
    query += " ORDER BY created_at DESC"
    
    products = db.execute(query, params).fetchall()
    
    return jsonify([dict(row) for row in products]), 200


@wholesaler_bp.route("/products/<int:product_id>", methods=["GET"])
@wholesaler_required
def get_product(product_id: int) -> tuple[Any, int]:
    """Get details of a specific product owned by this wholesaler.
    
    Args:
        product_id: ID of the product to retrieve
        
    Returns:
        JSON object with product details
    """
    db = get_db()
    user_id = session["user_id"]
    
    product = db.execute(
        """
        SELECT 
            id, name, description, price, stock, category,
            image_url, created_at, updated_at
        FROM products 
        WHERE id = ? AND retailer_id = ?
        """,
        (product_id, user_id),
    ).fetchone()
    
    if not product:
        return jsonify({"error": "Product not found or access denied"}), 404
    
    return jsonify(dict(product)), 200


@wholesaler_bp.route("/orders", methods=["GET"])
@wholesaler_required
def get_orders() -> tuple[Any, int]:
    """Get all orders containing this wholesaler's products.
    
    Query Parameters:
        status (optional): Filter by order status (pending, confirmed, shipped, delivered, cancelled)
        
    Returns:
        JSON array of order objects with item details
    """
    db = get_db()
    user_id = session["user_id"]
    
    query = """
        SELECT DISTINCT
            o.id, o.user_id, o.total_amount, o.status,
            o.created_at, o.updated_at,
            u.username as customer_username,
            u.email as customer_email
        FROM orders o
        JOIN order_items oi ON o.id = oi.order_id
        JOIN products p ON oi.product_id = p.id
        JOIN users u ON o.user_id = u.id
        WHERE p.retailer_id = ?
    """
    params = [user_id]
    
    # Add status filter if provided
    status = request.args.get("status")
    if status:
        query += " AND o.status = ?"
        params.append(status)
    
    query += " ORDER BY o.created_at DESC"
    
    orders = db.execute(query, params).fetchall()
    
    # For each order, get the items that belong to this wholesaler
    result = []
    for order in orders:
        items = db.execute(
            """
            SELECT 
                oi.id, oi.quantity, oi.price,
                p.id as product_id, p.name as product_name
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id = ? AND p.retailer_id = ?
            """,
            (order["id"], user_id),
        ).fetchall()
        
        order_dict = dict(order)
        order_dict["items"] = [dict(item) for item in items]
        result.append(order_dict)
    
    return jsonify(result), 200


@wholesaler_bp.route("/stats", methods=["GET"])
@wholesaler_required
def get_stats() -> tuple[Any, int]:
    """Get detailed statistics for wholesaler analytics.
    
    Returns:
        JSON object with:
        - Sales by category
        - Top selling products
        - Revenue trends
        - Customer count
    """
    db = get_db()
    user_id = session["user_id"]
    
    # Sales by category
    category_sales = db.execute(
        """
        SELECT 
            p.category,
            COUNT(DISTINCT oi.order_id) as order_count,
            SUM(oi.quantity) as units_sold,
            SUM(oi.quantity * oi.price) as revenue
        FROM products p
        JOIN order_items oi ON p.id = oi.product_id
        WHERE p.retailer_id = ?
        GROUP BY p.category
        ORDER BY revenue DESC
        """,
        (user_id,),
    ).fetchall()
    
    # Top selling products
    top_products = db.execute(
        """
        SELECT 
            p.id, p.name, p.category,
            SUM(oi.quantity) as units_sold,
            SUM(oi.quantity * oi.price) as revenue
        FROM products p
        JOIN order_items oi ON p.id = oi.product_id
        WHERE p.retailer_id = ?
        GROUP BY p.id
        ORDER BY units_sold DESC
        LIMIT 10
        """,
        (user_id,),
    ).fetchall()
    
    # Unique customer count
    customer_count = db.execute(
        """
        SELECT COUNT(DISTINCT o.user_id) as count
        FROM orders o
        JOIN order_items oi ON o.id = oi.order_id
        JOIN products p ON oi.product_id = p.id
        WHERE p.retailer_id = ?
        """,
        (user_id,),
    ).fetchone()
    
    return jsonify({
        "category_sales": [dict(row) for row in category_sales],
        "top_products": [dict(row) for row in top_products],
        "customer_count": customer_count["count"],
    }), 200
