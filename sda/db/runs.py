from __future__ import annotations

"""
Pipeline launch.
Pipeline — series of connected processes where the output
of one stage is the input for the next.
"""

from datetime import datetime
from typing import Optional, Iterable

from sqlalchemy import select

from sda.db.session import get_session
# TODO: implement Run class
from sda.models.run import Run


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now() -> datetime:
    return datetime.utcnow()


# ---------------------------------------------------------------------------
# CRUD-like API
# ---------------------------------------------------------------------------

def create_run(
    user_id: str,
    profile: str,
    params: dict[str, str] | None = None,
) -> Run:
    """
    Create a new pipeline run.

    Initial status is 'pending'. `params` is stored as JSON.
    """
    if not user_id:
        raise ValueError("create_run() requires non-empty user_id.")
    if not profile:
        raise ValueError("create_run() requires non-empty profile.")

    session = get_session()

    run = Run(
        user_id=user_id,
        profile=profile,
        params=params or {},
        status="pending",
        started_at=_now(),
    )

    session.add(run)
    session.commit()
    session.refresh(run)
    return run


def get_run(run_id: int) -> Optional[Run]:
    """
    Get a single run by ID.
    """
    session = get_session()
    return session.get(Run, run_id)


def list_runs_one(user_id: str, status: str | int | None = None) -> list[Run]:
    """
    List runs for a single user, optionally filtered by status.

    `status`:
        - if str: filter by Run.status == status
        - if int: you can map it to string codes in your application logic
    """
    if not user_id:
        raise ValueError("list_runs_one() requires non-empty user_id.")

    session = get_session()
    stmt = select(Run).where(Run.user_id == user_id)

    if isinstance(status, str):
        stmt = stmt.where(Run.status == status)
    elif isinstance(status, int):
        # Example mapping; you can change this to your own convention
        mapping = {
            0: "pending",
            1: "running",
            2: "finished",
            3: "failed",
            4: "killed",
        }
        status_str = mapping.get(status)
        if status_str is None:
            raise ValueError(f"Unknown numeric status: {status}")
        stmt = stmt.where(Run.status == status_str)

    return list(session.scalars(stmt).all())


def list_runs_all() -> list[Run]:
    """
    List all runs (for all users).
    """
    session = get_session()
    stmt = select(Run)
    return list(session.scalars(stmt).all())


def update_run_status(run_id: int, status: str = "kill") -> bool:
    """
    Update status of a run.

    Returns:
        True if the run exists and was updated, False otherwise.
    """
    session = get_session()
    run = session.get(Run, run_id)
    if run is None:
        return False

    run.status = status
    session.commit()
    return True


def finish_run(
    run_id: int,
    success: bool,
    error: str | None = None,
) -> bool:
    """
    Mark a run as finished.

    Arguments:
        run_id  – ID of the run.
        success – True if pipeline finished successfully, False otherwise.
        error   – Optional error message if failed.

    Returns:
        True if run found and updated, False otherwise.
    """
    session = get_session()
    run = session.get(Run, run_id)
    if run is None:
        return False

    run.success = success
    run.finished_at = _now()
    run.status = "finished" if success else "failed"
    if error is not None:
        run.error = error

    session.commit()
    return True


def delete_run(run_id: int) -> bool:
    """
    Delete a single run by ID.

    Returns:
        True if run existed and was deleted, False otherwise.
    """
    session = get_session()
    run = session.get(Run, run_id)
    if run is None:
        return False

    session.delete(run)
    session.commit()
    return True


def delete_runs(*run_ids: int) -> int:
    """
    Delete multiple runs by ID.

    Returns:
        number of runs actually deleted.
    """
    if not run_ids:
        raise ValueError("delete_runs() requires at least one run_id.")

    deleted = 0
    for run_id in run_ids:
        if delete_run(run_id):
            deleted += 1
    return deleted


def delete_run_all() -> int:
    """
    Delete all runs.

    Returns:
        number of rows deleted (best-effort approximation).
    """
    session = get_session()
    runs = session.scalars(select(Run)).all()
    count = len(runs)

    for run in runs:
        session.delete(run)
    session.commit()

    return count

