from __future__ import annotations

"""
ORM and schema initialization.
"""

from typing import Optional

from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase

from sda.db.engine import get_engine


class Base(DeclarativeBase):
    """
    Base class for all ORM models.

    Example:
        class User(Base):
            __tablename__ = "users"

            id: Mapped[int] = mapped_column(primary_key=True)
            ...
    """
    pass


def init_db(engine: Engine) -> None:
    """
    Create all tables defined on the Base metadata using the given engine.
    """
    Base.metadata.create_all(bind=engine)


def drop_db(engine: Engine) -> None:
    """
    Drop all tables defined on the Base metadata using the given engine.
    """
    Base.metadata.drop_all(bind=engine)


def create_all(engine: Optional[Engine] = None) -> None:
    """
    Convenience wrapper: create all tables using the global engine.

    If `engine` is not provided, uses sda.db.engine.get_engine().
    """
    if engine is None:
        engine = get_engine()
    Base.metadata.create_all(bind=engine)


def drop_all(engine: Optional[Engine] = None) -> None:
    """
    Convenience wrapper: drop all tables using the global engine.

    If `engine` is not provided, uses sda.db.engine.get_engine().
    """
    if engine is None:
        engine = get_engine()
    Base.metadata.drop_all(bind=engine)


def init_code(sql: str, engine: Optional[Engine] = None) -> None:
    """
    Execute arbitrary SQL against the database in a single transaction.

    Typical usage: idempotent initialization code, seed data, custom DDL.

    The SQL string may contain multiple statements if the backend and
    driver support it.
    """
    if engine is None:
        engine = get_engine()

    # Use a transactional context; commit on success, rollback on error.
    with engine.begin() as conn:
        conn.execute(text(sql))

