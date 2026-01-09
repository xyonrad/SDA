from __future__ import annotations

import os
from pathlib import Path

CDSE_CLIENT_URL: str = "https://stac.dataspace.copernicus.eu/v1"

CDSE_TOKEN_URL: str = (
    "https://identity.dataspace.copernicus.eu/"
    "auth/realms/CDSE/protocol/openid-connect/token"
)

CDSE_CLIENT_ID: str = "cdse-public"
CDSE_GRANT_TYPE_PASSWORD: str = "password"

class TokenData:
    TOKEN_USERNAME:     str = "username"
    TOKEN_PASSWORD:     str = "password"
    TOKEN_TOTP:         str = "totp"
    TOKEN_GRANT_TYPE:   str = "grant_type"
    TOKEN_CLIENT_ID:    str = "client_id"
    TOKEN_ACCESS:       str = "access_token"

CDSE_DATA_OUT_DIR: Path = Path(os.curdir) / "sda" / "data" / "data"

