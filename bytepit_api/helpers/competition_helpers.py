from fastapi import UploadFile
from typing import Union

from bytepit_api.models.dtos import CompetitionDTO, ProblemDTO, TrophyDTO


def validate_trophies(first_place_trophy: Union[UploadFile, None] = None, second_place_trophy: Union[UploadFile, None] = None, third_place_trophy: Union[UploadFile, None] = None):
    if first_place_trophy is None and (second_place_trophy is not None or third_place_trophy is not None):
        return False
    if second_place_trophy is None and third_place_trophy is not None:
        return False
    return True


def map_competition_dict_to_dto(competition_dict, trophies):
    problems = []
    for problem in competition_dict["problems"]:
        problems.append(
            ProblemDTO(
                id=problem["problem_id"],
                name=problem["problem_name"],
                example_input=problem["problem_example_input"],
                example_output=problem["problem_example_output"],
                is_hidden=problem["problem_is_hidden"],
                num_of_points=problem["problem_num_of_points"],
                runtime_limit=problem["problem_runtime_limit"],
                description=problem["problem_description"],
                organiser_id=problem["problem_organiser_id"],
                is_private=problem["problem_is_private"],
                created_on=problem["problem_created_on"],
            )
        )
    competition = CompetitionDTO(
        id=competition_dict["competition_id"],
        name=competition_dict["competition_name"],
        description=competition_dict["competition_description"],
        start_time=competition_dict["competition_start_time"],
        end_time=competition_dict["competition_end_time"],
        parent_id=competition_dict["competition_parent_id"],
        organiser_id=competition_dict["competition_organiser_id"],
        problems=problems,
        trophies=trophies,
    )
    return competition
