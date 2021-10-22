import uuid
import enum

from typing import Union
from pydantic import BaseModel
from sqlalchemy import Column, String, select, or_, and_, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from .base import Base
from ..fastapi_permissions import Allow, Authenticated


class Role(str, enum.Enum):
    admin = "admin"
    uploader = "uploader"
    user = "user"


class User(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role = Column(Enum(Role), nullable=False, default=Role.user)
    username = Column(String(15), nullable=False, unique=True)
    email = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)

    @property
    def principals(self):
        return [f"user:{self.id}", f"role:{self.role}"]

    @property
    def __acl__(self):
        return (
            *self.__class_acl__(),
            (Allow, [f"user:{self.id}"], "view"),
            (Allow, [f"user:{self.id}"], "edit"),
        )

    @classmethod
    def __class_acl__(cls):
        return (
            (Allow, ["role:admin"], "create"),
            (Allow, ["role:admin"], "view"),
            (Allow, ["role:admin"], "edit"),
        )

    @classmethod
    async def from_username_email(
        cls, db_session: AsyncSession, username_email: str, mail: str = "", ignore_user: uuid.UUID = None
    ):
        if mail == "":
            stmt = select(cls).where(or_(cls.username == username_email, cls.email == username_email))
        elif mail is None:
            stmt = select(cls).where(cls.username == username_email)
        else:
            stmt = select(cls).where(or_(cls.username == username_email, cls.email == mail))

        if ignore_user:
            stmt = stmt.where(cls.id != ignore_user)

        result = await db_session.execute(stmt)
        return result.scalars().first()

    @classmethod
    async def search(
        cls,
        db_session: AsyncSession,
        name: str = "",
        filters: Union[BaseModel, None] = None,
        limit: int = 20,
        offset: int = 0,
    ):
        stmt = select(cls).where(cls.username.ilike(f"%{name}%"))
        if filters is not None:
            filters = {k: v for k, v in filters.dict().items() if v}
            stmt = stmt.where(and_(True, *[getattr(cls, k) == v for k, v in filters.items()]))
        return await cls.pagination(db_session, stmt, limit, offset, (cls.username,))
