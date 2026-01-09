from __future__ import annotations

"""
Creating and managing the connection to PostgreSQL.
"""

from typing import Optional

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from sda.auth import Config

_ENGINE: Optional[Engine] = None


def init_engine(cfg: Config) -> Engine:
    """
    Initialize the global SQLAlchemy engine using the given Config.

    This function must be called once during application startup
    before any call to `get_engine()`, `ping_db()`, or `ensure_connection()`.
    """
    global _ENGINE

    if _ENGINE is not None:
        _ENGINE.dispose()

    # cfg.pg_dsn is expected to be a valid SQLAlchemy URL like:
    # postgresql+psycopg://user:pass@host:port/dbname
    _ENGINE = create_engine(cfg.pg_dsn, future=True)

    return _ENGINE


def get_engine() -> Engine:
    """
    Return the global SQLAlchemy engine.

    Raises:
        RuntimeError: if init_engine() has not been called yet.
    """
    if _ENGINE is None:
        raise RuntimeError("Database engine is not initialized. Call init_engine(Config) first.")
    return _ENGINE


def dispose_engine() -> None:
    """
    Dispose the global SQLAlchemy engine and reset it to an uninitialized state.

    Safely closes all pooled connections.
    """
    global _ENGINE
    if _ENGINE is not None:
        _ENGINE.dispose()
        _ENGINE = None


def ping_db() -> bool:
    """
    Check if the database is reachable using the current engine.

    Returns:
        True if a simple 'SELECT 1' succeeds, False otherwise.

    Raises:
        RuntimeError: if the engine has not been initialized.
    """
    engine = get_engine()

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except SQLAlchemyError:
        return False


def ensure_connection() -> None:
    """
    Ensure that the database is reachable.

    Raises:
        RuntimeError: if the engine is uninitialized or the ping fails.
    """
    # get_engine() already raises if _ENGINE is None
    if not ping_db():
        raise RuntimeError("Database connection check failed (ping_db()).")

