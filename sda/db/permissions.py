from __future__ import annotations

"""
Role and permission checks (placeholder API).
"""

from typing import Any

def check_perm(user_id: str | None = None, params: dict[str, Any] | None = None):
    """
    Validate whether a user has permission for a given action.

    This repository does not implement permission storage yet, so the
    function raises NotImplementedError as a clear signal to callers.
    """
    if user_id is None and params is None:
        raise ValueError("check_perm(): user_id or params must be provided.")
    raise NotImplementedError("check_perm() is not implemented yet.")


def grant_perm(user_id: str | None = None, params: dict[str, Any] | None = None):
    """
    Grant permissions to a user or role.

    This is a placeholder hook for future RBAC integration.
    """
    if user_id is None and params is None:
        raise ValueError("grant_perm(): user_id or params must be provided.")
    raise NotImplementedError("grant_perm() is not implemented yet.")


def revoke_perm(user_id: str | None = None, params: dict[str, Any] | None = None):
    """
    Revoke permissions from a user or role.

    This is a placeholder hook for future RBAC integration.
    """
    if user_id is None and params is None:
        raise ValueError("revoke_perm(): user_id or params must be provided.")
    raise NotImplementedError("revoke_perm() is not implemented yet.")


def list_perms(role: str | None = None):
    """
    List permissions granted to a role.

    This is a placeholder hook for future RBAC integration.
    """
    if role is None:
        raise ValueError("list_perms(): role must be provided.")
    raise NotImplementedError("list_perms() is not implemented yet.")
