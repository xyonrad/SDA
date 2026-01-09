from __future__ import annotations

from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Integer, Float

from sda.db.base import Base


class IndexFeature(Base):
    """
    Scalar features derived from an IndexArtifact.
    Example: mean NDVI, std NDVI, vegetation area ratio.
    """
    __tablename__ = "index_features"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    artifact_id: Mapped[int] = mapped_column(Integer, index=True)

    key: Mapped[str] = mapped_column(String(64))
    value: Mapped[float] = mapped_column(Float)
    units: Mapped[str | None] = mapped_column(String(32), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

