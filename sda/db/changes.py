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
        scene_before_id – Scene id for the "before" timestamp.
        scene_after_id  – Scene id for the "after" timestamp.
        index_name      – index name the change is computed from (e.g. "NDVI").
        method          – computation method (e.g. "diff", "zscore", "seasonal").
        thresholds      – JSON-ready threshold settings for masks or alerts.
        path            – filesystem or object-storage path of the artifact.
        sha256          – content hash of the artifact for integrity checks.
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
    Get a single change artifact by its primary key.

    Returns:
        Change or None if not found.
    """
    session = get_session()
    return session.get(Change, change_id)

def list_changes_for_scene(scene_id: int) -> list[Change]:
    """
    List all change artifacts where the given scene is either before or after.
    """
    session = get_session()
    stmt = select(Change).where(
        (Change.scene_before_id == scene_id)
        | (Change.scene_after_id == scene_id)
    )
    return list(session.scalars(stmt).all())

def delete_change(change_id: int) -> bool:
    """
    Delete a change artifact by its primary key.

    Returns:
        True if the row existed and was deleted, False otherwise.
    """
    session = get_session()
    obj = session.get(Change, change_id)
    if obj is None:
        return False
    session.delete(obj)
    session.commit()
    return True
