import os
import shutil

from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from .auth import is_connected, auth_responses, Permission
from ..exceptions import NotFoundHTTPException
from ..config import get_settings
from ..db import get_db
from ..models.chapter import Chapter
from ..schemas.chapter import ChapterSchema, ChapterResponse, LatestChaptersResponse, DetailedChapterResponse


settings = get_settings()

router = APIRouter(prefix="/chapter", tags=["Chapter"])


async def _get_chapter(chapter_id: UUID, db_session: AsyncSession = Depends(get_db)):
    return await Chapter.find(db_session, chapter_id, NotFoundHTTPException("Chapter not found"))


async def _get_detailed_chapter(chapter_id: UUID, db_session: AsyncSession = Depends(get_db)):
    return await Chapter.find_rel(db_session, chapter_id, Chapter.manga, NotFoundHTTPException("Chapter not found"))


@router.get("", response_model=LatestChaptersResponse)
async def get_latest_chapters(
    limit: Optional[int] = Query(10, ge=1, le=settings.max_page_limit),
    offset: Optional[int] = Query(0, ge=0),
    _: Chapter = Permission("view", Chapter.__class_acl__),
    db_session: AsyncSession = Depends(get_db),
):
    count, page = await Chapter.latest(db_session, limit, offset)
    return {
        "offset": offset,
        "limit": limit,
        "results": page,
        "total": count,
    }


get_responses = {
    200: {
        "description": "The requested chapter",
        "model": DetailedChapterResponse,
    },
    404: {
        "description": "The chapter couldn't be found",
        **NotFoundHTTPException.open_api("Chapter not found"),
    },
}


@router.get("/{chapter_id}", response_model=DetailedChapterResponse, responses=get_responses)
async def get_chapter(chapter: Chapter = Permission("view", _get_detailed_chapter)):
    return chapter


delete_responses = {
    **auth_responses,
    **get_responses,
    200: {
        "description": "The chapter was deleted",
        "content": {
            "application/json": {
                "example": "OK",
            },
        },
    },
}


@router.delete("/{chapter_id}", responses=delete_responses)
async def delete_chapter(
    chapter: Chapter = Permission("edit", _get_chapter), db_session: AsyncSession = Depends(get_db)
):
    shutil.rmtree(os.path.join(settings.media_path, str(chapter.manga_id), str(chapter.id)), True)
    return await chapter.delete(db_session)


put_responses = {
    **auth_responses,
    **get_responses,
    200: {
        "description": "The edited chapter",
        "model": ChapterResponse,
    },
}


@router.put("/{chapter_id}", response_model=ChapterResponse, responses=put_responses)
async def update_chapter(
    payload: ChapterSchema,
    chapter: Chapter = Permission("edit", _get_chapter),
    db_session: AsyncSession = Depends(get_db),
):
    await chapter.update(db_session, **payload.dict())
    return chapter
