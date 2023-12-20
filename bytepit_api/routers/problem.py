import uuid

from typing import Annotated, List

from fastapi import APIRouter, Depends

from bytepit_api.dependencies.auth_dependencies import get_current_approved_organiser
from bytepit_api.helpers import blob_storage_helpers
from bytepit_api.models.dtos import ProblemDTO, CreateProblemDTO, ModifyProblemDTO
from bytepit_api.models.db_models import User
from bytepit_api.services import problem_service


router = APIRouter(prefix="/problems", tags=["problems"])


@router.get("", response_model=List[ProblemDTO])
def list_problems():
    return problem_service.get_all_problems()


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


@router.get("/{problem_id}/{file_name}")
def get_file(problem_id: str, file_name: str):
    return blob_storage_helpers.get_blob(f"{problem_id}/{file_name}")
