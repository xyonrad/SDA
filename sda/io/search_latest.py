from __future__ import annotations

"""
Search utilities for recent CDSE STAC items.
"""

from datetime import datetime, timedelta
from pystac_client import Client
from .cdse_consts import CDSE_CLIENT_URL
from typing import Optional
from pystac import Item

_client: Client = Client.open(url=CDSE_CLIENT_URL)

def search_latest(
        collection: str, 
        aoi_geojson: dict, 
        day_utc: datetime, 
        fallback_days: int = 14
        ) -> Optional[Item | None]:
    """
    Return the most recent STAC Item for a collection and AOI within a time window.

    Args:
        collection     – STAC collection identifier (e.g. "sentinel-2-l2a").
        aoi_geojson    – GeoJSON geometry used for spatial filtering.
        day_utc        – reference date in UTC.
        fallback_days  – number of days before day_utc to include in the window.
    """
    start = (day_utc - timedelta(days=fallback_days)).isoformat()
    end   = (day_utc + timedelta(days=1)).isoformat()

    search = _client.search(
        collections=[collection],
        intersects=aoi_geojson,
        datetime=f"{start}/{end}",
        method="POST",
        limit=1,
        max_items=1,
        sortby=[{"field": "datetime", "direction": "desc"}],
    )

    for it in search.items():
        return it
    return None
