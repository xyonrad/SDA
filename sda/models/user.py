from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
from sda.db.base import Base

class User(Base):
    __tablename__ = "users"

    id:    Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    login: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    pass_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    token: Mapped[str] = mapped_column(String(128), nullable=True)
    role:  Mapped[str] = mapped_column(String(64), default="user", nullable=False)

