import uuid
import re

from typing import Union, List
from fastapi import UploadFile

from bytepit_api.database.queries import delete_problem_by_problem_id, modify_problem_by_id
from bytepit_api.helpers.blob_storage_helpers import delete_all_blobs_by_problem_id, upload_blob
from bytepit_api.models.dtos import ProblemDTO


def remove_problem(problem_id: Union[int, uuid.UUID]):
    result = delete_problem_by_problem_id(problem_id)
    if not result:
        return None
    result = delete_all_blobs_by_problem_id(problem_id)
    if not result:
        return None
    return True


def validate_inserted_problems(problems: List[UploadFile]):
    if len(problems) == 0:
        return False
    pattern = re.compile(r'^(\d+)_(in|out)\.txt$')
    problem_names = set()
    for problem in problems:
        if not pattern.match(problem.filename):
            return False
        if problem.filename in problem_names:
            return False
        problem_names.add(problem.filename)
    amount_of_problems = len(problem_names) // 2
    if amount_of_problems == 0:
        return False
    for i in range(1, amount_of_problems + 1):
        if f"{i}_in.txt" not in problem_names or f"{i}_out.txt" not in problem_names:
            return False
    return True


def modify_problem_in_database(problem: ProblemDTO, form_data, problem_id: uuid.UUID):
    modified_fields = form_data.model_dump(exclude_none=True, exclude={"test_files"})
    modified_object = problem.model_copy(update=modified_fields)
    result = modify_problem_by_id(problem_id, modified_object)
    if not result:
        return False
    return True


def modify_problem_in_blob_storage(problem_id: uuid.UUID, form_data):
    delete_result = delete_all_blobs_by_problem_id(problem_id)
    if not delete_result:
        return False
    for test_file in form_data.test_files:
        data = test_file.file.read()
        upload_blob(f"{problem_id}/{test_file.filename}", data)
    return True