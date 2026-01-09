"""
Sentinel-1 identifiers used across the Copernicus Data Space Ecosystem (CDSE) and Sentinel Hub APIs.

Scope:
- Sentinel Hub (Catalog / Process API): lower-case hyphenated collection identifiers.
- CDSE STAC Browser / STAC API: lower-case hyphenated collection identifiers for specific product families.
- CDSE OData Catalogue: upper-case mission-level collection names.

References (for maintainers):
- Sentinel Hub S1 GRD: https://docs.sentinel-hub.com/api/latest/data/sentinel-1-grd/
- CDSE Sentinel Hub S1GRD (Catalog API capabilities): https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/Data/S1GRD.html
- CDSE STAC collections (browser): https://browser.stac.dataspace.copernicus.eu/
- CDSE OData collections list: https://documentation.dataspace.copernicus.eu/APIs/OData.html
"""

# ---------------------------------------------------------------------------
# Sentinel Hub / CDSE Sentinel Hub (Catalog API, Process API)
# ---------------------------------------------------------------------------

S1_COLLECTION_GRD: str = "sentinel-1-grd"
"""
`Sentinel-1 Level-1 Ground Range Detected (GRD)` collection identifier for Sentinel Hub-style APIs.
Use this when the API expects a "collection identifier" / "type" such as in Catalog search or Process requests.
Distinguishing feature: detected + multi-looked SAR backscatter projected to ground range (analysis-friendly, not phase-preserving).
Source: Sentinel Hub S1 GRD docs; CDSE Sentinel Hub S1GRD page.
"""

# ---------------------------------------------------------------------------
# CDSE STAC (product catalogue) — collection IDs for concrete product families
# ---------------------------------------------------------------------------

S1_STAC_COLLECTION_GRD: str = "sentinel-1-grd"
"""
CDSE STAC collection id for `Sentinel-1 GRD products` (mirrors Sentinel Hub naming but is a STAC collection in CDSE).
Use this with pystac-client / STAC API search when you want GRD Items and their downloadable assets.
"""

S1_STAC_COLLECTION_SLC: str = "sentinel-1-slc"
"""
CDSE STAC collection id for `Sentinel-1 Level-1 Single Look Complex (SLC)` products (IW/EW/SM modes).
Distinguishing feature: complex SAR (phase preserved), required for interferometry and coherent processing;
generally larger and heavier than GRD, and less "plug-and-play" for simple backscatter analytics.
"""

S1_STAC_COLLECTION_SLC_WV: str = "sentinel-1-slc-wv"
"""
CDSE STAC collection id for `Sentinel-1 SLC products captured in Wave Mode (WV)`.
Distinguishing feature: WV is optimized for ocean wave spectra sampling, not for continuous land coverage;
this matters for availability and typical downstream use-cases.
"""

# ---------------------------------------------------------------------------
# CDSE OData Catalogue — mission-level collection names
# ---------------------------------------------------------------------------

S1_ODATA_COLLECTION: str = "SENTINEL-1"
"""
CDSE OData mission-level collection name for Sentinel-1.
Use this when forming OData queries against the CDSE catalogue where collections are expressed as upper-case mission tokens,
rather than STAC/Sentinel Hub collection identifiers.
"""

S1_ODATA_COLLECTION_RTC: str = "SENTINEL-1-RTC"
"""
CDSE OData mission-level collection name for `Sentinel-1 RTC` products.
Distinguishing feature: RTC denotes radiometric terrain correction (analysis-ready normalization with DEM-based orthorectification),
reducing terrain-induced radiometric distortions compared to plain GRD backscatter.
Source: CDSE OData documentation (explicitly lists SENTINEL-1-RTC among acceptable collection attribute sets).
"""
