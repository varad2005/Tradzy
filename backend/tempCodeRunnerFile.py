

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