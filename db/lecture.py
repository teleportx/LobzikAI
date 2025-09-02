import uuid

from sqlalchemy import Text, UUID, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseDBModel


class Lecture(BaseDBModel):
    __tablename__ = 'lecture'

    id: Mapped[uuid.UUID] = mapped_column(UUID(), primary_key=True, default=uuid.uuid4)
    owner_id: Mapped[int] = mapped_column(ForeignKey('user.id'), index=True)

    raw_text: Mapped[str] = mapped_column(Text())
    summarized_text: Mapped[str] = mapped_column(Text())
