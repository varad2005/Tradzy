from __future__ import annotations

import os
from typing import Any, Dict

from dotenv import load_dotenv
from flask import (
    Flask,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_talisman import Talisman

from config import Config
from db import close_db

load_dotenv()

SECURE_CSP: Dict[str, Any] = {
    "default-src": ["'self'"],
    "script-src": ["'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net", "https://cdnjs.cloudflare.com"],
    "style-src": ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com", "https://cdn.jsdelivr.net"],
    "font-src": ["'self'", "https://fonts.gstatic.com", "https://cdn.jsdelivr.net"],
    "img-src": ["'self'", "data:", "https://via.placeholder.com"],
    "connect-src": ["'self'", "http://localhost:5000", "http://127.0.0.1:5000"],
}


def create_app(config_class: type[Config] = Config) -> Flask:
    app = Flask(
        __name__,
        static_url_path="/static",
        static_folder=config_class.FRONTEND_STATIC_FOLDER,
        template_folder=config_class.FRONTEND_TEMPLATE_FOLDER,
    )

    app.config.from_object(config_class)
    app.config.setdefault("SESSION_PERMANENT", False)

    # Configure CORS for API routes only
    CORS(
        app,
        resources={r"/api/*": {
            "origins": app.config["CORS_WHITELIST"],
            "supports_credentials": app.config["CORS_SUPPORTS_CREDENTIALS"],
            "allow_headers": app.config["CORS_ALLOW_HEADERS"],
            "methods": app.config["CORS_METHODS"],
        }},
    )

    JWTManager(app)

    # Apply basic security headers when running in production
    force_https = app.config.get("SESSION_COOKIE_SECURE", False)
    Talisman(
        app,
        content_security_policy=SECURE_CSP if not app.config.get("DEBUG") else None,
        force_https=force_https,
        strict_transport_security=force_https,
    )

    from routes.auth import auth_bp
    from routes.products import products_bp
    from routes.orders import orders_bp
    from routes.cart import cart_bp
    from routes.wishlist import wishlist_bp
    from routes.admin import admin_bp
    from routes.wholesaler import wholesaler_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(wishlist_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(wholesaler_bp)

    @app.teardown_appcontext
    def teardown_db(exception: BaseException | None) -> None:  # pragma: no cover - teardown
        close_db(exception)

    @app.context_processor
    def inject_globals() -> Dict[str, Any]:
        return {
            "api_base_url": os.getenv("PUBLIC_API_BASE_URL", "/api"),
            "app_name": "TRADZY",
        }

    @app.route("/")
    def serve_index() -> str:
        return render_template("index.html")

    @app.route("/login")
    def serve_login() -> str:
        return render_template("login.html")

    @app.route("/contact")
    def serve_contact() -> str:
        """Serve the contact page."""
        return render_template("contact.html")

    @app.route("/products")
    def serve_products() -> str:
        """Serve the products page."""
        return render_template("products.html")

    @app.route("/admin.html")
    def serve_admin_login() -> str:
        """Serve the admin login page."""
        return render_template("admin.html")

    @app.route("/retailer.html")
    def serve_retailer_login() -> str:
        """Serve the retailer login page."""
        return render_template("retailer.html")

    @app.route("/wholesaler.html")
    def serve_wholesaler_login() -> str:
        """Serve the wholesaler login page."""
        return render_template("wholesaler.html")

    dashboard_templates = {
        "admin": "admin.html",
        "retailer": "retailer.html",
        "wholesaler": "wholesaler.html",
    }

    @app.route("/dashboard/<role>")
    def serve_dashboard(role: str):
        template = dashboard_templates.get(role)
        if template is None:
            return redirect(url_for("serve_login"))

        if "user_id" not in session:
            return redirect(url_for("serve_login"))

        if session.get("role") != role:
            return redirect(url_for("serve_login"))

        return render_template(template)

    @app.route("/admin")
    def admin_alias():
        return redirect(url_for("serve_dashboard", role="admin"))

    @app.route("/retailer")
    def retailer_alias():
        return redirect(url_for("serve_dashboard", role="retailer"))

    @app.route("/wholesaler")
    def wholesaler_alias():
        return redirect(url_for("serve_dashboard", role="wholesaler"))

    @app.route("/health")
    def health_check() -> Dict[str, str]:
        return {"status": "ok"}

    @app.route("/api/health")
    def api_health() -> Dict[str, str]:
        return {"status": "ok"}

    @app.errorhandler(401)
    def handle_unauthorised(_: Any):
        """Handle 401 Unauthorized errors."""
        if request.path.startswith("/api/"):
            return jsonify({"error": "Authentication required"}), 401
        return redirect(url_for("serve_login"))

    @app.errorhandler(403)
    def handle_forbidden(_: Any):
        """Handle 403 Forbidden errors."""
        if request.path.startswith("/api/"):
            return jsonify({"error": "Permission denied"}), 403
        try:
            return render_template("403.html"), 403
        except Exception:
            return "<h1>403 - Access Forbidden</h1><p>You don't have permission to access this resource.</p>", 403

    @app.errorhandler(404)
    def handle_not_found(_: Any):
        """Handle 404 Not Found errors."""
        if request.path.startswith("/api/"):
            return jsonify({"error": "Not Found"}), 404
        try:
            return render_template("404.html"), 404
        except Exception:
            return "<h1>404 - Page Not Found</h1><p>The page you're looking for doesn't exist.</p>", 404

    @app.errorhandler(500)
    def handle_internal_error(_: Any):
        """Handle 500 Internal Server Error."""
        if request.path.startswith("/api/"):
            return jsonify({"error": "Internal server error"}), 500
        try:
            return render_template("500.html"), 500
        except Exception:
            return "<h1>500 - Internal Server Error</h1><p>Something went wrong. Please try again later.</p>", 500

    @app.errorhandler(Exception)
    def handle_exception(error: Exception):
        """Handle uncaught exceptions."""
        # In debug mode, let Flask's debugger handle it
        if app.config.get("DEBUG"):
            raise error
        
        # Log the error
        app.logger.error(f"Unhandled exception: {error}", exc_info=True)
        
        # Return appropriate response
        if request.path.startswith("/api/"):
            return jsonify({"error": "Internal server error"}), 500
        try:
            return render_template("500.html"), 500
        except Exception:
            return "<h1>500 - Internal Server Error</h1><p>Something went wrong. Please try again later.</p>", 500

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "5000")),
        debug=app.config.get("DEBUG", False),
    )