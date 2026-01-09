from __future__ import annotations

"""
AOI (Areas of Interest), analysis regions.
"""

from typing import Any, Optional, List, Tuple

from sqlalchemy import select

from sda.auth.config import DEFAULT_STR
from sda.db.session import get_session
from sda.models.region import Region


# Constants

# Deprecated or too massive for the model, don't use
INTERNATIONAL_STR   = "INTERNATIONAL"
INTERNATIONAL_COORD = (-180.0, -90.0, 180.0, 90.0)

# Siberia full
SIBERIA_LONGITUDE_MIN = 50.0
SIBERIA_LONGITUDE_MAX = 180.0
SIBERIA_LATITUDE_MIN  = 50.0
SIBERIA_LATITUDE_MAX  = 75.0

SIBERIA_FULL: Tuple[float, float, float, float] = (
    SIBERIA_LONGITUDE_MIN,
    SIBERIA_LATITUDE_MIN,
    SIBERIA_LONGITUDE_MAX,
    SIBERIA_LATITUDE_MAX,
)


# ---------------------------------------------------------------------------
# Register
# ---------------------------------------------------------------------------

def register_region(
    name: str,
    geom_tuple: tuple[float, float, float, float],
    meta_dict: dict[str, Any] | None = None,
) -> Region:
    """
    Register a new AOI region.

    Args:
        name       – region name (must not be 'INTERNATIONAL').
        geom_tuple – bounding box (lon_min, lat_min, lon_max, lat_max).
        meta_dict  – optional JSON metadata.

    Returns:
        Region ORM instance.

    Raises:
        ValueError if INTERNATIONAL_* is used or name/geometry are invalid.
    """
    if not name:
        raise ValueError("register_region() requires non-empty name.")

    # Block deprecated / too-massive AOI for model
    if name == INTERNATIONAL_STR or geom_tuple == INTERNATIONAL_COORD:
        raise ValueError(DEFAULT_STR)

    if len(geom_tuple) != 4:
        raise ValueError("geom_tuple must be (lon_min, lat_min, lon_max, lat_max).")

    lon_min, lat_min, lon_max, lat_max = geom_tuple

    session = get_session()

    region = Region(
        name=name,
        lon_min=lon_min,
        lat_min=lat_min,
        lon_max=lon_max,
        lat_max=lat_max,
        meta=meta_dict or {},
    )

    session.add(region)
    session.commit()
    session.refresh(region)
    return region


# ---------------------------------------------------------------------------
# Get
# ---------------------------------------------------------------------------

def get_region_by_id(region_id: int) -> Optional[Region]:
    """
    Get a region by its ID.
    """
    session = get_session()
    return session.get(Region, region_id)


def get_regions_by_ids(*region_ids: int) -> list[Region]:
    """
    Get multiple regions by their IDs.
    """
    if not region_ids:
        raise ValueError("get_regions_by_ids() requires at least one region_id.")

    session = get_session()
    stmt = select(Region).where(Region.id.in_(region_ids))
    return list(session.scalars(stmt).all())


def get_region_by_name(name: str) -> Optional[Region]:
    """
    Get a region by its name.
    """
    if not name:
        raise ValueError("get_region_by_name() requires non-empty name.")

    session = get_session()
    stmt = select(Region).where(Region.name == name)
    return session.scalar(stmt)


def get_regions_by_names(*names: str) -> list[Region]:
    """
    Get multiple regions by their names.
    """
    if not names:
        raise ValueError("get_regions_by_names() requires at least one name.")

    session = get_session()
    stmt = select(Region).where(Region.name.in_(names))
    return list(session.scalars(stmt).all())


# ---------------------------------------------------------------------------
# List
# ---------------------------------------------------------------------------

def list_regions() -> list[Region]:
    """
    List all registered regions.
    """
    session = get_session()
    stmt = select(Region)
    return list(session.scalars(stmt).all())


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------

def update_region(
    region_id: int,
    *,
    name: str | None = None,
    geom_tuple: tuple[float, float, float, float] | None = None,
    meta_dict: dict[str, Any] | None = None,
) -> bool:
    """
    Update region properties.

    Only provided fields are updated.

    Returns:
        True if region existed and was updated, False otherwise.
    """
    session = get_session()
    region = session.get(Region, region_id)
    if region is None:
        return False

    changed = False

    if name is not None:
        if not name:
            raise ValueError("update_region(): name cannot be empty.")
        if name == INTERNATIONAL_STR:
            raise ValueError(DEFAULT_STR)
        region.name = name
        changed = True

    if geom_tuple is not None:
        if len(geom_tuple) != 4:
            raise ValueError("geom_tuple must be (lon_min, lat_min, lon_max, lat_max).")
        if geom_tuple == INTERNATIONAL_COORD:
            raise ValueError(DEFAULT_STR)
        lon_min, lat_min, lon_max, lat_max = geom_tuple
        region.lon_min = lon_min
        region.lat_min = lat_min
        region.lon_max = lon_max
        region.lat_max = lat_max
        changed = True

    if meta_dict is not None:
        region.meta = meta_dict
        changed = True

    if changed:
        # If Region has an updated_at, set it here; if not, this line can be removed
        # region.updated_at = datetime.utcnow()
        session.commit()

    return changed


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------

def delete_region(region_id: int) -> bool:
    """
    Delete a region by its ID.

    Returns:
        True if region existed and was deleted, False otherwise.
    """
    session = get_session()
    region = session.get(Region, region_id)
    if region is None:
        return False

    session.delete(region)
    session.commit()
    return True

