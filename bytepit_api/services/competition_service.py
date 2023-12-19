import uuid
from fastapi import status, HTTPException, Response

import bytepit_api.database.competition_queries as competition_queries
import bytepit_api.database.trophies_queries as trophies_queries
import bytepit_api.helpers.competition_helpers as competition_helpers

from bytepit_api.models.dtos import CreateCompetitionDTO, ModifyCompetitionDTO


def get_all_competitions():
    competitions_dict = competition_queries.get_competitions()
    competitions = []
    for competition in competitions_dict:
        trophies = trophies_queries.get_trophies_by_ids(competition["trophies"])
        competitions.append(competition_helpers.map_competition_dict_to_dto(competition, trophies))
    return competitions


def get_every_active_competition():
    competitions_dict = competition_queries.get_active_competitions()
    competitions = []
    for competition in competitions_dict:
        trophies = trophies_queries.get_trophies_by_ids(competition["trophies"])
        competitions.append(competition_helpers.map_competition_dict_to_dto(competition, trophies))
    return competitions


def get_one_random_competition():
    competition_dict = competition_queries.get_random_competition()
    trophies = trophies_queries.get_trophies_by_ids(competition_dict["trophies"])
    return competition_helpers.map_competition_dict_to_dto(competition_dict, trophies)


def get_one_competition(competition_id: uuid.UUID):
    competition_dict = competition_queries.get_competition(competition_id)
    if not competition_dict:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No competition found",
        )
    trophies = trophies_queries.get_trophies_by_ids(competition_dict["trophies"])
    return competition_helpers.map_competition_dict_to_dto(competition_dict, trophies)


def create_competition(form_data: CreateCompetitionDTO, current_user: uuid.UUID):
    problems = competition_queries.get_problems(form_data.problems)
    if len(problems) != len(form_data.problems):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid problems",
        )
    if not competition_helpers.validate_trophies(form_data.first_place_trophy, form_data.second_place_trophy, form_data.third_place_trophy):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid trophies",
        )
    result = competition_queries.insert_competition(
        form_data.name,
        form_data.description,
        form_data.start_time,
        form_data.end_time,
        form_data.problems,
        current_user,
        form_data.parent_id,
    )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong. Please try again.",
        )
    trophies_queries.insert_trophy(result, 1, form_data.first_place_trophy)
    trophies_queries.insert_trophy(result, 2, form_data.second_place_trophy)
    trophies_queries.insert_trophy(result, 3, form_data.third_place_trophy)
    return Response(status_code=status.HTTP_201_CREATED)


def set_trophy_to_user(competition_id: uuid.UUID, user_id: uuid.UUID, position: int):
    result = competition_queries.set_user_trophy(competition_id, user_id, position)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong. Please try again.",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def modify_competition(competition_id: uuid.UUID, form_data: ModifyCompetitionDTO):
    if form_data.problems == []:
        form_data.problems = None
    else:
        problems = competition_queries.get_problems(form_data.problems)
        if len(problems) != len(form_data.problems):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid problems",
            )
    competition_to_modify = competition_queries.get_competition_without_trophies(competition_id)
    if not competition_to_modify:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Competition not found",
        )
    modified_fields = form_data.model_dump(exclude_none=True, exclude={"first_place_trophy", "second_place_trophy", "third_place_trophy"})
    modified_object = competition_to_modify.model_copy(update=modified_fields)
    if not competition_queries.modify_competition(competition_id, modified_object):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong. Please try again.",
        )
    if form_data.first_place_trophy is not None or form_data.second_place_trophy is not None or form_data.third_place_trophy is not None:
        if not competition_helpers.validate_trophies(form_data.first_place_trophy, form_data.second_place_trophy, form_data.third_place_trophy):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid trophies",
            )
        trophies_queries.delete_trophy_by_competition_id(competition_id)
        trophies_queries.insert_trophy(competition_id, 1, form_data.first_place_trophy)
        trophies_queries.insert_trophy(competition_id, 2, form_data.second_place_trophy)
        trophies_queries.insert_trophy(competition_id, 3, form_data.third_place_trophy)
    return Response(status_code=status.HTTP_200_OK)


def delete_competition(competition_id: uuid.UUID):
    result = competition_queries.delete_competition(competition_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No competition with id {competition_id} found",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
