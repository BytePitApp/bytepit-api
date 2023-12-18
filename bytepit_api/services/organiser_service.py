import uuid

from fastapi import status, HTTPException

from bytepit_api.models.dtos import CompetitionDTO, CreateCompetitionDTO, ModifyCompetitionDTO
from bytepit_api.database.queries import get_every_competition_by_organiser_id, get_trophies_by_ids
from bytepit_api.helpers.competition_helpers import map_competition_dict_to_dto


def get_all_competitions_by_organiser_id(organiser_id: uuid.UUID):
    competitions_dict = get_every_competition_by_organiser_id(organiser_id)
    if not competitions_dict:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No competition found",
        )
    competitions = []
    for competition in competitions_dict:
        trophies = get_trophies_by_ids(competition["trophies"])
        competitions.append(map_competition_dict_to_dto(competition, trophies))
    return competitions
