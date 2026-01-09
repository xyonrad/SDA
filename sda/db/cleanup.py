from __future__ import annotations

"""
Trash and old data cleanup.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import select, text

from sda.auth.config import DEFAULT_STR
from sda.db.engine import get_engine
from sda.db.session import get_session
from sda.models.run import Run
from sda.models.index_artifact import IndexArtifact
from sda.models.index_feature import IndexFeature
from sda.models.change import Change


def cleanup(params: dict[str, Any]) -> Dict[str, int]:
    """
    High-level cleanup dispatcher.

    Expected params keys (example):
        {
            "orphan_assets": True | False,
            "failed_runs":   True | False,
            "old_runs_days": int | None,
        }

    Returns:
        dict with counters per cleanup category, e.g.:
        {
            "orphan_assets": 10,
            "failed_runs":   3,
            "old_runs":      5,
        }
    """
    if not params:
        raise ValueError(DEFAULT_STR)

    results: Dict[str, int] = {}

    if params.get("failed_runs"):
        results["failed_runs"] = _cleanup_failed_runs()

    old_runs_days = params.get("old_runs_days")
    if isinstance(old_runs_days, int) and old_runs_days > 0:
        results["old_runs"] = _cleanup_old_runs(days=old_runs_days)

    return results


def _cleanup_failed_runs() -> int:
    """
    Delete runs with status 'failed' or 'killed'.

    Returns:
        number of runs deleted.
    """
    session = get_session()

    q = session.query(Run).filter(Run.status.in_(["failed", "killed"]))
    runs = q.all()
    count = len(runs)

    for run in runs:
        session.delete(run)

    session.commit()
    return count


def _cleanup_old_runs(days: int) -> int:
    """
    Delete old runs (and implicitly any dependent data if cascades are configured).

    Deletes runs whose finished_at is older than `days`. If finished_at is null,
    status must be terminal to be deleted.
    """
    session = get_session()
    cutoff = datetime.utcnow() - timedelta(days=days)

    q = (
        session.query(Run)
        .filter(Run.finished_at.isnot(None))
        .filter(Run.finished_at < cutoff)
    )
    runs = q.all()
    count = len(runs)

    for run in runs:
        session.delete(run)

    session.commit()
    return count


def vacuum_tables(
    table_names: List[str] | None = None,
    *,
    full: bool = False,
    analyze: bool = True,
) -> None:
    """
    Run PostgreSQL VACUUM on selected tables (or on the whole DB if table_names is None).

    Args:
        table_names – list of table names; if None, vacuum all tables.
        full        – use VACUUM FULL (heavier, locks tables).
        analyze     – include ANALYZE to update planner statistics.

    Notes:
        - Requires PostgreSQL.
        - Executed in AUTOCOMMIT mode because VACUUM cannot run inside a transaction.
    """
    engine = get_engine()

    options: List[str] = []
    if full:
        options.append("FULL")
    if analyze:
        options.append("ANALYZE")

    opt_str = ""
    if options:
        opt_str = " (" + ", ".join(options) + ")"

    if table_names:
        target = ", ".join(table_names)
    else:
        target = ""  # vacuum entire DB

    sql = f"VACUUM{opt_str} {target};"

    # VACUUM must run outside a transaction
    with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
        conn.execute(text(sql))

