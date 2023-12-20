import uuid

from fastapi import status, HTTPException

from bytepit_api.database import competition_queries, organiser_queries, problem_queries
from bytepit_api.models.dtos import CompetitionDTO, ProblemDTO, TrophyDTO


def get_competitions_by_organiser(organiser_id: uuid.UUID):
    competitions = organiser_queries.get_competitions_by_organiser(organiser_id)
    if not competitions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No competition with organiser id {organiser_id} found",
        )
    competition_dtos = []
    for competition in competitions:
        problems = problem_queries.get_problems_by_competition(competition.id)
        trophies = competition_queries.get_trophies_by_competition(competition.id)
        competition_dict = competition.model_dump(exclude={"problems"})
        competition_dto = CompetitionDTO(**competition_dict)
        competition_dto.problems = [ProblemDTO(**problem.model_dump()) for problem in problems]
        competition_dto.trophies = [TrophyDTO(**trophy.model_dump()) for trophy in trophies]
        competition_dtos.append(competition_dto)
    return competition_dtos


def get_problems_by_organiser(organiser_id: uuid.UUID):
    problems = organiser_queries.get_problems_by_organiser(organiser_id)
    if problems is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"No problems with organiser id {organiser_id} found"
        )
    return problems
