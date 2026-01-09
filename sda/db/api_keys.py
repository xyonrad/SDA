from __future__ import annotations

"""
Managing API-keys (CLI + localhost).
"""

import hashlib
import secrets
from datetime import datetime
from typing import Iterable, List, Optional, Tuple

from sqlalchemy import select, update

from sda.auth.config import DEFAULT_STR
from sda.db.session import get_session
from sda.models.apikey import ApiKey


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _hash_key(raw: str) -> str:
    """
    One-way hash of an API key. Only the hash is stored in DB.
    """
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _now() -> datetime:
    return datetime.utcnow()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def create_api_key(user_id: int, name: str = DEFAULT_STR) -> Tuple[str, ApiKey]:
    """
    Create a single API key for a user.

    Returns:
        (plain_key, ApiKey ORM instance)
        - plain_key: the secret token (show it once, then store only hash).
    """
    session = get_session()

    plain_key = secrets.token_urlsafe(32)
    key_hash = _hash_key(plain_key)

    api = ApiKey(
        user_id=user_id,
        name=name,
        key_hash=key_hash,
        is_revoked=False,
        created_at=_now(),
    )
    session.add(api)
    session.commit()
    session.refresh(api)

    return plain_key, api


def create_api_keys(*names: str, user_ids: List[str] | None = None) -> List[Tuple[str, ApiKey]]:
    """
    Batch create API keys.

    Rules:
        - If user_ids is None or has length 1:
            all keys are created for that single user.
        - If user_ids has the same length as names:
            keys are created pairwise (names[i] for user_ids[i]).
        - Otherwise: ValueError.
    """
    if user_ids is None or len(user_ids) == 1:
        if user_ids is None:
            raise ValueError("create_api_keys requires `user_ids` when using batch mode.")
        user_id = user_ids[0]
        return [create_api_key(user_id=user_id, name=name) for name in names]

    if len(user_ids) != len(names):
        raise ValueError("Length of user_ids must be 1 or equal to the number of names.")

    out: List[Tuple[str, ApiKey]] = []
    for user_id, name in zip(user_ids, names, strict=True):
        out.append(create_api_key(user_id=user_id, name=name))
    return out


def get_api_key(key: str | None = None, user_id: int | None = None) -> Optional[ApiKey]:
    """
    Look up an API key by its *plain* value and optionally user_id.

    If `key` is None, returns None.
    """
    if key is None:
        return None

    session = get_session()
    key_hash = _hash_key(key)

    stmt = select(ApiKey).where(ApiKey.key_hash == key_hash)
    if user_id is not None:
        stmt = stmt.where(ApiKey.user_id == user_id)

    api = session.scalar(stmt)
    return api


def get_api_keys(*user_ids: str, keys: List[str] | None = None) -> List[ApiKey]:
    """
    Batch lookup.

    Modes:
        - If `keys` is provided: return all matching ApiKey rows by key values.
        - Else: return all keys belonging to the given user_ids.
    """
    session = get_session()

    if keys is not None:
        hashes = [_hash_key(k) for k in keys]
        stmt = select(ApiKey).where(ApiKey.key_hash.in_(hashes))
        return list(session.scalars(stmt).all())

    if not user_ids:
        raise ValueError("get_api_keys requires at least one user_id or `keys`.")

    stmt = select(ApiKey).where(ApiKey.user_id.in_(user_ids))
    return list(session.scalars(stmt).all())


def list_api_for_one(user_id: int) -> List[ApiKey]:
    """
    List all API keys for a single user (revoked and active).
    """
    session = get_session()
    stmt = select(ApiKey).where(ApiKey.user_id == user_id)
    return list(session.scalars(stmt).all())


def list_api_for_all() -> List[ApiKey]:
    """
    List all API keys for all users.
    """
    session = get_session()
    stmt = select(ApiKey)
    return list(session.scalars(stmt).all())


def revoke_api_key(key: str | None = None) -> bool:
    """
    Revoke a single API key by its *plain* value.

    Returns:
        True if a key was found and revoked, False otherwise.
    """
    if key is None:
        return False

    session = get_session()
    key_hash = _hash_key(key)

    api = session.scalar(select(ApiKey).where(ApiKey.key_hash == key_hash))
    if api is None or api.is_revoked:
        return False

    api.is_revoked = True
    session.commit()
    return True


def revoke_api_keys(*keys: str) -> int:
    """
    Batch revoke keys by plain value.

    Returns:
        number of keys successfully revoked.
    """
    count = 0
    for key in keys:
        if revoke_api_key(key):
            count += 1
    return count


def rotate_api_key(key: str | None = None) -> Optional[Tuple[str, ApiKey]]:
    """
    Rotate a single key: revoke old, create a new one for the same user and name.

    Returns:
        (new_plain_key, new_ApiKey) or None if original key not found.
    """
    if key is None:
        return None

    session = get_session()
    key_hash = _hash_key(key)

    api = session.scalar(select(ApiKey).where(ApiKey.key_hash == key_hash))
    if api is None or api.is_revoked:
        return None

    # Revoke old
    api.is_revoked = True
    session.commit()

    # Create new with same user_id and name
    return create_api_key(user_id=api.user_id, name=api.name)


def rotate_api_keys(*keys: str) -> List[Tuple[str, ApiKey]]:
    """
    Batch rotate keys.

    Returns:
        list of (new_plain_key, new_ApiKey); missing/invalid old keys are skipped.
    """
    out: List[Tuple[str, ApiKey]] = []
    for key in keys:
        result = rotate_api_key(key)
        if result is not None:
            out.append(result)
    return out


def valid_api_key(key: str | None = None) -> bool:
    """
    Check if a plain key is valid (exists and not revoked).
    """
    if key is None:
        return False

    api = get_api_key(key)
    if api is None:
        return False
    if api.is_revoked:
        return False

    # Optional: update last_used_at for localhost tracking
    session = get_session()
    api.last_used_at = _now()
    session.commit()

    return True


def valid_api_keys(*keys: str) -> dict[str, bool]:
    """
    Batch validity check.

    Returns:
        dict: {plain_key: is_valid}
    """
    results: dict[str, bool] = {}
    for key in keys:
        results[key] = valid_api_key(key)
    return results

