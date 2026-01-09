from __future__ import annotations

"""
Managing sessions and transactions.
"""

from contextlib import contextmanager
from contextvars import ContextVar
from typing import Generator, Optional

from sqlalchemy.orm import Session, sessionmaker

from sda.db.engine import get_engine


# Factory for creating Session objects (lazy-initialized).
_SessionFactory: Optional[sessionmaker[Session]] = None

# Context-local "current" session (per async task / thread / greenlet).
_CURRENT_SESSION: ContextVar[Optional[Session]] = ContextVar(
    "_CURRENT_SESSION",
    default=None,
)


def _get_session_factory() -> sessionmaker[Session]:
    """
    Return the global Session factory, creating it on first use.
    """
    global _SessionFactory

    if _SessionFactory is None:
        engine = get_engine()
        _SessionFactory = sessionmaker(
            bind=engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    return _SessionFactory


def get_session() -> Session:
    """
    Return the current session if one is bound to the context,
    otherwise create a new session and bind it.

    This allows zero-argument helpers like commit_session() and
    rollback_session() to operate on the context-local session.
    """
    session = _CURRENT_SESSION.get()
    if session is None:
        factory = _get_session_factory()
        session = factory()
        _CURRENT_SESSION.set(session)
    return session


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """
    Provide a transactional scope around a series of operations.

    Usage:
        with session_scope() as session:
            # use `session` here
            ...

    On successful exit:
        - commits the transaction

    On exception:
        - rolls back the transaction
        - re-raises the exception

    In all cases:
        - closes the session and clears the context-local binding
    """
    factory = _get_session_factory()
    session = factory()

    # Bind this session to the current context.
    token = _CURRENT_SESSION.set(session)

    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        try:
            session.close()
        finally:
            # Restore previous context value (if any).
            _CURRENT_SESSION.reset(token)


def commit_session() -> None:
    """
    Commit the current context-local session.

    Raises:
        RuntimeError if no session is available and cannot be created.
    """
    session = get_session()
    session.commit()


def rollback_session() -> None:
    """
    Roll back the current context-local session.

    Raises:
        RuntimeError if no session is available and cannot be created.
    """
    session = get_session()
    session.rollback()


def close_session() -> None:
    """
    Close the current context-local session and clear it from the context.

    Safe to call multiple times; does nothing if there is no active session.
    """
    session = _CURRENT_SESSION.get()
    if session is None:
        return

    try:
        session.close()
    finally:
        _CURRENT_SESSION.set(None)

