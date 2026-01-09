from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

import requests
from sqlalchemy import select

from sda.db.session import get_session
from sda.io.cdse_consts import CDSE_CLIENT_URL
from sda.io.get_token import get_cdse_token_payload
from sda.models.cdse_token import CDSEToken


def _now() -> datetime:
    return datetime.utcnow()


def _compute_expires_at(issued_at: datetime, expires_in_s: int | None) -> datetime | None:
    if expires_in_s is None:
        return None
    return issued_at + timedelta(seconds=int(expires_in_s))


def _token_is_valid(access_token: str, timeout: int = 20) -> bool:
    """
    Check token validity by pinging the CDSE STAC endpoint.

    Returns:
        True if the token is accepted, False if unauthorized or request fails.
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        response = requests.get(CDSE_CLIENT_URL, headers=headers, timeout=timeout)
    except requests.RequestException:
        return False
    return response.status_code < 400


def create_token(login: str, password: str, totp: str | None = None) -> CDSEToken:
    """
    Request a new CDSE token and persist it in the database.
    """
    if not login:
        raise ValueError("create_token(): login is required.")
    if not password:
        raise ValueError("create_token(): password is required.")

    payload = get_cdse_token_payload(login, password, totp=totp)

    issued_at = _now()
    expires_in_s = payload.get("expires_in")
    expires_at = _compute_expires_at(issued_at, expires_in_s)

    token = CDSEToken(
        login=login,
        password=password,
        access_token=payload.get("access_token", ""),
        refresh_token=payload.get("refresh_token"),
        token_type=payload.get("token_type"),
        scope=payload.get("scope"),
        expires_in_s=expires_in_s,
        issued_at=issued_at,
        expires_at=expires_at,
        is_revoked=False,
        created_at=issued_at,
        updated_at=issued_at,
    )

    session = get_session()
    session.add(token)
    session.commit()
    session.refresh(token)
    return token


def get_token_by_id(token_id: int) -> Optional[CDSEToken]:
    """
    Return a token row by primary key.
    """
    session = get_session()
    return session.get(CDSEToken, token_id)


def list_tokens(login: str | None = None) -> list[CDSEToken]:
    """
    List tokens, optionally filtered by login.
    """
    session = get_session()
    stmt = select(CDSEToken)
    if login:
        stmt = stmt.where(CDSEToken.login == login)
    return list(session.scalars(stmt).all())


def get_latest_token(login: str) -> Optional[CDSEToken]:
    """
    Return the most recently issued token for a login.
    """
    if not login:
        raise ValueError("get_latest_token(): login is required.")

    session = get_session()
    stmt = (
        select(CDSEToken)
        .where(CDSEToken.login == login)
        .order_by(CDSEToken.issued_at.desc())
    )
    return session.scalar(stmt)


def token_is_expired(token: CDSEToken) -> bool:
    """
    Return True if the token is expired or marked revoked.
    """
    if token.is_revoked:
        return True
    if token.expires_at is None:
        return False
    return _now() >= token.expires_at


def get_or_create_valid_token(
    login: str,
    password: str,
    *,
    totp: str | None = None,
    validate_with_ping: bool = True,
) -> CDSEToken:
    """
    Return a valid token for a login, creating one if required.

    Validation order:
        1) If the latest token is expired or revoked, create a new token.
        2) If ping validation is enabled and the token is rejected, create a new token.
    """
    token = get_latest_token(login)
    if token is None:
        return create_token(login, password, totp=totp)

    if token_is_expired(token):
        return create_token(login, password, totp=totp)

    if validate_with_ping and not _token_is_valid(token.access_token):
        return create_token(login, password, totp=totp)

    return token


def revoke_token(token_id: int) -> bool:
    """
    Mark a token as revoked.
    """
    session = get_session()
    token = session.get(CDSEToken, token_id)
    if token is None:
        return False
    token.is_revoked = True
    token.updated_at = _now()
    session.commit()
    return True


def revoke_tokens_for_login(login: str) -> int:
    """
    Revoke all tokens for a given login.
    """
    if not login:
        raise ValueError("revoke_tokens_for_login(): login is required.")

    session = get_session()
    stmt = select(CDSEToken).where(CDSEToken.login == login)
    tokens = list(session.scalars(stmt).all())
    for token in tokens:
        token.is_revoked = True
        token.updated_at = _now()
    session.commit()
    return len(tokens)


def delete_token(token_id: int) -> bool:
    """
    Delete a token row by primary key.
    """
    session = get_session()
    token = session.get(CDSEToken, token_id)
    if token is None:
        return False
    session.delete(token)
    session.commit()
    return True


def delete_tokens_for_login(login: str) -> int:
    """
    Delete all tokens for a given login.
    """
    if not login:
        raise ValueError("delete_tokens_for_login(): login is required.")

    session = get_session()
    stmt = select(CDSEToken).where(CDSEToken.login == login)
    tokens = list(session.scalars(stmt).all())
    for token in tokens:
        session.delete(token)
    session.commit()
    return len(tokens)


def purge_expired_tokens() -> int:
    """
    Delete tokens that are expired or explicitly revoked.
    """
    session = get_session()
    stmt = select(CDSEToken)
    tokens = list(session.scalars(stmt).all())
    to_delete = [
        token for token in tokens
        if token.is_revoked or (token.expires_at is not None and _now() >= token.expires_at)
    ]
    for token in to_delete:
        session.delete(token)
    session.commit()
    return len(to_delete)
