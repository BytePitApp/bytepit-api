import uuid

from typing import Union, List
from fastapi import UploadFile, HTTPException, status, Response

from bytepit_api.database import problem_queries
from bytepit_api.helpers import blob_storage_helpers, problem_helpers
from bytepit_api.models.dtos import ProblemDTO, CreateProblemDTO, ModifyProblemDTO


def get_all_problems():
    result = problem_queries.get_all_problems()
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Could not found any problems")
    return result


def get_problem(problem_id: uuid.UUID):
    return problem_helpers.get_problem(problem_id)


def delete_problem(problem_id: uuid.UUID):
    result = problem_queries.delete_problem(problem_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Could not delete problem with id {problem_id}"
        )
    blob_storage_helpers.delete_all_blobs(problem_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def create_problem(problem: CreateProblemDTO, current_user_id: uuid.UUID):
    if not problem_helpers.validate_problems(problem.test_files):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid test files")
    problem_id = problem_queries.insert_problem(problem, current_user_id)
    if not problem_id:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not insert problem")
    for test_file in problem.test_files:
        data = test_file.file.read()
        blob_storage_helpers.upload_blob(f"{problem_id}/{test_file.filename}", data)
    return Response(status_code=status.HTTP_201_CREATED)


def modify_problem(problem_id: uuid.UUID, problem: ModifyProblemDTO):
    if len(problem.test_files) > 0:
        if not problem_helpers.validate_problems(problem.test_files):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid test files")
        problem_helpers.modify_problem_in_blob_storage(problem_id, problem.test_files)
    problem_helpers.modify_problem_in_database(problem_id, problem)
    return Response(status_code=status.HTTP_200_OK)
