import uuid
from typing import Annotated, List

from fastapi import APIRouter, Depends

from bytepit_api.dependencies.auth_dependencies import get_current_verified_user
from bytepit_api.models.db_models import User
from bytepit_api.models.dtos import CompetitionDTO, ProblemDTO
from bytepit_api.services import organiser_service


router = APIRouter(prefix="/organiser", tags=["organiser"])


@router.get("/{organiser_id}/problems", response_model=List[ProblemDTO])
def get_problems_by_organiser(organiser_id: uuid.UUID):
    return organiser_service.get_problems_by_organiser(organiser_id)


@router.get("/{organiser_id}/competitions", response_model=List[CompetitionDTO])
def get_competitions_by_organiser(
    organiser_id: uuid.UUID, current_user: Annotated[User, Depends(get_current_verified_user)]
):
    return organiser_service.get_competitions_by_organiser(organiser_id)
