from __future__ import annotations

"""
Permissions and roles managing
"""

from sda.auth.config import DEFAULT_STR
from typing import Any

def check_perm(user_id: str | None = None, params: dict[str, Any] | None = None):
    if user_id is None and params is None:
        raise BaseException(DEFAULT_STR) # TODO: throwing message constant for devs

def grant_perm(user_id: str | None = None, params: dict[str, Any] | None = None):
    if user_id is None and params is None:
        raise BaseException(DEFAULT_STR) # TODO: throwing message constant for devs

def revoke_perm(user_id: str | None = None, params: dict[str, Any] | None = None):
    if user_id is None and params is None:
        raise BaseException(DEFAULT_STR) # TODO: throwing message constant for devs

def list_perms(role: str | None = None):
    if role is None:
        raise BaseException(DEFAULT_STR) # TODO: throwing message constant for devs

