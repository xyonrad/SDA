from __future__ import annotations

from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime, String, Integer, Boolean
from sda.db.base import Base

class CDSEToken(Base):
    """
    Persisted CDSE OAuth token data for a login.

    This model stores both the access token and the related metadata
    required for expiry checks and audit trails.
    """
    __tablename__ = "cdse_token"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    login: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    password: Mapped[str] = mapped_column(String(128), nullable=False)

    access_token: Mapped[str] = mapped_column(String(2048), nullable=False)
    refresh_token: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    token_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    scope: Mapped[str | None] = mapped_column(String(512), nullable=True)

    expires_in_s: Mapped[int | None] = mapped_column(Integer, nullable=True)
    issued_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    is_revoked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
