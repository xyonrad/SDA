# sda/models/region.py
from __future__ import annotations

from datetime import datetime

from sqlalchemy import Float, Integer, String, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from sda.db.base import Base


class Region(Base):
    __tablename__ = "regions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)

    # Bounding box: (lon_min, lat_min, lon_max, lat_max)
    lon_min: Mapped[float] = mapped_column(Float, nullable=False)
    lat_min: Mapped[float] = mapped_column(Float, nullable=False)
    lon_max: Mapped[float] = mapped_column(Float, nullable=False)
    lat_max: Mapped[float] = mapped_column(Float, nullable=False)

    meta: Mapped[dict] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

