import uuid

from bytepit_api.database.queries import delete_problem
from bytepit_api.helpers.blob_storage_helpers import delete_all_blobs_by_id
from typing import Union


def problem_delete(problemId: Union[int, uuid.UUID]):
    result = delete_problem(problemId)
    if not result:
        return None
    result = delete_all_blobs_by_id(problemId)
    if not result:
        return None
    return True
