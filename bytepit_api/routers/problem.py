import uuid
from typing import Annotated, List

from fastapi import APIRouter, Depends, Response, status, HTTPException

from bytepit_api.dependencies.auth_dependencies import get_current_approved_organiser, get_current_admin_or_approved_organiuser_user
from bytepit_api.models.dtos import ProblemDTO, CreateProblemDTO, ModifyProblemDTO
from bytepit_api.database.queries import get_all_problems, get_problem_by_id, insert_problem
from bytepit_api.helpers.blob_storage_helpers import upload_blob, get_file_by_problem_id_and_file_name
from bytepit_api.helpers.problem_helpers import remove_problem, validate_inserted_problems, modify_problem_in_database, modify_problem_in_blob_storage


router = APIRouter(prefix="/problems", tags=["problems"])


@router.get("", response_model=List[ProblemDTO])
def list_problems():
    return get_all_problems()


@router.get("/{problem_id}", response_model=ProblemDTO)
def get_problem(problem_id: uuid.UUID):
    problem = get_problem_by_id(problem_id)
    if not problem:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found")
    return problem


@router.post("")
def create_problem(
    form_data: Annotated[CreateProblemDTO, Depends()],
    current_user: Annotated[uuid.UUID, Depends(get_current_approved_organiser)]
):
    if not validate_inserted_problems(form_data.test_files):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid test files",
        )
    result = insert_problem(
        form_data.name,
        form_data.example_input,
        form_data.example_output,
        form_data.is_hidden,
        form_data.num_of_points,
        form_data.runtime_limit,
        current_user.id,
        form_data.description,
        form_data.is_private,
    )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong. Please try again.",
        )
    for test_file in form_data.test_files:
        data = test_file.file.read()
        upload_blob(f"{result}/{test_file.filename}", data)
    return Response(status_code=status.HTTP_201_CREATED)


@router.patch("/{problem_id}")
def modify_problem(
    problem_id: uuid.UUID,
    form_data: Annotated[ModifyProblemDTO, Depends()],
    current_user: Annotated[uuid.UUID, Depends(get_current_admin_or_approved_organiuser_user)]
):
    problem_to_modify = get_problem_by_id(problem_id)
    if not problem_to_modify:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Problem not found",
        )
    if not modify_problem_in_database(problem_to_modify, form_data, problem_id):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong. Please try again.",
        )
    if form_data.test_files != []:
        if not validate_inserted_problems(form_data.test_files):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid test files",
            )
        if not modify_problem_in_blob_storage(problem_id, form_data):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Something went wrong. Please try again.",
            )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/{problem_id}")
def delete_problem(
    problem_id: uuid.UUID,
    current_user: Annotated[uuid.UUID, Depends(get_current_approved_organiser)]
):
    result = remove_problem(problem_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong. Please try again.",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{problem_id}/{file_name}")
def get_file(problem_id: str, file_name: str):
    file = get_file_by_problem_id_and_file_name(f"{problem_id}/{file_name}")
    if not file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    return file
