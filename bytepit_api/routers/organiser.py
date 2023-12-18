import uuid

from fastapi import APIRouter, status, HTTPException, Depends
from typing import Annotated

import bytepit_api.services.organiser_service as organiser_service

from bytepit_api.database.queries import get_organisers_problems
from bytepit_api.dependencies.auth_dependencies import get_current_verified_user

router = APIRouter(prefix="/organiser", tags=["organiser"])


@router.get("/{organiser_id}/problems")
async def get_problems_by_organiser_id(organiser_id: uuid.UUID):
    problems = get_organisers_problems(organiser_id)
    if problems:
        return problems
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No problems found")


@router.get("/{organiser_id}/competitions")
async def get_competitions_by_organiser_id(
    organiser_id: uuid.UUID,
    current_user: Annotated[uuid.UUID, Depends(get_current_verified_user)]
):
    return organiser_service.get_all_competitions_by_organiser_id(organiser_id)
