from __future__ import annotations

from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Integer, JSON

from sda.db.base import Base


class Change(Base):
    """
    Raster delta between two scenes for the same index.
    Example: dNDVI, dNBR.
    """
    __tablename__ = "changes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    scene_before_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    scene_after_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)

    index_name: Mapped[str] = mapped_column(String(16), index=True)
    method: Mapped[str] = mapped_column(String(32))          # diff / zscore / seasonal
    thresholds: Mapped[dict] = mapped_column(JSON, default=dict)

    path: Mapped[str] = mapped_column(String(512), nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), index=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

