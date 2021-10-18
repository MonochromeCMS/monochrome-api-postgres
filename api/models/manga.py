import uuid
import enum

from fastapi_permissions import Allow, Everyone
from sqlalchemy import Column, String, select, Numeric, Enum, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from .base import Base


class Status(str, enum.Enum):
    ongoing = "ongoing"
    completed = "completed"
    hiatus = "hiatus"
    cancelled = "cancelled"


class Manga(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("user.id", name="fk_manga_owner"))
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    author = Column(String, nullable=False)
    artist = Column(String, nullable=False)
    create_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    year = Column(Numeric(4, 0))
    status = Column(Enum(Status), nullable=False)
    chapters = relationship("Chapter", back_populates="manga", cascade="all, delete", passive_deletes=True)
    sessions = relationship("UploadSession", back_populates="manga", cascade="all, delete", passive_deletes=True)

    __mapper_args__ = {"eager_defaults": True}

    @property
    def __acl__(self):
        return (
            *self.__class_acl__(),
            (Allow, ["role:uploader", f"user:{self.owner_id}"], "edit"),
        )

    @classmethod
    def __class_acl__(cls):
        return (
            (Allow, [Everyone], "view"),
            (Allow, ["role:admin"], "edit"),
            (Allow, ["role:admin"], "create"),
            (Allow, ["role:uploader"], "create"),
        )

    @classmethod
    async def search(cls, db_session: AsyncSession, title: str, limit: int = 20, offset: int = 0):
        escaped_title = title.replace("%", "\\%")
        stmt = select(cls).where(cls.title.ilike(f"%{escaped_title}%"))
        return await cls.pagination(db_session, stmt, limit, offset, (cls.create_time.desc(),))
