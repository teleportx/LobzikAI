import uuid
from datetime import datetime

from sqlalchemy import Text, UUID, ForeignKey, DateTime, func, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseDBModel


class Lecture(BaseDBModel):
    __tablename__ = 'lecture'

    id: Mapped[uuid.UUID] = mapped_column(UUID(), primary_key=True, default=uuid.uuid4)
    owner_id: Mapped[int] = mapped_column(ForeignKey('user.id'), index=True)

    title: Mapped[str] = mapped_column(String(128))
    raw_text: Mapped[str] = mapped_column(Text())
    summarized_text: Mapped[str] = mapped_column(Text())

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class LectureTestQuestion(BaseDBModel):
    __tablename__ = 'lecture_test_question'

    id: Mapped[uuid.UUID] = mapped_column(UUID(), primary_key=True, default=uuid.uuid4)
    lecture_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('lecture.id'), index=True)

    text: Mapped[str] = mapped_column(Text())
    answer: Mapped[str] = mapped_column(Text())
