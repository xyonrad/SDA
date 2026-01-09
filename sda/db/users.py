from __future__ import annotations

from typing import Optional, Iterable

from sqlalchemy import select
from sda.db.session import get_session
from sda.auth.config import DEFAULT_STR
from sda.models.user import User

def create_user(
        login: str,
        pass_hash: str,
        token: str = DEFAULT_STR,
        role: str = DEFAULT_STR,
) -> User:
    session = get_session()

    user = User(
        login=login,
        pass_hash=pass_hash,
        token=token,
        role=role,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def get_user_by_login(login: str) -> Optional[User]:
    session = get_session()
    stmt = select(User).where(User.login == login)
    return session.scalar(stmt)


def get_user_by_id(user_id: int) -> Optional[User]:
    session = get_session()
    return session.get(User, user_id)


def list_users() -> Iterable[User]:
    session = get_session()
    stmt = select(User)
    return session.scalars(stmt).all()


def update_user_pass(user_id: int, pass_hash: str) -> bool:
    """
    Update user password hash.
    Returns True, if user found and saved.
    """
    session = get_session()
    user = session.get(User, user_id)
    if user is None:
        return False

    user.pass_hash = pass_hash
    session.commit()
    return True


def update_user_role(user_id: int, role: str) -> bool:
    """
    User role updater.
    Returns True, if user found and saved.
    """
    session = get_session()
    user = session.get(User, user_id)
    if user is None:
        return False

    user.role = role
    session.commit()
    return True


def delete_user(user_id: int) -> bool:
    """
    Delete user by id.
    Returns True, if user already existed and was successfuly deleted.
    """
    session = get_session()
    user = session.get(User, user_id)
    if user is None:
        return False

    session.delete(user)
    session.commit()
    return True


import hashlib
def _hash_pass(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def verify_credentials(login: str, pass_plain: str) -> Optional[User]:
    """
    Return login and password if all is correctly, else None
    """
    user = get_user_by_login(login)
    if user is None:
        return None

    if _hash_pass(pass_plain) != user.pass_hash:
        return None

    return user

def exists_user(login: str | None = None, user_id: int | None = None) -> bool:
    if login is None and user_id is None:
        raise ValueError("exists_user() requires login or user_id.")

    if login is not None:
        return get_user_by_login(login) is not None

    if user_id is not None:
        return get_user_by_id(user_id) is not None

    return False

