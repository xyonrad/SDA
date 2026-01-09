from __future__ import annotations

from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Integer, Boolean, JSON

from sda.db.base import Base


class SceneAsset(Base):
    """
    Any raster directly tied to a Scene:
    - raw bands (B04_10m, B12_20m)
    - resampled bands (B12_10m)
    - masks (SCL_10m)
    """
    __tablename__ = "scene_assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    scene_id: Mapped[int] = mapped_column(Integer, index=True)

    kind: Mapped[str] = mapped_column(String(32), index=True)
    resolution_m: Mapped[int] = mapped_column(Integer)   # 10 or 20
    dtype: Mapped[str] = mapped_column(String(16))       # uint16 / uint8 / float32

    path: Mapped[str] = mapped_column(String(512))
    sha256: Mapped[str] = mapped_column(String(64), index=True)

    is_resampled: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

