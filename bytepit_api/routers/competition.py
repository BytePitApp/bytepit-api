import uuid
from fastapi import APIRouter, Depends
from typing import Annotated, List

import bytepit_api.services.competition_service as competition_service

from bytepit_api.dependencies.auth_dependencies import get_current_approved_organiser, get_current_verified_user
from bytepit_api.models.dtos import CompetitionDTO, CreateCompetitionDTO, ModifyCompetitionDTO, TrophiesByUserDTO
from bytepit_api.models.db_models import User


router = APIRouter(prefix="/competitions", tags=["competitions"])


@router.get("/trophies-by-user/{user_id}", response_model=List[TrophiesByUserDTO])
def get_trophies_by_user(user_id: uuid.UUID, current_user: Annotated[User, Depends(get_current_verified_user)]):
    return competition_service.get_trophies_by_user(user_id)


@router.post("")
async def create_competition(
    form_data: Annotated[CreateCompetitionDTO, Depends()],
    current_user: Annotated[User, Depends(get_current_approved_organiser)],
):
    return competition_service.create_competition(form_data, current_user.id)


@router.get("", response_model=List[CompetitionDTO])
async def get_all_competitions(current_user: Annotated[User, Depends(get_current_verified_user)]):
    return competition_service.get_all_competitions()


@router.get("/active", response_model=List[CompetitionDTO])
async def get_active_competitions(current_user: Annotated[User, Depends(get_current_verified_user)]):
    return competition_service.get_active_competitions()


@router.get("/random", response_model=List[CompetitionDTO])
async def get_random_competition(current_user: Annotated[User, Depends(get_current_verified_user)]):
    return competition_service.get_random_competition()


@router.get("/{competition_id}", response_model=CompetitionDTO)
async def get_competition(competition_id: uuid.UUID, current_user: Annotated[User, Depends(get_current_verified_user)]):
    return competition_service.get_competition(competition_id)


@router.post("/{competition_id}/trophy/{user_id}")
async def set_trophy_to_user(
    competition_id: uuid.UUID,
    user_id: uuid.UUID,
    position: int,
    current_user: Annotated[User, Depends(get_current_verified_user)],
):
    return competition_service.set_trophy_to_user(competition_id, user_id, position)


@router.patch("/{competition_id}")
async def modify_competition(
    competition_id: uuid.UUID,
    form_data: Annotated[ModifyCompetitionDTO, Depends()],
    current_user: Annotated[User, Depends(get_current_approved_organiser)],
):
    return competition_service.modify_competition(competition_id, form_data)


@router.delete("/{competition_id}")
async def delete_competition(
    competition_id: uuid.UUID, current_user: Annotated[User, Depends(get_current_approved_organiser)]
):
    return competition_service.delete_competition(competition_id)


@router.get("/{competition_id}/results")
async def get_competition_results(
    competition_id: uuid.UUID, current_user: Annotated[User, Depends(get_current_verified_user)]
):
    return competition_service.get_competition_results(competition_id)


# DONE TODO: rang lista po ostvarenom broju bodova za određeno natjecanje ILI problem_id ako nije natjecanje
# SELECT * FROM problem_results
# WHERE competition_id = 'competition_id'
# GROUP BY user_id
# ORDER BY SUM(num_of_points) DESC


# [
#     {
#         "user_id": "Marko",
#         "total_points": 10,
#         "problems": [
#             {"problem_id": 2, "num_of_points": 10, "source_code": 3},
#             {"problem_id": 2, "num_of_points": 10, "source_code": 3},
#             {"problem_id": 2, "num_of_points": 10, "source_code": 3},
#         ],
#     },
#     {
#         "user_id": "Gana",
#         "total_points": 10,
#         "problems": [
#             {"problem_id": 2, "num_of_points": 10, "source_code": 3},
#             {"problem_id": 2, "num_of_points": 10, "source_code": 3},
#             {"problem_id": 2, "num_of_points": 10, "source_code": 3},
#         ],
#     },
# ]


# DONE TODO: izračunavanje trofeja na profilu korisnika
# """
# WITH total_points AS (
#   SELECT
#     competition_id,
#     user_id,
#     SUM(num_of_points) as total_points
#   FROM
#     problem_results
#   GROUP BY
#     competition_id,
#     user_id
# ),
# top_3_in_each_competition AS (
#   SELECT
#     competition_id,
#     user_id,
#     total_points,
#     ROW_NUMBER() OVER(
#       PARTITION BY competition_id
#       ORDER BY
#         total_points DESC
#     ) as rn
#   FROM
#     total_points
# )
# SELECT
#   top_3_in_each_competition.competition_id,
#   top_3_in_each_competition.user_id,
#   top_3_in_each_competition.rn AS rank_in_competition,
#   trophies.icon
# FROM
#   top_3_in_each_competition
#   LEFT JOIN trophies ON top_3_in_each_competition.competition_id = trophies.competition_id
#   AND rn = position
# WHERE
#   rn <= 3
#   AND top_3_in_each_competition.competition_id IS NOT NULL
#   AND top_3_in_each_competition.user_id = '58a6fe1b-d110-4821-bd04-db60a7b3fd27'
# ORDER BY
#   total_points DESC;
# """


# TODO: ukupan broj zadataka koje je korisnik pokušao riješiti / uspio riješiti

# TODO: get competition by organiser

# TODO: get problems by organiser
