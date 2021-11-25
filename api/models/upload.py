import uuid

from sqlalchemy import Column, ForeignKey, delete, String, select
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from .base import Base
from ..fastapi_permissions import Allow


class UploadSession(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("user.id", name="fk_session_owner", ondelete="CASCADE"))
    chapter_id = Column(UUID(as_uuid=True), ForeignKey("chapter.id", ondelete="CASCADE"))
    manga_id = Column(UUID(as_uuid=True), ForeignKey("manga.id", ondelete="CASCADE"), nullable=False)
    manga = relationship("Manga", back_populates="sessions")
    chapter = relationship("Chapter", back_populates="sessions")
    blobs = relationship("UploadedBlob", back_populates="session", cascade="all, delete", passive_deletes=True)

    @property
    def __acl__(self):
        return (
            *self.__class_acl__(),
            (Allow, ["role:uploader", f"user:{self.owner_id}"], "view"),
            (Allow, ["role:uploader", f"user:{self.owner_id}"], "edit"),
        )

    @classmethod
    def __class_acl__(cls):
        return (
            (Allow, ["role:admin"], "create"),
            (Allow, ["role:uploader"], "create"),
            (Allow, ["role:admin"], "view"),
            (Allow, ["role:admin"], "edit"),
        )

    @classmethod
    async def flush(cls, db_session: AsyncSession):
        stmt = delete(cls)
        return await db_session.execute(stmt)


class UploadedBlob(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    session_id = Column(UUID(as_uuid=True), ForeignKey("uploadsession.id", ondelete="CASCADE"), nullable=False)
    session = relationship("UploadSession", back_populates="blobs")

    @classmethod
    async def from_session(cls, db_session: AsyncSession, session_id: UUID):
        stmt = select(cls).where(cls.session_id == session_id)
        result = await db_session.execute(stmt)

        return result.scalars().all()
