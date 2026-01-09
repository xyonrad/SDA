# sentinel2_api.py
"""
Sentinel-2 identifiers used across the Copernicus Data Space Ecosystem (CDSE) and Sentinel Hub APIs.

Scope:
- Sentinel Hub / CDSE Sentinel Hub (Catalog / Process API): lower-case hyphenated collection identifiers.
- CDSE STAC Browser / STAC API: lower-case hyphenated collection identifiers for specific processing levels.
- CDSE OData Catalogue: upper-case mission-level collection name.

References (for maintainers):
- CDSE Sentinel Hub S2L1C (Catalog API capabilities): https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/Data/S2L1C.html
- CDSE Sentinel Hub S2L2A (Catalog API capabilities): https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/Data/S2L2A.html
- Sentinel Hub S2 L2A page: https://docs.sentinel-hub.com/api/latest/data/sentinel-2-l2a/
- CDSE STAC collections (browser): https://browser.stac.dataspace.copernicus.eu/
- CDSE OData collections list: https://documentation.dataspace.copernicus.eu/APIs/OData.html
"""

# ---------------------------------------------------------------------------
# Sentinel Hub / CDSE Sentinel Hub (Catalog API, Process API)
# ---------------------------------------------------------------------------

S2_COLLECTION_L1C: str = "sentinel-2-l1c"
"""
Sentinel-2 Level-1C collection identifier for Sentinel Hub-style APIs.
Distinguishing feature: Top-Of-Atmosphere (TOA) reflectance in cartographic geometry (orthorectified);
atmospheric effects are not corrected, which can bias surface analyses unless compensated downstream.
"""

S2_COLLECTION_L2A: str = "sentinel-2-l2a"
"""
Sentinel-2 Level-2A collection identifier for Sentinel Hub-style APIs.
Distinguishing feature: Bottom-Of-Atmosphere (BOA) / surface reflectance (typically Sen2Cor-derived),
making it the default choice for most land-surface analytics (vegetation indices, land cover, change detection).
"""

# ---------------------------------------------------------------------------
# CDSE STAC (product catalogue) — collection IDs for concrete processing levels
# ---------------------------------------------------------------------------

S2_STAC_COLLECTION_L1C: str = "sentinel-2-l1c"
"""
CDSE STAC collection id for Sentinel-2 L1C Items.
Use with STAC API search when you explicitly want L1C metadata/assets (e.g., to reproduce TOA-based pipelines).
"""

S2_STAC_COLLECTION_L2A: str = "sentinel-2-l2a"
"""
CDSE STAC collection id for Sentinel-2 L2A Items.
Use with STAC API search when you want L2A metadata/assets (surface reflectance products), typically preferred for analysis.
"""

# ---------------------------------------------------------------------------
# CDSE OData Catalogue — mission-level collection name
# ---------------------------------------------------------------------------

S2_ODATA_COLLECTION: str = "SENTINEL-2"
"""
CDSE OData mission-level collection name for Sentinel-2.
Use this in OData catalogue queries when the API expects a mission token rather than a processing-level STAC/Sentinel Hub id.
"""

