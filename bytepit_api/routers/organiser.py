import uuid
from fastapi import APIRouter, Depends
from typing import Annotated

import bytepit_api.services.organiser_service as organiser_service

from bytepit_api.dependencies.auth_dependencies import get_current_verified_user
from bytepit_api.models.db_models import User


router = APIRouter(prefix="/organiser", tags=["organiser"])


@router.get("/{organiser_id}/problems")
def get_problems_by_organiser_id(organiser_id: uuid.UUID):
    return organiser_service.get_problems_by_organiser_id(organiser_id)


@router.get("/{organiser_id}/competitions")
def get_competitions_by_organiser_id(
    organiser_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_verified_user)]
):
    return organiser_service.get_all_competitions_by_organiser_id(organiser_id)
