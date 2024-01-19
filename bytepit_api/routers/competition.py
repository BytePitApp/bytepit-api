import uuid
from fastapi import APIRouter, Depends
from typing import Annotated, List

import bytepit_api.services.competition_service as competition_service

from bytepit_api.dependencies.auth_dependencies import get_current_approved_organiser, get_current_verified_user
from bytepit_api.models.dtos import CompetitionDTO, CompetitionResultDTO, CreateCompetitionDTO, ModifyCompetitionDTO
from bytepit_api.models.db_models import User


router = APIRouter(prefix="/competitions", tags=["competitions"])


@router.post("")
async def create_competition(
    form_data: Annotated[CreateCompetitionDTO, Depends()],
    current_user: Annotated[User, Depends(get_current_approved_organiser)],
):
    return competition_service.create_competition(form_data, current_user.id)


@router.post("/virtual", response_model=str)
async def create_virtual_competition(
    parent_competition_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_verified_user)],
):
    return competition_service.create_virtual_competition(parent_competition_id, current_user.id)


@router.get("", response_model=List[CompetitionDTO])
async def get_all_competitions(
    current_user: Annotated[User, Depends(get_current_verified_user)], trophies: bool = False
):
    return competition_service.get_all_competitions(current_user.id, trophies)


@router.get("/random", response_model=CompetitionDTO)
async def get_random_competition(current_user: Annotated[User, Depends(get_current_verified_user)]):
    return competition_service.get_random_competition()


@router.get("/{competition_id}", response_model=CompetitionDTO)
async def get_competition(competition_id: uuid.UUID, current_user: Annotated[User, Depends(get_current_verified_user)]):
    return competition_service.get_competition(competition_id)


@router.patch("/{competition_id}")
async def modify_competition(
    competition_id: uuid.UUID,
    form_data: Annotated[ModifyCompetitionDTO, Depends()],
    current_user: Annotated[User, Depends(get_current_approved_organiser)],
):
    return competition_service.modify_competition(competition_id, form_data)


@router.delete("/{competition_id}")
async def delete_competition(
    competition_id: uuid.UUID, current_user: Annotated[User, Depends(get_current_approved_organiser)]
):
    return competition_service.delete_competition(competition_id)


@router.get("/{competition_id}/results", response_model=List[CompetitionResultDTO])
async def get_competition_results(
    competition_id: uuid.UUID, current_user: Annotated[User, Depends(get_current_verified_user)]
):
    return competition_service.get_competition_results(competition_id)


@router.get("/virtual/{competition_id}/results", response_model=List[CompetitionResultDTO])
async def get_virtual_competition_results(
    competition_id: uuid.UUID, current_user: Annotated[User, Depends(get_current_verified_user)]
):
    return competition_service.get_virtual_competition_results(competition_id, current_user.id)


@router.get("/competitions-by-organiser/{organiser_id}", response_model=List[CompetitionDTO])
async def get_competitions_by_organiser(
    organiser_id: uuid.UUID, current_user: Annotated[User, Depends(get_current_verified_user)], trophies: bool = False
):
    return competition_service.get_competitions_by_organiser(organiser_id, trophies)
