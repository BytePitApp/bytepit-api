import uuid
from typing import Union
from typing import Annotated, List

from fastapi import APIRouter, Depends, Response, status, HTTPException, UploadFile, File

from bytepit_api.dependencies.auth_dependencies import get_current_admin_user, get_current_organiser_user
from bytepit_api.models.dtos import ProblemDTO, CreateProblemDTO, ModifyProblemDTO
from bytepit_api.database.queries import get_problems, get_problem_by_id, create_new_problem
from bytepit_api.helpers.blob_storage_helpers import upload_blob, get_blob, delete_blob, download_blob
from bytepit_api.helpers.problem_helpers import problem_delete


router = APIRouter(prefix="/problem", tags=["problem"])


@router.get("/list-problems", response_model=List[ProblemDTO])
def list_problems():
    return get_problems()


@router.get("/problem/{problemId}", response_model=ProblemDTO)
def get_problem(problemId: uuid.UUID):
    return get_problem_by_id(problemId)


@router.post("/create-problem")
async def create_problem(
    form_data: CreateProblemDTO,
    current_user: Annotated[uuid.UUID, Depends(get_current_organiser_user)]
):
    result = create_new_problem(
        form_data.name,
        form_data.example_input,
        form_data.example_output,
        form_data.is_hidden,
        form_data.num_of_points,
        form_data.runtime_limit,
        form_data.description,
        form_data.is_private,
    )
    for test_file in form_data.test_files:
        data = await test_file.file.read()
        upload_blob(test_file.filename, data)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong. Please try again.",
        )
    return Response(status_code=status.HTTP_201_CREATED)


# @router.post("/modify-problem")


@router.delete("/delete-problem/{problemId}")
def delete_problem(
    problemId: Union[int, uuid.UUID],
    current_user: Annotated[uuid.UUID, Depends(get_current_organiser_user)]
):
    result = problem_delete(problemId)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong. Please try again.",
        )
    return result


@router.get("/blobstorage/get/{dirname}/{filename}")
async def get_file(dirname: str, filename: str):
    return get_blob(f"{dirname}/{filename}")


# @router.get("/blobstorage/download/{filename}")
# async def download_file(filename: str):
#     return download_blob(filename)
