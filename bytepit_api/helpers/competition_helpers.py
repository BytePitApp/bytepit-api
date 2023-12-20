from fastapi import UploadFile
from typing import Union

from bytepit_api.models.dtos import CompetitionDTO, ProblemDTO


def validate_trophies(
    first_place_trophy: Union[UploadFile, None] = None,
    second_place_trophy: Union[UploadFile, None] = None,
    third_place_trophy: Union[UploadFile, None] = None,
):
    if first_place_trophy is None and (second_place_trophy is not None or third_place_trophy is not None):
        return False
    if second_place_trophy is None and third_place_trophy is not None:
        return False
    return True
