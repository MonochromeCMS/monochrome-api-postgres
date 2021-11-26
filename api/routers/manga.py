import os
import shutil
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from PIL import Image
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import get_settings
from ..db import get_db
from ..exceptions import BadRequestHTTPException, NotFoundHTTPException
from ..fastapi_permissions import has_permission, permission_exception
from ..models.chapter import Chapter
from ..models.manga import Manga
from ..models.user import User
from ..schemas.chapter import ChapterResponse
from ..schemas.manga import MangaResponse, MangaSchema, MangaSearchResponse
from .auth import Permission, auth_responses, get_active_principals, get_connected_user

settings = get_settings()

router = APIRouter(prefix="/manga", tags=["Manga"])


async def _get_manga(manga_id: UUID, db_session: AsyncSession = Depends(get_db)):
    return await Manga.find(db_session, manga_id, NotFoundHTTPException("Manga not found"))


post_responses = {
    **auth_responses,
    201: {
        "description": "The created manga",
        "model": MangaResponse,
    },
}


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=MangaResponse,
    responses=post_responses,
)
async def create_manga(
    payload: MangaSchema,
    user: User = Depends(get_connected_user),
    _: Manga = Permission("create", Manga.__class_acl__),
    db_session: AsyncSession = Depends(get_db),
):
    manga = Manga(**payload.dict(), owner_id=user.id)
    await manga.save(db_session)
    os.mkdir(os.path.join(settings.media_path, str(manga.id)))
    return manga


@router.get("", response_model=MangaSearchResponse)
async def search_manga(
    title: str = "",
    limit: Optional[int] = Query(10, ge=1, le=settings.max_page_limit),
    offset: Optional[int] = Query(0, ge=0),
    _: Manga = Permission("view", Manga.__class_acl__),
    db_session: AsyncSession = Depends(get_db),
):
    count, page = await Manga.search(db_session, title, limit, offset)
    return {
        "offset": offset,
        "limit": limit,
        "results": page,
        "total": count,
    }


get_responses = {
    404: {
        "description": "The manga couldn't be found",
        **NotFoundHTTPException.open_api("Manga not found"),
    },
    200: {
        "description": "The requested manga",
        "model": MangaResponse,
    },
}


@router.get("/{manga_id}", response_model=MangaResponse, responses=get_responses)
async def get_manga(manga: Manga = Permission("view", _get_manga)):
    return manga


get_chapters_responses = {
    **get_responses,
    200: {
        "description": "The requested chapters",
        "model": list[ChapterResponse],
    },
}


@router.get("/{manga_id}/chapters", response_model=list[ChapterResponse], responses=get_chapters_responses)
async def get_manga_chapters(
    manga: Manga = Permission("view", _get_manga),
    user_principals=Depends(get_active_principals),
    db_session: AsyncSession = Depends(get_db),
):
    if await has_permission(user_principals, "view", Chapter.__class_acl__()):
        return await Chapter.from_manga(db_session, manga.id)
    else:
        raise permission_exception


delete_responses = {
    **auth_responses,
    **get_responses,
    200: {
        "description": "The manga was deleted",
        "content": {
            "application/json": {
                "example": "OK",
            },
        },
    },
}


@router.delete("/{manga_id}", responses=delete_responses)
async def delete_manga(manga: Manga = Permission("edit", _get_manga), db_session: AsyncSession = Depends(get_db)):
    shutil.rmtree(os.path.join(settings.media_path, str(manga.id)))
    return await manga.delete(db_session)


put_responses = {
    **auth_responses,
    **get_responses,
    200: {
        "description": "The edited manga",
        "model": MangaResponse,
    },
}


@router.put("/{manga_id}", response_model=MangaResponse, responses=put_responses)
async def update_manga(
    payload: MangaSchema,
    manga: Manga = Permission("edit", _get_manga),
    db_session: AsyncSession = Depends(get_db),
):
    await manga.update(db_session, **payload.dict())
    return manga


def save_cover(manga_id: UUID, file: File):
    im = Image.open(file)
    im.convert("RGB").save(os.path.join(settings.media_path, str(manga_id), "cover.jpg"))


put_cover_responses = {
    **auth_responses,
    **get_responses,
    400: {
        "description": "The cover isn't a valid image",
        **BadRequestHTTPException.open_api("<image_name> is not an image"),
    },
    200: {
        "description": "The edited manga",
        "model": MangaResponse,
    },
}


@router.put("/{manga_id}/cover", responses=put_cover_responses)
async def set_manga_cover(
    payload: UploadFile = File(...),
    manga: Manga = Permission("edit", _get_manga),
    db_session: AsyncSession = Depends(get_db),
):
    if not payload.content_type.startswith("image/"):
        raise BadRequestHTTPException(f"'{payload.filename}' is not an image")

    save_cover(manga.id, payload.file)
    await manga.save(db_session)

    return manga
