from __future__ import annotations

from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime, Integer, JSON

from sda.db.base import Base


class Stats(Base):
    __tablename__ = "stats"

    run_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    stats: Mapped[dict] = mapped_column(JSON)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

