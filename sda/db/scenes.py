from __future__ import annotations

"""
Sentinel-1 / Sentinel-2 scenes registry.

This module provides **pure DB-access helpers** for working with Scene objects.
All functions are intentionally thin and explicit to keep behavior predictable
and auditable for contributors.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import select

from sda.db.session import get_session
from sda.models.scene import Scene


# ---------------------------------------------------------------------------
# Get (single)
# ---------------------------------------------------------------------------

def get_scene_by_pk(scene_pk: int) -> Optional[Scene]:
    """
    Get a scene by its internal primary key (DB id).

    Use this only when you already operate on internal IDs
    (e.g. relations, foreign keys).
    """
    if scene_pk <= 0:
        raise ValueError("get_scene_by_pk(): scene_pk must be positive")

    session = get_session()
    return session.get(Scene, scene_pk)


def get_scene_by_product_id(product_id: str) -> Optional[Scene]:
    """
    Get a scene by Sentinel product ID.

    Example:
        S2C_MSIL2A_20260106T072311_N0511_R006_T41VNE_20260106T103817
    """
    if not product_id:
        raise ValueError("get_scene_by_product_id(): product_id required")

    session = get_session()
    stmt = select(Scene).where(Scene.product_id == product_id)
    return session.scalar(stmt)


def get_scene_by_tiledate(tile: str, acquisition_time: datetime) -> Optional[Scene]:
    """
    Get a scene by tile code and acquisition datetime (UTC).

    Args:
        tile              – Sentinel tile code (e.g. 'T41VNE')
        acquisition_time  – exact acquisition datetime (UTC)
    """
    if not tile:
        raise ValueError("get_scene_by_tiledate(): tile required")
    if acquisition_time is None:
        raise ValueError("get_scene_by_tiledate(): acquisition_time required")

    session = get_session()
    stmt = (
        select(Scene)
        .where(Scene.tile == tile)
        .where(Scene.acquisition_time == acquisition_time)
    )
    return session.scalar(stmt)


# ---------------------------------------------------------------------------
# List
# ---------------------------------------------------------------------------

def list_scenes_all() -> list[Scene]:
    """
    List all scenes in the database.

    WARNING:
        Unbounded query. Use only for admin, diagnostics, or tests.
    """
    session = get_session()
    stmt = select(Scene)
    return list(session.scalars(stmt).all())


def list_scenes_filtered(params: dict[str, str]) -> list[Scene]:
    """
    List scenes using a simple filter dictionary.

    Supported keys:
        - tile
        - satellite
        - product_id
        - from   (ISO-8601 datetime, inclusive)
        - to     (ISO-8601 datetime, inclusive)

    Any unsupported key raises ValueError.
    """
    session = get_session()
    stmt = select(Scene)

    for key, value in params.items():
        if key == "tile":
            stmt = stmt.where(Scene.tile == value)
        elif key == "satellite":
            stmt = stmt.where(Scene.satellite == value)
        elif key == "product_id":
            stmt = stmt.where(Scene.product_id == value)
        elif key == "from":
            stmt = stmt.where(Scene.acquisition_time >= datetime.fromisoformat(value))
        elif key == "to":
            stmt = stmt.where(Scene.acquisition_time <= datetime.fromisoformat(value))
        else:
            raise ValueError(f"list_scenes_filtered(): unsupported filter key '{key}'")

    return list(session.scalars(stmt).all())


# ---------------------------------------------------------------------------
# Exists
# ---------------------------------------------------------------------------

def scene_exists_pk(scene_pk: int) -> bool:
    """
    Check whether a scene exists by internal primary key.
    """
    if scene_pk <= 0:
        return False
    return get_scene_by_pk(scene_pk) is not None


def scene_exists_product(product_id: str) -> bool:
    """
    Check whether a scene exists by Sentinel product ID.
    """
    if not product_id:
        return False
    return get_scene_by_product_id(product_id) is not None


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------

def delete_scene_by_pk(scene_pk: int) -> bool:
    """
    Delete a scene by internal primary key.

    Returns:
        True  – scene existed and was deleted
        False – scene not found
    """
    if scene_pk <= 0:
        raise ValueError("delete_scene_by_pk(): scene_pk must be positive")

    session = get_session()
    scene = session.get(Scene, scene_pk)
    if scene is None:
        return False

    session.delete(scene)
    session.commit()
    return True


def delete_scene_by_product(product_id: str) -> bool:
    """
    Delete a scene by Sentinel product ID.

    Returns:
        True  – scene existed and was deleted
        False – scene not found
    """
    if not product_id:
        raise ValueError("delete_scene_by_product(): product_id required")

    session = get_session()
    stmt = select(Scene).where(Scene.product_id == product_id)
    scene = session.scalar(stmt)
    if scene is None:
        return False

    session.delete(scene)
    session.commit()
    return True

