from datetime import datetime

from sqlalchemy import BigInteger, String, DateTime, func, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseDBModel


class User(BaseDBModel):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True)

    first_name: Mapped[str] = mapped_column(String(64), nullable=True)
    last_name: Mapped[str] = mapped_column(String(64), nullable=True)
    username: Mapped[str] = mapped_column(String(32), nullable=True)

    is_whitelisted: Mapped[bool] = mapped_column(Boolean(), server_default='false')
    is_admin: Mapped[bool] = mapped_column(Boolean(), server_default='false')

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
