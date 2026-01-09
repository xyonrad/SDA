from __future__ import annotations

"""
Files connected with scenes (ZIP, JP2, TIF)
"""

from sda.auth.config import DEFAULT_STR

# TODO: add function params based on real values
# def register_asset():
#     pass

def list_assets_one(scene_id: str | None = None):
    if scene_id is None:
        raise BaseException(DEFAULT_STR) # TODO: throwing message constant for devs

def list_assets_all():
    pass

def get_asset(scene_id: str | None = None, kind: str | None = None):
    if scene_id is None or kind is None:
        raise BaseException(DEFAULT_STR) # TODO: throwing message constant for devs

def exists_asset(scene_id: str | None = None, kind: str | None = None):
    if scene_id is None or kind is None:
        raise BaseException(DEFAULT_STR) # TODO: throwing message constant for devs

def delete_asset(asset_id: str | None = None, params: dict[str, str] | None = None):
    """
    `params`:
        -- `scene_id`;
        -- `kind`;
    """
    if asset_id is None and params is None:
        raise BaseException(DEFAULT_STR) # TODO: throwing message constant for devs


