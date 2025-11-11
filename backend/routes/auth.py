from __future__ import annotations

import functools
from typing import Any, Callable, Iterable

from flask import Blueprint, jsonify, request, session, url_for
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from werkzeug.security import check_password_hash, generate_password_hash

from db import get_db

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

VALID_ROLES: set[str] = {"admin", "retailer", "wholesaler"}


def login_required(view: Callable[..., Any]) -> Callable[..., Any]:
    @functools.wraps(view)
    def wrapped_view(*args: Any, **kwargs: Any) -> Any:
        if "user_id" not in session:
            return jsonify({"error": "Authentication required"}), 401
        return view(*args, **kwargs)

    return wrapped_view


def role_required(allowed_roles: Iterable[str]) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator to restrict access to routes based on user role.
    
    Args:
        allowed_roles: Iterable of role names that can access the route.
        
    Returns:
        Decorated function that checks user role before allowing access.
    """
    def decorator(view: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(view)
        def wrapped_view(*args: Any, **kwargs: Any) -> Any:
            if "user_id" not in session:
                return jsonify({"error": "Authentication required"}), 401

            db = get_db()
            user = db.execute(
                "SELECT role FROM users WHERE id = ?",
                (session["user_id"],),
            ).fetchone()

            if not user or user["role"] not in allowed_roles:
                return jsonify({"error": "Permission denied"}), 403

            return view(*args, **kwargs)

        return wrapped_view

    return decorator


# Convenience decorators for specific roles
def admin_required(view: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to restrict access to admin users only."""
    return role_required(["admin"])(view)


def retailer_required(view: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to restrict access to retailer users only."""
    return role_required(["retailer"])(view)


def wholesaler_required(view: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to restrict access to wholesaler users only."""
    return role_required(["wholesaler"])(view)


@auth_bp.route("/register", methods=["POST"])
def register() -> tuple[Any, int]:
    payload = request.get_json() or {}

    required_fields = {"username", "password", "email", "role"}
    if not required_fields.issubset(payload.keys()):
        return jsonify({"error": "Missing required fields"}), 400

    role = payload["role"].lower()
    if role not in VALID_ROLES:
        return jsonify({"error": "Invalid role"}), 400

    db = get_db()

    existing_username = db.execute(
        "SELECT id FROM users WHERE username = ?",
        (payload["username"],),
    ).fetchone()
    if existing_username:
        return jsonify({"error": "Username already registered"}), 400

    existing_email = db.execute(
        "SELECT id FROM users WHERE email = ?",
        (payload["email"],),
    ).fetchone()
    if existing_email:
        return jsonify({"error": "Email already registered"}), 400

    password_hash = generate_password_hash(payload["password"])
    company = payload.get("company")
    if company is not None:
        db.execute(
            "INSERT INTO users (username, password, email, role, company) VALUES (?, ?, ?, ?, ?)",
            (payload["username"], password_hash, payload["email"], role, company),
        )
    else:
        db.execute(
            "INSERT INTO users (username, password, email, role) VALUES (?, ?, ?, ?)",
            (payload["username"], password_hash, payload["email"], role),
        )
    db.commit()

    return jsonify({"message": "Registration successful"}), 201


@auth_bp.route("/create", methods=["POST"])
@login_required
def create_user() -> tuple[Any, int]:
    """Allow any authenticated user to create a new user account.

    This endpoint is intended for in-app user creation (e.g. a wholesaler
    or retailer inviting another user). It requires an active session but
    does not restrict by role.
    """
    payload = request.get_json() or {}

    required_fields = {"username", "password", "email"}
    if not required_fields.issubset(payload.keys()):
        return jsonify({"error": "Missing required fields"}), 400

    role = payload.get("role", "retailer").lower()
    if role not in VALID_ROLES:
        return jsonify({"error": "Invalid role"}), 400

    db = get_db()

    existing_username = db.execute(
        "SELECT id FROM users WHERE username = ?",
        (payload["username"],),
    ).fetchone()
    if existing_username:
        return jsonify({"error": "Username already registered"}), 400

    existing_email = db.execute(
        "SELECT id FROM users WHERE email = ?",
        (payload["email"],),
    ).fetchone()
    if existing_email:
        return jsonify({"error": "Email already registered"}), 400

    password_hash = generate_password_hash(payload["password"])
    company = payload.get("company")
    if company is not None:
        db.execute(
            "INSERT INTO users (username, password, email, role, company) VALUES (?, ?, ?, ?, ?)",
            (payload["username"], password_hash, payload["email"], role, company),
        )
    else:
        db.execute(
            "INSERT INTO users (username, password, email, role) VALUES (?, ?, ?, ?)",
            (payload["username"], password_hash, payload["email"], role),
        )
    db.commit()

    return jsonify({"message": "User created successfully"}), 201


@auth_bp.route("/login", methods=["POST"])
def login() -> tuple[Any, int]:
    payload = request.get_json() or {}

    if not {"email", "password"}.issubset(payload.keys()):
        return jsonify({"error": "Missing email/username or password"}), 400

    db = get_db()
    user = db.execute(
        "SELECT id, username, email, password, role FROM users WHERE email = ? OR username = ?",
        (payload["email"], payload["email"]),
    ).fetchone()

    if user is None or not check_password_hash(user["password"], payload["password"]):
        return jsonify({"error": "Invalid credentials"}), 401

    access_token = create_access_token(identity=user["id"])

    # FIX: Clear and set session with proper configuration
    session.clear()
    session.permanent = True  # CRITICAL: Set this BEFORE setting session data
    session["user_id"] = user["id"]
    session["role"] = user["role"]
    session.modified = True  # FIX: Explicitly mark session as modified
    
    # Enhanced debug logging
    print(f"\n=== LOGIN SUCCESSFUL ===")
    print(f"User ID: {user['id']}, Role: {user['role']}")
    print(f"Session after setting: {dict(session)}")
    print(f"Session permanent: {session.permanent}")
    print(f"Session modified: {session.modified}")
    print(f"========================\n")

    # Role-based redirect mapping - use explicit dashboard URLs
    redirect_map = {
        "admin": "/admin_dashboard.html",
        "retailer": "/retailer",
        "wholesaler": "/wholesaler/dashboard",
    }

    response_data = {
        "message": "Login successful",
        "access_token": access_token,
        "redirect": redirect_map.get(user["role"], "/"),
        "user": {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "role": user["role"],
        },
    }
    
    # FIX: Create explicit response to ensure session is saved
    response = jsonify(response_data)
    response.status_code = 200
    
    return response


@auth_bp.route("/logout", methods=["POST"])
def logout() -> tuple[Any, int]:
    session.clear()
    return jsonify({"message": "Logged out successfully"}), 200


@auth_bp.route("/check-auth", methods=["GET"])
def check_auth() -> tuple[Any, int]:
    if "user_id" not in session:
        return jsonify({"authenticated": False}), 401

    db = get_db()
    user = db.execute(
        "SELECT id, username, email, role FROM users WHERE id = ?",
        (session["user_id"],),
    ).fetchone()

    if user is None:
        session.clear()
        return jsonify({"authenticated": False}), 401

    return (
        jsonify(
            {
                "authenticated": True,
                "user": {
                    "id": user["id"],
                    "username": user["username"],
                    "email": user["email"],
                    "role": user["role"],
                },
            }
        ),
        200,
    )


@auth_bp.route("/session", methods=["GET"])
@login_required
def get_session_details() -> tuple[Any, int]:
    return check_auth()


@auth_bp.route("/protected", methods=["GET"])
@jwt_required()
def protected() -> tuple[Any, int]:
    user_id = get_jwt_identity()
    db = get_db()
    user = db.execute(
        "SELECT id, username, email, role FROM users WHERE id = ?",
        (user_id,),
    ).fetchone()

    if user is None:
        return jsonify({"error": "User not found"}), 404

    return (
        jsonify(
            {
                "message": "Access granted to protected resource",
                "user": {
                    "id": user["id"],
                    "username": user["username"],
                    "email": user["email"],
                    "role": user["role"],
                },
            }
        ),
        200,
    )
