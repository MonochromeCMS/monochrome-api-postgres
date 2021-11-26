from fastapi import APIRouter

from ..config import get_settings
from ..models.settings import Settings
from ..schemas.settings import SettingsSchema
from .auth import Permission, auth_responses

global_settings = get_settings()

router = APIRouter(prefix="/settings", tags=["Settings"])

custom_settings = Settings()


@router.get(
    "",
    response_model=SettingsSchema,
    dependencies=[Permission("view", custom_settings)],
)
async def get_site_settings():
    return custom_settings.get()


put_responses = {
    **auth_responses,
    200: {
        "description": "The website settings",
        "model": SettingsSchema,
    },
}


@router.put(
    "", response_model=SettingsSchema, dependencies=[Permission("edit", custom_settings)], responses=put_responses
)
async def edit_site_settings(settings: SettingsSchema):
    return custom_settings.set(settings)
