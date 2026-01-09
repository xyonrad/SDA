from __future__ import annotations

"""
Scene-linked file assets (ZIP, JP2, TIF).
"""

from datetime import datetime
from pathlib import Path
from typing import Optional

from sqlalchemy import select

from sda.db.session import get_session
from sda.models.scene_asset import SceneAsset

import hashlib


def _hash_file_or_path(path: str) -> str:
    """
    Return the SHA256 of file contents when the file exists,
    otherwise fall back to a deterministic hash of the path string.
    """
    candidate = Path(path)
    if candidate.is_file():
        return hashlib.sha256(candidate.read_bytes()).hexdigest()
    return hashlib.sha256(path.encode("utf-8")).hexdigest()


def register_asset(
    scene_id: int,
    kind: str,
    resolution_m: int,
    dtype: str,
    path: str,
    *,
    is_resampled: bool = False,
    sha256: str | None = None,
) -> SceneAsset:
    """
    Create a SceneAsset row for a file tied to a Scene.

    Args:
        scene_id     – internal Scene primary key.
        kind         – asset name (e.g. "B04_10m", "SCL_20m", "NDVI_10m").
        resolution_m – native pixel resolution in meters (10 or 20).
        dtype        – data type label (e.g. "uint16", "uint8", "float32").
        path         – filesystem or object-store path to the asset.
        is_resampled – True if the asset was resampled from its native grid.
        sha256       – optional precomputed content hash; computed from file if omitted.
    """
    if not scene_id:
        raise ValueError("register_asset(): scene_id must be a positive integer.")
    if not kind:
        raise ValueError("register_asset(): kind is required.")
    if not resolution_m:
        raise ValueError("register_asset(): resolution_m is required.")
    if not dtype:
        raise ValueError("register_asset(): dtype is required.")
    if not path:
        raise ValueError("register_asset(): path is required.")

    session = get_session()
    asset = SceneAsset(
        scene_id=scene_id,
        kind=kind,
        resolution_m=resolution_m,
        dtype=dtype,
        path=path,
        sha256=sha256 or _hash_file_or_path(path),
        is_resampled=is_resampled,
        created_at=datetime.utcnow(),
    )
    session.add(asset)
    session.commit()
    session.refresh(asset)
    return asset


def list_assets_one(scene_id: int) -> list[SceneAsset]:
    """
    Return all assets for a single Scene.
    """
    if not scene_id:
        raise ValueError("list_assets_one(): scene_id must be a positive integer.")

    session = get_session()
    stmt = select(SceneAsset).where(SceneAsset.scene_id == scene_id)
    return list(session.scalars(stmt).all())


def list_assets_all() -> list[SceneAsset]:
    """
    Return all assets across all scenes.
    """
    session = get_session()
    stmt = select(SceneAsset)
    return list(session.scalars(stmt).all())


def get_asset(scene_id: int, kind: str) -> Optional[SceneAsset]:
    """
    Return a single asset by scene_id and kind.
    """
    if not scene_id:
        raise ValueError("get_asset(): scene_id must be a positive integer.")
    if not kind:
        raise ValueError("get_asset(): kind is required.")

    session = get_session()
    stmt = select(SceneAsset).where(
        (SceneAsset.scene_id == scene_id) & (SceneAsset.kind == kind)
    )
    return session.scalar(stmt)


def exists_asset(scene_id: int, kind: str) -> bool:
    """
    Return True if an asset exists for the given scene_id and kind.
    """
    return get_asset(scene_id, kind) is not None


def delete_asset(
    asset_id: int | None = None,
    params: dict[str, str] | None = None,
) -> bool:
    """
    Delete a single asset by ID or by filter params.

    Params must include:
        - scene_id
        - kind
    """
    session = get_session()

    if asset_id is not None:
        asset = session.get(SceneAsset, asset_id)
        if asset is None:
            return False
        session.delete(asset)
        session.commit()
        return True

    if not params:
        raise ValueError("delete_asset(): asset_id or params is required.")

    scene_id = params.get("scene_id")
    kind = params.get("kind")
    if not scene_id or not kind:
        raise ValueError("delete_asset(): params must include scene_id and kind.")

    stmt = select(SceneAsset).where(
        (SceneAsset.scene_id == int(scene_id)) & (SceneAsset.kind == kind)
    )
    asset = session.scalar(stmt)
    if asset is None:
        return False
    session.delete(asset)
    session.commit()
    return True

