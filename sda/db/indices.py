from __future__ import annotations

"""
Store all the valuable features from the Sentinel-1/2 data.

IndexArtifact – describes a stored index artifact (e.g. NDVI GeoTIFF for a scene).
IndexFeature  – describes scalar features extracted from an artifact (e.g. mean NDVI).
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Optional

from sqlalchemy import select

from sda.db.session import get_session
from sda.models.index_artifact import IndexArtifact
from sda.models.index_feature import IndexFeature 

import hashlib

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now() -> datetime:
    return datetime.utcnow()

def _hash_path(path: str) -> str:
    return hashlib.sha256(path.encode("utf-8")).hexdigest()

def _hash_file_or_path(path: str) -> str:
    """
    Return the SHA256 of file contents when the file exists,
    otherwise fall back to a deterministic hash of the path string.
    """
    candidate = Path(path)
    if candidate.is_file():
        return hashlib.sha256(candidate.read_bytes()).hexdigest()
    return _hash_path(path)

# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

def register_index_path(
    scene_id: int,
    index_name: str,
    path: str,
    meta_data: dict[str, Any] | None = None,
    *,
    sha256: str | None = None,
    resolution_m: int = 10
) -> IndexArtifact:
    """
    Register a single index artifact (e.g. NDVI GeoTIFF) for a given scene.

    Required:
        scene_id   – external scene identifier (Sentinel product ID or own ID)
        index_name – logical index name (e.g. "NDVI", "VV_MEAN")
        path       – filesystem or object storage path

    Optional:
        meta_data  – arbitrary JSON-serializable dictionary
                     (CRS, resolution, processing options, etc.)
    """
    if not scene_id:
        raise ValueError("register_index_path() requires non-empty scene_id.")
    if not index_name:
        raise ValueError("register_index_path() requires non-empty index_name.")
    if not path:
        raise ValueError("register_index_path() requires non-empty path.")

    session = get_session()

    artifact = IndexArtifact(
        scene_id=scene_id,
        index_name=index_name,
        resolution_m=resolution_m,
        path=path,
        sha256=sha256 or _hash_file_or_path(path),
        meta_data=meta_data or {},
        created_at=_now(),
        updated_at=_now(),
    )

    session.add(artifact)
    session.commit()
    session.refresh(artifact)
    return artifact


def register_index_value(
    artifact_id: int,
    key: str,
    value: float,
    units: str | None = None,
) -> IndexFeature:
    """
    Register a single scalar feature for an existing index artifact.

    Example: key="mean", value=0.42, units="".
    """
    if not key:
        raise ValueError("register_index_value() requires non-empty key.")

    session = get_session()

    feature = IndexFeature(
        artifact_id=artifact_id,
        key=key,
        value=value,
        units=units,
        created_at=_now(),
    )

    session.add(feature)
    session.commit()
    session.refresh(feature)
    return feature


def register_index_values(
    artifact_id: int,
    values: dict[str, float],
    units: str | None = None,
) -> list[IndexFeature]:
    """
    Register multiple scalar features for a single artifact.

    values:
        mapping from key -> value, e.g. {"mean": 0.42, "std": 0.1}
    """
    if not values:
        raise ValueError("register_index_values() requires non-empty values dict.")

    session = get_session()
    features: list[IndexFeature] = []

    for key, val in values.items():
        feature = IndexFeature(
            artifact_id=artifact_id,
            key=key,
            value=float(val),
            units=units,
            created_at=_now(),
        )
        session.add(feature)
        features.append(feature)

    session.commit()

    # refresh for IDs if needed
    for f in features:
        session.refresh(f)

    return features


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------

def update_index(
    artifact_id: int,
    *,
    path: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> bool:
    """
    Update a single index artifact.

    Only provided fields are updated. The metadata argument updates
    IndexArtifact.meta_data.

    Returns:
        True if artifact existed and was updated, False otherwise.
    """
    session = get_session()
    artifact = session.get(IndexArtifact, artifact_id)
    if artifact is None:
        return False

    changed = False

    if path is not None:
        artifact.path = path
        changed = True

    if metadata is not None:
        artifact.meta_data = metadata
        changed = True

    if changed:
        artifact.updated_at = _now()
        session.commit()
    return changed


def update_indices(
    artifact_ids: list[int],
    *,
    path: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> int:
    """
    Batch update artifacts.

    Returns:
        number of artifacts actually updated.
    """
    if not artifact_ids:
        raise ValueError("update_indices() requires non-empty artifact_ids.")

    updated = 0
    for artifact_id in artifact_ids:
        if update_index(artifact_id, path=path, metadata=metadata):
            updated += 1
    return updated


# ---------------------------------------------------------------------------
# Get / list
# ---------------------------------------------------------------------------

def get_index(artifact_id: int) -> Optional[IndexArtifact]:
    """
    Get a single artifact by ID.
    """
    session = get_session()
    return session.get(IndexArtifact, artifact_id)


def get_indices(
    *,
    scene_id: int | None = None,
    index_name: str | None = None,
) -> list[IndexArtifact]:
    """
    Get artifacts filtered by scene_id and/or index_name.

    If no filters are provided, returns all artifacts (use with care).
    """
    session = get_session()
    stmt = select(IndexArtifact)

    if scene_id is not None:
        stmt = stmt.where(IndexArtifact.scene_id == scene_id)
    if index_name is not None:
        stmt = stmt.where(IndexArtifact.index_name == index_name)

    return list(session.scalars(stmt).all())


def get_index_value(feature_id: int) -> Optional[IndexFeature]:
    """
    Get a single feature (scalar index value) by ID.
    """
    session = get_session()
    return session.get(IndexFeature, feature_id)


def get_index_values(
    artifact_id: int,
    keys: list[str] | None = None,
) -> list[IndexFeature]:
    """
    Get all features for a given artifact, optionally filtered by keys.
    """
    session = get_session()
    stmt = select(IndexFeature).where(IndexFeature.artifact_id == artifact_id)

    if keys:
        stmt = stmt.where(IndexFeature.key.in_(keys))

    return list(session.scalars(stmt).all())


def list_indices_one(scene_id: int) -> list[IndexArtifact]:
    """
    List all artifacts for a single scene.
    """
    if not scene_id:
        raise ValueError("list_indices_one() requires non-empty scene_id.")

    session = get_session()
    stmt = select(IndexArtifact).where(IndexArtifact.scene_id == scene_id)
    return list(session.scalars(stmt).all())


def list_indices_all() -> list[IndexArtifact]:
    """
    List all artifacts for all scenes.
    """
    session = get_session()
    stmt = select(IndexArtifact)
    return list(session.scalars(stmt).all())


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------

def delete_index(artifact_id: int) -> bool:
    """
    Delete a single artifact and optionally its features (if cascade configured).

    Returns:
        True if artifact existed and was deleted, False otherwise.
    """
    session = get_session()
    artifact = session.get(IndexArtifact, artifact_id)
    if artifact is None:
        return False

    session.delete(artifact)
    session.commit()
    return True


def delete_indices(*artifact_ids: int) -> int:
    """
    Delete multiple artifacts by ID.

    Returns:
        number of artifacts actually deleted.
    """
    if not artifact_ids:
        raise ValueError("delete_indices() requires at least one artifact_id.")

    deleted = 0
    for artifact_id in artifact_ids:
        if delete_index(artifact_id):
            deleted += 1
    return deleted
