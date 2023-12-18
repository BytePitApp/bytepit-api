import uuid

from fastapi import status, HTTPException, Response

from bytepit_api.models.dtos import CreateCompetitionDTO, ModifyCompetitionDTO
from bytepit_api.database.queries import insert_competition, get_problems_by_ids, insert_trophy, get_all_competitions, get_all_active_competitions, get_random_competition, get_competition_by_id, set_user_trophy, modify_competition_by_id, delete_trophy_by_competition_id, delete_competition_by_id, get_competition_by_id_without_trophies, get_trophies_by_ids
from bytepit_api.helpers.competition_helpers import validate_trophies, map_competition_dict_to_dto


def get_every_competition():
    competitions_dict = get_all_competitions()
    competitions = []
    for competition in competitions_dict:
        trophies = get_trophies_by_ids(competition["trophies"])
        competitions.append(map_competition_dict_to_dto(competition, trophies))
    return competitions


def get_every_active_competition():
    competitions_dict = get_all_active_competitions()
    competitions = []
    for competition in competitions_dict:
        trophies = get_trophies_by_ids(competition["trophies"])
        competitions.append(map_competition_dict_to_dto(competition, trophies))
    return competitions


def get_one_random_competition():
    competition_dict = get_random_competition()
    trophies = get_trophies_by_ids(competition_dict["trophies"])
    return map_competition_dict_to_dto(competition_dict, trophies)


def get_one_competition(competition_id: uuid.UUID):
    competition_dict = get_competition_by_id(competition_id)
    if not competition_dict:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No competition found",
        )
    trophies = get_trophies_by_ids(competition_dict["trophies"])
    return map_competition_dict_to_dto(competition_dict, trophies)


def create_competition(form_data: CreateCompetitionDTO, current_user: uuid.UUID):
    problems = get_problems_by_ids(form_data.problems)
    if len(problems) != len(form_data.problems):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid problems",
        )
    if not validate_trophies(form_data.first_place_trophy, form_data.second_place_trophy, form_data.third_place_trophy):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid trophies",
        )
    result = insert_competition(
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
    insert_trophy(result, 1, form_data.first_place_trophy)
    insert_trophy(result, 2, form_data.second_place_trophy)
    insert_trophy(result, 3, form_data.third_place_trophy)
    return Response(status_code=status.HTTP_201_CREATED)


def set_trophy_to_user(competition_id: uuid.UUID, user_id: uuid.UUID, position: int):
    result = set_user_trophy(competition_id, user_id, position)
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
        problems = get_problems_by_ids(form_data.problems)
        if len(problems) != len(form_data.problems):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid problems",
            )
    competition_to_modify = get_competition_by_id_without_trophies(competition_id)
    if not competition_to_modify:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Competition not found",
        )
    modified_fields = form_data.model_dump(exclude_none=True, exclude={"first_place_trophy", "second_place_trophy", "third_place_trophy"})
    modified_object = competition_to_modify.model_copy(update=modified_fields)
    if not modify_competition_by_id(competition_id, modified_object):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong. Please try again.",
        )
    if form_data.first_place_trophy is not None or form_data.second_place_trophy is not None or form_data.third_place_trophy is not None:
        if not validate_trophies(form_data.first_place_trophy, form_data.second_place_trophy, form_data.third_place_trophy):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid trophies",
            )
        delete_trophy_by_competition_id(competition_id)
        insert_trophy(competition_id, 1, form_data.first_place_trophy)
        insert_trophy(competition_id, 2, form_data.second_place_trophy)
        insert_trophy(competition_id, 3, form_data.third_place_trophy)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def delete_competition(competition_id: uuid.UUID):
    result = delete_trophy_by_competition_id(competition_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong. Please try again.",
        )
    result = delete_competition_by_id(competition_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong. Please try again.",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
