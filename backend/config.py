import os
from datetime import timedelta
from pathlib import Path


def _to_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR.parent / "frontend"


class Config:
    """Centralised Flask configuration for all environments."""

    SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
    SESSION_TYPE = os.getenv("SESSION_TYPE", "filesystem")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = _to_bool(os.getenv("SESSION_COOKIE_SECURE"), False)
    SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")
    PERMANENT_SESSION_LIFETIME = timedelta(
        seconds=int(os.getenv("SESSION_LIFETIME_SECONDS", "3600"))
    )

    DATABASE = os.getenv("DATABASE_URL", str(BASE_DIR / "tradzy.db"))

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        minutes=int(os.getenv("JWT_EXPIRY_MINUTES", "60"))
    )
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"

    CORS_WHITELIST = [
        origin.strip()
        for origin in os.getenv(
            "CORS_WHITELIST", "http://localhost:5000,http://127.0.0.1:5000"
        ).split(",")
        if origin.strip()
    ]
    CORS_SUPPORTS_CREDENTIALS = True
    CORS_ALLOW_HEADERS = ["Content-Type", "Authorization"]
    CORS_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]

    FRONTEND_STATIC_FOLDER = os.getenv(
        "FRONTEND_STATIC_FOLDER", str(FRONTEND_DIR / "static")
    )
    FRONTEND_TEMPLATE_FOLDER = os.getenv(
        "FRONTEND_TEMPLATE_FOLDER", str(FRONTEND_DIR / "templates")
    )

    TEMPLATES_AUTO_RELOAD = _to_bool(os.getenv("TEMPLATES_AUTO_RELOAD"), False)
    SEND_FILE_MAX_AGE_DEFAULT = int(os.getenv("SEND_FILE_MAX_AGE_DEFAULT", "600"))

    DEBUG = _to_bool(os.getenv("FLASK_DEBUG"), False)
    TESTING = _to_bool(os.getenv("FLASK_TESTING"), False)
    ENV = os.getenv("FLASK_ENV", "production")

    API_RATE_LIMIT_ENABLED = _to_bool(
        os.getenv("API_RATE_LIMIT_ENABLED"), False
    )
    API_RATE_LIMIT = os.getenv("API_RATE_LIMIT", "100/hour")


class TestingConfig(Config):
    TESTING = True
    DATABASE = os.getenv("TEST_DATABASE_URL", str(BASE_DIR / "test_tradzy.db"))
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)
    DEBUG = True


class DevelopmentConfig(Config):
    DEBUG = True
    ENV = "development"
    TEMPLATES_AUTO_RELOAD = True


class ProductionConfig(Config):
    DEBUG = False
    ENV = "production"
    SESSION_COOKIE_SECURE = True
    TEMPLATES_AUTO_RELOAD = False
