from __future__ import annotations

"""
CDSE OAuth token acquisition helpers.
"""

import os, re, requests
from tqdm import tqdm

from .download_fast import make_session
from .cdse_consts import (
    CDSE_TOKEN_URL,
    CDSE_CLIENT_ID,
    CDSE_GRANT_TYPE_PASSWORD,
    TokenData
)

_session: requests.Session = make_session()

def get_cdse_token(
        username: str, 
        password: str, 
        totp: str | None = None, 
        timeout: int = 60
        ) -> str:
    """
    Retrieve a CDSE access token using the password grant.

    Returns:
        Access token string.
    """
    TD = TokenData

    data = {
        TD.TOKEN_USERNAME: username,
        TD.TOKEN_PASSWORD: password,
        TD.TOKEN_GRANT_TYPE: CDSE_GRANT_TYPE_PASSWORD,
        TD.TOKEN_CLIENT_ID: CDSE_CLIENT_ID,
    }

    if totp is not None:
        data[TD.TOKEN_TOTP] = totp

    r = _session.post(CDSE_TOKEN_URL, data=data, timeout=timeout)
    r.raise_for_status()
    return r.json()[TD.TOKEN_ACCESS]


def get_cdse_token_payload(
        username: str,
        password: str,
        totp: str | None = None,
        timeout: int = 60
        ) -> dict:
    """
    Retrieve the full CDSE token payload for persistence and expiry handling.
    """
    TD = TokenData

    data = {
        TD.TOKEN_USERNAME: username,
        TD.TOKEN_PASSWORD: password,
        TD.TOKEN_GRANT_TYPE: CDSE_GRANT_TYPE_PASSWORD,
        TD.TOKEN_CLIENT_ID: CDSE_CLIENT_ID,
    }

    if totp is not None:
        data[TD.TOKEN_TOTP] = totp

    r = _session.post(CDSE_TOKEN_URL, data=data, timeout=timeout)
    r.raise_for_status()
    return r.json()
