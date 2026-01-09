from __future__ import annotations

from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Integer, JSON

from sda.db.base import Base


class IndexArtifact(Base):
    """
    Raster index computed on the 10 m grid (NDVI, NBR, etc.).
    """
    __tablename__ = "index_artifacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    scene_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    index_name: Mapped[str] = mapped_column(String(16), index=True)
    resolution_m: Mapped[int] = mapped_column(Integer, default=10)

    path: Mapped[str] = mapped_column(String(512), nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), index=True, nullable=False)

    meta_data: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

