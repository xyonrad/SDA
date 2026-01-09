from __future__ import annotations

"""
Change-detection (ΔNDVI, ΔNBR, masks)
"""

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import select

from sda.db.session import get_session
from sda.models.change import Change


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now() -> datetime:
    return datetime.utcnow()


# ---------------------------------------------------------------------------
# Registration (optional, but useful)
# ---------------------------------------------------------------------------

def register_change(
    scene_before_id: int,
    scene_after_id: int,
    index_name: str,
    method: str,
    thresholds: dict[str, Any],
    path: str,
    sha256: str,
    ) -> Change:
    """
    Register a single change-detection artifact.

    Args:
        run_id   – pipeline run identifier (foreign key to Run).
        kind     – change type, e.g. "delta_ndvi", "delta_nbr", "mask".
        path     – filesystem / object-storage path of the artifact.
        meta_data – optional JSON metadata (thresholds, parameters, CRS, etc.).
    """
    if not scene_before_id or not scene_after_id:
        raise ValueError("register_change(): scene ids required")
    if not index_name or not method or not path or not sha256:
        raise ValueError("register_change(): missing required fields")

    session = get_session()

    change = Change(
        scene_before_id=scene_before_id,
        scene_after_id=scene_after_id,
        index_name=index_name,
        method=method,
        thresholds=thresholds,
        path=path,
        sha256=sha256,
        created_at=_now(),
    )

    session.add(change)
    session.commit()
    session.refresh(change)
    return change


# ---------------------------------------------------------------------------
# Get / list
# ---------------------------------------------------------------------------

def get_change(change_id: int) -> Optional[Change]:
    """
    Get a single change artifact by run and kind.

    Returns:
        Change or None if not found.
    """
    session = get_session()
    return session.get(Change, change_id)

def list_changes_for_scene(scene_id: int) -> list[Change]:
    """
    TODO: Comment the function functionality
    """
    session = get_session()
    stmt = select(Change).where(
        (Change.scene_before_id == scene_id)
        | (Change.scene_after_id == scene_id)
    )
    return list(session.scalars(stmt).all())

def delete_change(change_id: int) -> bool:
    """
    TODO: Comment the function functionality
    """
    session = get_session()
    obj = session.get(Change, change_id)
    if obj is None:
        return False
    session.delete(obj)
    session.commit()
    return True
