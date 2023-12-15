import uuid
import re

from bytepit_api.database.queries import delete_problem_by_problem_id
from bytepit_api.helpers.blob_storage_helpers import delete_all_blobs_by_problem_id
from typing import Union, List
from fastapi import UploadFile


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
    for i in range(1, amount_of_problems + 1):
        if f"{i}_in.txt" not in problem_names or f"{i}_out.txt" not in problem_names:
            return False
    return True