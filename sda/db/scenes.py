from __future__ import annotations

"""
Sentinel-1 / Sentinel-2 scenes registry.

This module provides **pure DB-access helpers** for working with Scene objects.
All functions are intentionally thin and explicit to keep behavior predictable
and auditable for contributors.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import select

from sda.db.session import get_session
from sda.models.scene import Scene
from sda.models.scene_asset import SceneAsset
from sda.db.assets import register_asset, list_assets_one, get_asset, delete_asset


def create_scene(
    product_id: str,
    satellite: str,
    tile: str,
    acquisition_time: datetime,
    crs: str,
    transform: list[float],
    width: int,
    height: int,
    lon_min: float,
    lat_min: float,
    lon_max: float,
    lat_max: float,
    *,
    processing_level: str = "L2A",
    source_zip: str = "",
) -> Scene:
    """
    Create and persist a Scene row for one satellite acquisition.

    Args:
        product_id       – Sentinel product identifier.
        satellite        – satellite name (e.g. "S2A", "S2B", "S2C").
        tile             – tile code (e.g. "T41VNE").
        acquisition_time – acquisition timestamp (UTC).
        crs              – CRS string (e.g. "EPSG:32641").
        transform        – affine transform coefficients (length 9).
        width            – raster width in pixels.
        height           – raster height in pixels.
        lon_min          – western longitude.
        lat_min          – southern latitude.
        lon_max          – eastern longitude.
        lat_max          – northern latitude.
        processing_level – processing level label (default "L2A").
        source_zip       – source archive path (optional).
    """
    if not product_id:
        raise ValueError("create_scene(): product_id is required.")
    if not satellite:
        raise ValueError("create_scene(): satellite is required.")
    if not tile:
        raise ValueError("create_scene(): tile is required.")
    if acquisition_time is None:
        raise ValueError("create_scene(): acquisition_time is required.")
    if not crs:
        raise ValueError("create_scene(): crs is required.")
    if not transform or len(transform) != 9:
        raise ValueError("create_scene(): transform must have length 9.")
    if width <= 0 or height <= 0:
        raise ValueError("create_scene(): width and height must be positive.")

    session = get_session()
    scene = Scene(
        product_id=product_id,
        satellite=satellite,
        tile=tile,
        acquisition_time=acquisition_time,
        crs=crs,
        transform=transform,
        width=width,
        height=height,
        lon_min=lon_min,
        lat_min=lat_min,
        lon_max=lon_max,
        lat_max=lat_max,
        processing_level=processing_level,
        source_zip=source_zip,
        created_at=datetime.utcnow(),
    )
    session.add(scene)
    session.commit()
    session.refresh(scene)
    return scene


def create_scene_asset(
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
    Create and persist a SceneAsset row using the assets helper.
    """
    return register_asset(
        scene_id=scene_id,
        kind=kind,
        resolution_m=resolution_m,
        dtype=dtype,
        path=path,
        is_resampled=is_resampled,
        sha256=sha256,
    )


def list_scene_assets(scene_id: int) -> list[SceneAsset]:
    """
    List all assets for a scene by internal scene id.
    """
    return list_assets_one(scene_id)


def list_scene_assets_by_product_id(product_id: str) -> list[SceneAsset]:
    """
    List all assets for a scene by Sentinel product_id.
    """
    scene = get_scene_by_product_id(product_id)
    if scene is None:
        return []
    return list_assets_one(scene.id)


def get_scene_with_assets(scene_id: int) -> tuple[Scene | None, list[SceneAsset]]:
    """
    Return a scene and its assets in one call.
    """
    scene = get_scene_by_pk(scene_id)
    if scene is None:
        return None, []
    return scene, list_assets_one(scene_id)


def get_scene_asset(scene_id: int, kind: str) -> Optional[SceneAsset]:
    """
    Return a single asset for a scene by kind.
    """
    return get_asset(scene_id, kind)


def delete_scene_with_assets(scene_id: int) -> bool:
    """
    Delete a scene and all attached assets.

    Returns:
        True if the scene existed and was deleted, False otherwise.
    """
    assets = list_assets_one(scene_id)
    for asset in assets:
        delete_asset(asset.id)
    return delete_scene_by_pk(scene_id)

# ---------------------------------------------------------------------------
# Get (single)
# ---------------------------------------------------------------------------

def get_scene_by_pk(scene_pk: int) -> Optional[Scene]:
    """
    Get a scene by its internal primary key (DB id).

    Use this only when you already operate on internal IDs
    (e.g. relations, foreign keys).
    """
    if scene_pk <= 0:
        raise ValueError("get_scene_by_pk(): scene_pk must be positive")

    session = get_session()
    return session.get(Scene, scene_pk)


def get_scene_by_product_id(product_id: str) -> Optional[Scene]:
    """
    Get a scene by Sentinel product ID.

    Example:
        S2C_MSIL2A_20260106T072311_N0511_R006_T41VNE_20260106T103817
    """
    if not product_id:
        raise ValueError("get_scene_by_product_id(): product_id required")

    session = get_session()
    stmt = select(Scene).where(Scene.product_id == product_id)
    return session.scalar(stmt)


def get_scene_by_tiledate(tile: str, acquisition_time: datetime) -> Optional[Scene]:
    """
    Get a scene by tile code and acquisition datetime (UTC).

    Args:
        tile              – Sentinel tile code (e.g. 'T41VNE')
        acquisition_time  – exact acquisition datetime (UTC)
    """
    if not tile:
        raise ValueError("get_scene_by_tiledate(): tile required")
    if acquisition_time is None:
        raise ValueError("get_scene_by_tiledate(): acquisition_time required")

    session = get_session()
    stmt = (
        select(Scene)
        .where(Scene.tile == tile)
        .where(Scene.acquisition_time == acquisition_time)
    )
    return session.scalar(stmt)


# ---------------------------------------------------------------------------
# List
# ---------------------------------------------------------------------------

def list_scenes_all() -> list[Scene]:
    """
    List all scenes in the database.

    WARNING:
        Unbounded query. Use only for admin, diagnostics, or tests.
    """
    session = get_session()
    stmt = select(Scene)
    return list(session.scalars(stmt).all())


def list_scenes_filtered(params: dict[str, str]) -> list[Scene]:
    """
    List scenes using a simple filter dictionary.

    Supported keys:
        - tile
        - satellite
        - product_id
        - from   (ISO-8601 datetime, inclusive)
        - to     (ISO-8601 datetime, inclusive)

    Any unsupported key raises ValueError.
    """
    session = get_session()
    stmt = select(Scene)

    for key, value in params.items():
        if key == "tile":
            stmt = stmt.where(Scene.tile == value)
        elif key == "satellite":
            stmt = stmt.where(Scene.satellite == value)
        elif key == "product_id":
            stmt = stmt.where(Scene.product_id == value)
        elif key == "from":
            stmt = stmt.where(Scene.acquisition_time >= datetime.fromisoformat(value))
        elif key == "to":
            stmt = stmt.where(Scene.acquisition_time <= datetime.fromisoformat(value))
        else:
            raise ValueError(f"list_scenes_filtered(): unsupported filter key '{key}'")

    return list(session.scalars(stmt).all())


# ---------------------------------------------------------------------------
# Exists
# ---------------------------------------------------------------------------

def scene_exists_pk(scene_pk: int) -> bool:
    """
    Check whether a scene exists by internal primary key.
    """
    if scene_pk <= 0:
        return False
    return get_scene_by_pk(scene_pk) is not None


def scene_exists_product(product_id: str) -> bool:
    """
    Check whether a scene exists by Sentinel product ID.
    """
    if not product_id:
        return False
    return get_scene_by_product_id(product_id) is not None


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------

def delete_scene_by_pk(scene_pk: int) -> bool:
    """
    Delete a scene by internal primary key.

    Returns:
        True  – scene existed and was deleted
        False – scene not found
    """
    if scene_pk <= 0:
        raise ValueError("delete_scene_by_pk(): scene_pk must be positive")

    session = get_session()
    scene = session.get(Scene, scene_pk)
    if scene is None:
        return False

    session.delete(scene)
    session.commit()
    return True


def delete_scene_by_product(product_id: str) -> bool:
    """
    Delete a scene by Sentinel product ID.

    Returns:
        True  – scene existed and was deleted
        False – scene not found
    """
    if not product_id:
        raise ValueError("delete_scene_by_product(): product_id required")

    session = get_session()
    stmt = select(Scene).where(Scene.product_id == product_id)
    scene = session.scalar(stmt)
    if scene is None:
        return False

    session.delete(scene)
    session.commit()
    return True
