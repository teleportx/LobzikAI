from sqlalchemy import BigInteger, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseDBModel


class Lesson(BaseDBModel):
    __tablename__ = 'lesson'

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True)

    raw_text: Mapped[str] = mapped_column(Text())
    summarized_text: Mapped[str] = mapped_column(Text())
