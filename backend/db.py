from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Iterable

from flask import current_app, g


def get_db() -> sqlite3.Connection:
    """Return a SQLite connection stored in the Flask application context."""
    if "db" not in g:
        database_path = Path(current_app.config["DATABASE"]).expanduser()
        database_path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(database_path, detect_types=sqlite3.PARSE_DECLTYPES)
        connection.row_factory = sqlite3.Row
        g.db = connection
    return g.db  # type: ignore[return-value]


def close_db(*_: Any) -> None:
    """Close the database connection at the end of the request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def query_db(query: str, args: Iterable[Any] | None = None, one: bool = False) -> Any:
    """Utility helper to execute a query and optionally fetch a single row."""
    cursor = get_db().execute(query, args or [])
    try:
        rows = cursor.fetchall()
        return (rows[0] if rows else None) if one else rows
    finally:
        cursor.close()


def init_db() -> None:
    """Initialise the database schema using schema.sql."""
    with current_app.open_resource("schema.sql") as schema_file:
        schema_sql = schema_file.read().decode("utf-8")
        db = get_db()
        db.executescript(schema_sql)
        db.commit()


def check_and_create_tables() -> None:
    """Check if required tables exist and create them if they don't."""
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Check if users table exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
        )
        table_exists = cursor.fetchone()
        
        if not table_exists:
            current_app.logger.info("Database tables not found. Initializing database...")
            init_db()
            current_app.logger.info("Database initialized successfully!")
        else:
            current_app.logger.info("Database tables already exist.")
            
    except sqlite3.Error as e:
        current_app.logger.error(f"Database error during table check: {e}")
        # Try to initialize anyway
        try:
            init_db()
            current_app.logger.info("Database initialized after error.")
        except Exception as init_error:
            current_app.logger.error(f"Failed to initialize database: {init_error}")
            raise
    finally:
        cursor.close()
