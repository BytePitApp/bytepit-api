import uuid
from fastapi import status, HTTPException

import bytepit_api.database.organiser_queries as organiser_queries
import bytepit_api.helpers.competition_helpers as competition_helpers


def get_all_competitions_by_organiser_id(organiser_id: uuid.UUID):
    competitions_dict = organiser_queries.get_competitions_by_organiser_id(organiser_id)
    if not competitions_dict:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No competition with organiser id {organiser_id} found",
        )
    competitions = []
    for competition in competitions_dict:
        trophies = organiser_queries.get_trophies_by_ids(competition["trophies"])
        competitions.append(competition_helpers.map_competition_dict_to_dto(competition, trophies))
    return competitions


def get_problems_by_organiser_id(organiser_id: uuid.UUID):
    problems = organiser_queries.get_organisers_problems(organiser_id)
    if problems is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No problems with organiser id {organiser_id} found"
        )
    return problems
