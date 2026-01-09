from __future__ import annotations

"""
Diagnostics.
"""

from typing import Any, Dict, List

from sqlalchemy import MetaData, Table, func, select, inspect
from sqlalchemy.exc import SQLAlchemyError

from sda.auth.config import DEFAULT_STR
from sda.db.engine import get_engine, ping_db


def db_healthcheck() -> bool:
    """
    Lightweight DB healthcheck.

    Returns:
        True  – DB is reachable and responds to a trivial query.
        False – connection or query failed.
    """
    return ping_db()


def count_rows(table_name: str) -> int:
    """
    Count rows in a given table.

    Args:
        table_name – name of the table as it exists in the DB.

    Returns:
        Row count (int).

    Raises:
        ValueError – if table_name is empty or table does not exist.
    """
    if not table_name:
        raise ValueError(DEFAULT_STR)

    engine = get_engine()
    inspector = inspect(engine)

    if table_name not in inspector.get_table_names():
        raise ValueError(f"Unknown table: {table_name!r}")

    metadata = MetaData()
    table = Table(table_name, metadata, autoload_with=engine)

    with engine.connect() as conn:
        stmt = select(func.count()).select_from(table)
        return conn.execute(stmt).scalar_one()


def db_info() -> Dict[str, Any]:
    """
    Basic DB diagnostics information.

    Returns:
        {
            "ok": bool,
            "dialect": str,
            "driver": str,
            "url": str,           # password redacted
            "tables": list[str],
        }
    """
    engine = get_engine()
    inspector = inspect(engine)

    # redact password from URL
    safe_url = engine.url.set(password="***")

    info: Dict[str, Any] = {
        "ok": False,
        "dialect": engine.dialect.name,
        "driver": engine.dialect.driver,
        "url": str(safe_url),
        "tables": inspector.get_table_names(),
    }

    try:
        info["ok"] = ping_db()
    except SQLAlchemyError:
        info["ok"] = False

    return info

