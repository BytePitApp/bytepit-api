import uuid
from fastapi import APIRouter, Depends
from typing import Annotated

import bytepit_api.services.competition_service as competition_service

from bytepit_api.dependencies.auth_dependencies import get_current_approved_organiser, get_current_verified_user, get_current_admin_or_approved_organiser_user
from bytepit_api.models.dtos import CreateCompetitionDTO, ModifyCompetitionDTO
from bytepit_api.models.db_models import User


router = APIRouter(prefix="/competitions", tags=["competitions"])


@router.post("")
async def create_competition(
    form_data: Annotated[CreateCompetitionDTO, Depends()],
    current_user: Annotated[User, Depends(get_current_approved_organiser)]
):
    return competition_service.create_competition(form_data, current_user.id)


@router.get("")
async def get_all_competitions(current_user: Annotated[User, Depends(get_current_verified_user)]):
    return competition_service.get_all_competitions()


@router.get("/active")
async def get_active_competitions(current_user: Annotated[User, Depends(get_current_verified_user)]):
    return competition_service.get_every_active_competition()


@router.get("/random")
async def get_random_competition(current_user: Annotated[User, Depends(get_current_verified_user)]):
    return competition_service.get_one_random_competition()


@router.get("/{competition_id}")
async def get_competition(
    competition_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_verified_user)]
):
    return competition_service.get_one_competition(competition_id)


@router.post("/{competition_id}/trophy/{user_id}")
async def set_trophy(
    competition_id: uuid.UUID,
    user_id: uuid.UUID,
    position: int,
    current_user: Annotated[User, Depends(get_current_verified_user)]
):
    return competition_service.set_trophy_to_user(competition_id, user_id, position)


@router.patch("/{competition_id}")
async def modify_competition(
    competition_id: uuid.UUID,
    form_data: Annotated[ModifyCompetitionDTO, Depends()],
    current_user: Annotated[User, Depends(get_current_admin_or_approved_organiser_user)]
):
    return competition_service.modify_competition(competition_id, form_data)


@router.delete("/{competition_id}")
async def delete_competition(
    competition_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_admin_or_approved_organiser_user)]
):
    return competition_service.delete_competition(competition_id)
