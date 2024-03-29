import uuid

from typing import Annotated, List

from fastapi import APIRouter, Depends

from bytepit_api.dependencies.auth_dependencies import (
    get_current_approved_organiser,
    get_current_verified_user,
)
from bytepit_api.helpers import blob_storage_helpers
from bytepit_api.models.dtos import (
    CreateSubmissionDTO,
    ProblemDTO,
    CreateProblemDTO,
    ModifyProblemDTO,
    ProblemResultStatusDTO,
    UserStatisticsDTO,
)
from bytepit_api.models.db_models import User
from bytepit_api.services import problem_service


router = APIRouter(prefix="/problems", tags=["problems"])


@router.get("", response_model=List[ProblemDTO])
def list_problems():
    return problem_service.get_all_problems()


@router.get("/user-statistics/{user_id}", response_model=UserStatisticsDTO)
def get_user_statistics(user_id: uuid.UUID, current_user: Annotated[User, Depends(get_current_verified_user)]):
    return problem_service.get_user_statistics(user_id)


@router.get("/problems-by-organiser/{organiser_id}", response_model=List[ProblemDTO])
def get_problems_by_organiser(
    organiser_id: uuid.UUID, current_user: Annotated[User, Depends(get_current_verified_user)]
):
    return problem_service.get_problems_by_organiser(organiser_id)


@router.get("/available", response_model=List[ProblemDTO])
def get_available_problems(current_user: Annotated[User, Depends(get_current_verified_user)]):
    return problem_service.get_available_problems()


@router.get("/{problem_id}", response_model=ProblemDTO)
def get_problem(problem_id: uuid.UUID):
    return problem_service.get_problem(problem_id)


@router.post("")
def create_problem(
    form_data: Annotated[CreateProblemDTO, Depends()],
    current_user: Annotated[User, Depends(get_current_approved_organiser)],
):
    return problem_service.create_problem(form_data, current_user.id)


@router.patch("/{problem_id}")
def modify_problem(
    problem_id: uuid.UUID,
    form_data: Annotated[ModifyProblemDTO, Depends()],
    current_user: Annotated[User, Depends(get_current_approved_organiser)],
):
    return problem_service.modify_problem(problem_id, form_data)


@router.delete("/{problem_id}")
def delete_problem(problem_id: uuid.UUID, current_user: Annotated[User, Depends(get_current_approved_organiser)]):
    return problem_service.delete_problem(problem_id)


@router.post("/create-submission", response_model=ProblemResultStatusDTO)
def create_submission(
    current_user: Annotated[User, Depends(get_current_verified_user)],
    form_data: Annotated[CreateSubmissionDTO, Depends()],
):
    return problem_service.create_submission(current_user.id, form_data)


@router.get("/submission/{problem_id}")
def get_submission(problem_id: uuid.UUID, current_user: Annotated[User, Depends(get_current_verified_user)]):
    return problem_service.get_submission(problem_id, current_user.id)


@router.get("/submission/{problem_id}/{competition_id}")
def get_submission_on_competition(
    problem_id: uuid.UUID,
    competition_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_verified_user)],
):
    return problem_service.get_submission_on_competition(problem_id, current_user.id, competition_id)


@router.get("/{problem_id}/{file_name}")
def get_file(problem_id: uuid.UUID, file_name: str):
    return blob_storage_helpers.get_blob(f"{problem_id}/{file_name}")
