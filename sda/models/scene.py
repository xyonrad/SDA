from __future__ import annotations

from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Integer, JSON, Float

from sda.db.base import Base


class Scene(Base):
    """
    One satellite acquisition on a fixed grid.
    Derived directly from Sentinel-2 L2A metadata.
    """
    __tablename__ = "scenes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # External identifiers
    product_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    satellite: Mapped[str] = mapped_column(String(8), nullable=False)   # S2A / S2B / S2C
    tile: Mapped[str] = mapped_column(String(8), index=True)            # e.g. T41VNE

    acquisition_time: Mapped[datetime] = mapped_column(DateTime, index=True)

    # Spatial definition (canonical 10 m grid)
    crs: Mapped[str] = mapped_column(String(32))                         # EPSG:32641
    transform: Mapped[list[float]] = mapped_column(JSON)                 # affine (9 elems)
    width: Mapped[int] = mapped_column(Integer)
    height: Mapped[int] = mapped_column(Integer)

    lon_min: Mapped[float] = mapped_column(Float)
    lat_min: Mapped[float] = mapped_column(Float)
    lon_max: Mapped[float] = mapped_column(Float)
    lat_max: Mapped[float] = mapped_column(Float)

    processing_level: Mapped[str] = mapped_column(String(8), default="L2A")
    source_zip: Mapped[str] = mapped_column(String(512))

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

