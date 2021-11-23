import uuid

from sqlalchemy import Column, String, DateTime, func, select, ForeignKey
from sqlalchemy.orm import relationship, joinedload
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from .base import Base
from ..fastapi_permissions import Allow, Everyone, Authenticated


class Comment(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    author_id = Column(UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    content = Column(String, nullable=False)
    chapter_id = Column(UUID(as_uuid=True), ForeignKey("chapter.id", ondelete="CASCADE"), nullable=False)
    reply_to = Column(UUID(as_uuid=True))
    create_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    chapter = relationship("Chapter", back_populates="comments")
    author = relationship("User", back_populates="comments")

    __mapper_args__ = {"eager_defaults": True}

    @property
    def __acl__(self):
        return (
            *self.__class_acl__(),
            (Allow, [f"user:{self.author_id}"], "edit"),
        )

    @classmethod
    def __class_acl__(cls):
        return (
            (Allow, [Everyone], "view"),
            (Allow, [Authenticated], "create"),
            (Allow, ["role:uploader"], "edit"),
            (Allow, ["role:admin"], "edit"),
        )

    @classmethod
    async def from_chapter(
        cls,
        db_session: AsyncSession,
        chapter_id: uuid.UUID,
        limit: int = 20,
        offset: int = 0,
    ):
        stmt = select(cls).where(cls.chapter_id == chapter_id).options(joinedload(cls.author))
        return await cls.pagination(db_session, stmt, limit, offset, (cls.create_time.desc(),))
