from __future__ import annotations

"""
Aggregation statistics (areas, clusters, metrics).
"""

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import select

from sda.db.session import get_session
from sda.models.stats import Stats


def _now() -> datetime:
    return datetime.utcnow()


def register_stats(run_id: int, stats_: dict[str, Any]) -> Stats:
    """
    Create aggregation statistics for a run.

    Fails if stats for this run already exist (depending on your logic, you may
    want to overwrite instead – then call update_stats).
    """
    if not run_id:
        raise ValueError("register_stats() requires run_id.")
    if not stats_:
        raise ValueError("register_stats() requires non-empty stats_ dict.")

    session = get_session()

    # Optional: check for existing stats and fail to avoid silent overwrite
    existing = session.get(Stats, run_id)
    if existing is not None:
        raise ValueError(f"Stats for run_id={run_id} already exist. Use update_stats().")

    stats = Stats(
        run_id=run_id,
        stats=stats_,
        created_at=_now(),
        updated_at=_now(),
    )

    session.add(stats)
    session.commit()
    session.refresh(stats)
    return stats


def get_stats(run_id: int) -> Optional[Stats]:
    """
    Get aggregation statistics for a run.
    """
    if not run_id:
        raise ValueError("get_stats() requires run_id.")

    session = get_session()
    return session.get(Stats, run_id)


def update_stats(run_id: int, stats_: dict[str, Any]) -> bool:
    """
    Update aggregation statistics for a run.

    Overwrites the stored JSON blob with the provided stats_.

    Returns:
        True if stats existed and were updated, False otherwise.
    """
    if not run_id:
        raise ValueError("update_stats() requires run_id.")
    if not stats_:
        raise ValueError("update_stats() requires non-empty stats_ dict.")

    session = get_session()
    stats = session.get(Stats, run_id)
    if stats is None:
        return False

    stats.stats = stats_
    stats.updated_at = _now()
    session.commit()
    return True


def delete_stats(run_id: int) -> bool:
    """
    Delete aggregation statistics for a run.

    Returns:
        True if stats existed and were deleted, False otherwise.
    """
    if not run_id:
        raise ValueError("delete_stats() requires run_id.")

    session = get_session()
    stats = session.get(Stats, run_id)
    if stats is None:
        return False

    session.delete(stats)
    session.commit()
    return True

