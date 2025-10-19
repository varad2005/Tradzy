from __future__ import annotations

import os
from datetime import timedelta
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
from db import close_db, check_and_create_tables

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
    
    # FIX 1: Ensure SECRET_KEY is set from environment or use a fixed fallback
    # This is CRITICAL - without a consistent SECRET_KEY, sessions will be invalidated
    if not app.config.get('SECRET_KEY'):
        app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production-12345')
    
    # FIX 2: Session configuration for development - proper settings for localhost
    # Use Flask's built-in session (client-side signed cookies) instead of filesystem
    app.config['SESSION_COOKIE_HTTPONLY'] = True   # Security: prevent XSS attacks
    app.config['SESSION_COOKIE_SECURE'] = False     # Allow HTTP for localhost
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'   # Allow same-site navigation
    app.config['SESSION_COOKIE_NAME'] = 'tradzy_session'
    app.config['SESSION_COOKIE_DOMAIN'] = None      # Use None for localhost compatibility
    app.config['SESSION_COOKIE_PATH'] = '/'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
    # REMOVED: SESSION_TYPE = 'filesystem' - use Flask's default client-side sessions
    
    # Enable debug mode
    app.config['DEBUG'] = True

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

    # Initialize database tables if they don't exist
    with app.app_context():
        try:
            check_and_create_tables()
        except Exception as e:
            app.logger.error(f"Failed to initialize database: {e}")
            # Continue anyway - let the first request handle it

    @app.before_request
    def ensure_database_exists():
        """Ensure database tables exist before handling any request."""
        # FIX 5: Enhanced debug logging for session troubleshooting
        print(f"\n=== REQUEST: {request.method} {request.path} ===")
        print(f"Session data: {dict(session)}")
        print(f"Session modified: {session.modified}")
        print(f"Cookies received: {dict(request.cookies)}")
        print(f"====================================\n")
        
        # Only check once per application instance
        if not hasattr(app, '_database_initialized'):
            try:
                check_and_create_tables()
                app._database_initialized = True
            except Exception as e:
                app.logger.error(f"Database initialization error: {e}")
                # Don't block requests, but log the error

    # FIX 6: Add after_request handler to debug response cookies
    @app.after_request
    def debug_response_cookies(response):
        """Debug response cookies being sent."""
        print(f"\n=== RESPONSE for {request.path} ===")
        print(f"Status: {response.status}")
        print(f"Set-Cookie headers: {response.headers.getlist('Set-Cookie')}")
        print(f"Session after request: {dict(session)}")
        print(f"====================================\n")
        return response

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

    @app.route("/wholesaler")
    def serve_wholesaler_portal() -> str:
        """Redirect to wholesaler login page."""
        return redirect(url_for("serve_wholesaler_login"))

    # === AUTHENTICATION-PROTECTED DASHBOARD ROUTES ===
    
    @app.route("/admin")
    @app.route("/admin_dashboard.html")
    def admin_dashboard():
        """Serve the admin dashboard page.
        
        Only accessible to users with 'admin' role.
        Redirects to login if not authenticated or wrong role.
        """
        print(f"\n=== ADMIN DASHBOARD ACCESS ATTEMPT ===")
        print(f"Session data: {dict(session)}")
        print(f"Session keys: {list(session.keys())}")
        print(f"user_id in session: {'user_id' in session}")
        print(f"role in session: {session.get('role')}")
        print(f"Cookies: {dict(request.cookies)}")
        print(f"======================================\n")
        
        if "user_id" not in session:
            print("ADMIN DASHBOARD: No user_id, redirecting to login")
            return redirect(url_for("serve_admin_login"))
        
        if session.get("role") != "admin":
            print(f"ADMIN DASHBOARD: Wrong role '{session.get('role')}', redirecting to login")
            return redirect(url_for("serve_admin_login"))
        
        print("ADMIN DASHBOARD: Access granted, rendering template")
        return render_template("admin_dashboard.html")

    @app.route("/retailer")
    def retailer_dashboard():
        """Serve the retailer dashboard page.
        
        Only accessible to users with 'retailer' role.
        Redirects to login if not authenticated or wrong role.
        """
        print(f"\n=== RETAILER DASHBOARD ACCESS ATTEMPT ===")
        print(f"Session data: {dict(session)}")
        print(f"======================================\n")
        
        if "user_id" not in session:
            return redirect(url_for("serve_login"))
        
        if session.get("role") != "retailer":
            return redirect(url_for("serve_login"))
        
        return render_template("retailer_dashboard.html")

    @app.route("/wholesaler/dashboard")
    def wholesaler_dashboard():
        """Serve the wholesaler dashboard page.
        
        Only accessible to users with 'wholesaler' role.
        Redirects to login if not authenticated or wrong role.
        """
        print(f"\n=== WHOLESALER DASHBOARD ACCESS ATTEMPT ===")
        print(f"Session data: {dict(session)}")
        print(f"======================================\n")
        
        if "user_id" not in session:
            return redirect(url_for("serve_login"))
        
        if session.get("role") != "wholesaler":
            return redirect(url_for("serve_login"))
        
        return render_template("wholesaler_dashboard.html")

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