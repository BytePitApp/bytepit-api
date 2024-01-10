import datetime
import uuid
from fastapi import status, HTTPException, Response

from bytepit_api.database import competition_queries, problem_queries
import bytepit_api.helpers.competition_helpers as competition_helpers

from bytepit_api.models.dtos import CompetitionDTO, CreateCompetitionDTO, ModifyCompetitionDTO, ProblemDTO, TrophyDTO


def get_all_competitions():
    competitions = competition_queries.get_competitions()
    competitions_dtos = []
    for competition in competitions:
        problems = problem_queries.get_problems_by_competition(competition.id)
        trophies = competition_queries.get_trophies_by_competition(competition.id)

        competition_dict = competition.model_dump(exclude={"problems"})
        competition_dto = CompetitionDTO(**competition_dict)
        competition_dto.problems = [ProblemDTO(**problem.model_dump()) for problem in problems]
        competition_dto.trophies = [TrophyDTO(**trophy.model_dump()) for trophy in trophies]
        competitions_dtos.append(competition_dto)

    return competitions_dtos


def get_virtual_competitions():
    competitions = competition_queries.get_virtual_competitions()
    competitions_dtos = []
    for competition in competitions:
        problems = problem_queries.get_problems_by_competition(competition.id)
        trophies = competition_queries.get_trophies_by_competition(competition.parent_id)

        competition_dict = competition.model_dump(exclude={"problems"})
        competition_dto = CompetitionDTO(**competition_dict)
        competition_dto.problems = [ProblemDTO(**problem.model_dump()) for problem in problems]
        competition_dto.trophies = [TrophyDTO(**trophy.model_dump()) for trophy in trophies]
        competitions_dtos.append(competition_dto)

    return competitions_dtos


def get_active_competitions():
    competitions = competition_queries.get_active_competitions()
    competitions_dtos = []
    for competition in competitions:
        problems = problem_queries.get_problems_by_competition(competition.id)
        trophies = competition_queries.get_trophies_by_competition(competition.id)

        competition_dict = competition.model_dump(exclude={"problems"})
        competition_dto = CompetitionDTO(**competition_dict)
        competition_dto.problems = [ProblemDTO(**problem.model_dump()) for problem in problems]
        competition_dto.trophies = [TrophyDTO(**trophy.model_dump()) for trophy in trophies]
        competitions_dtos.append(competition_dto)

    return competitions_dtos


def get_random_competition():
    competition = competition_queries.get_random_competition()
    if not competition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No competitions found",
        )
    problems = problem_queries.get_problems_by_competition(competition.id)
    trophies = competition_queries.get_trophies_by_competition(competition.id)

    competition_dict = competition.model_dump(exclude={"problems"})
    competition_dto = CompetitionDTO(**competition_dict)
    competition_dto.problems = [ProblemDTO(**problem.model_dump()) for problem in problems]
    competition_dto.trophies = [TrophyDTO(**trophy.model_dump()) for trophy in trophies]
    return competition_dto


def get_competition(competition_id: uuid.UUID):
    competition = competition_queries.get_competition(competition_id)
    if not competition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No competition with id {competition_id} found",
        )
    problems = problem_queries.get_problems_by_competition(competition.id)
    trophies = competition_queries.get_trophies_by_competition(competition.id)

    competition_dict = competition.model_dump(exclude={"problems"})
    competition_dto = CompetitionDTO(**competition_dict)
    competition_dto.problems = [ProblemDTO(**problem.model_dump()) for problem in problems]
    competition_dto.trophies = [TrophyDTO(**trophy.model_dump()) for trophy in trophies]
    return competition_dto


def get_virtual_competition(competition_id: uuid.UUID):
    competition = competition_queries.get_virtual_competition(competition_id)
    if not competition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No competition with id {competition_id} found",
        )
    problems = problem_queries.get_problems_by_competition(competition.id)
    trophies = competition_queries.get_trophies_by_competition(competition.parent_id)

    competition_dict = competition.model_dump(exclude={"problems"})
    competition_dto = CompetitionDTO(**competition_dict)
    competition_dto.problems = [ProblemDTO(**problem.model_dump()) for problem in problems]
    competition_dto.trophies = [TrophyDTO(**trophy.model_dump()) for trophy in trophies]
    return competition_dto


def create_competition(form_data: CreateCompetitionDTO, current_user: uuid.UUID):
    problems = competition_queries.get_problems(form_data.problems)
    if len(problems) != len(form_data.problems):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid problems",
        )
    if not competition_helpers.validate_trophies(
        form_data.first_place_trophy, form_data.second_place_trophy, form_data.third_place_trophy
    ):
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
    competition_queries.insert_trophy(result, 1, form_data.first_place_trophy)
    competition_queries.insert_trophy(result, 2, form_data.second_place_trophy)
    competition_queries.insert_trophy(result, 3, form_data.third_place_trophy)
    return Response(status_code=status.HTTP_201_CREATED)


def create_virtual_competition(parent_competition_id: uuid.UUID, current_user: uuid.UUID):
    competition = competition_queries.get_competition(parent_competition_id)
    if not competition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent competition not found",
        )
    problems = problem_queries.get_problems_by_competition(parent_competition_id)
    problem_ids = [problem.id for problem in problems]
    competition_duration = competition.end_time - competition.start_time
    competition_start_time = datetime.datetime.now()
    competition_end_time = competition_start_time + competition_duration

    result = competition_queries.insert_competition(
        competition.name,
        competition.description,
        competition_start_time,
        competition_end_time,
        problem_ids,
        current_user,
        parent_competition_id,
    )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong. Please try again.",
        )
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
    competition_to_modify = competition_queries.get_competition(competition_id)
    if not competition_to_modify:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Competition not found",
        )
    modified_fields = form_data.model_dump(
        exclude_none=True, exclude={"first_place_trophy", "second_place_trophy", "third_place_trophy"}
    )
    modified_object = competition_to_modify.model_copy(update=modified_fields)
    if not competition_queries.modify_competition(competition_id, modified_object):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong. Please try again.",
        )
    if (
        form_data.first_place_trophy is not None
        or form_data.second_place_trophy is not None
        or form_data.third_place_trophy is not None
    ):
        if not competition_helpers.validate_trophies(
            form_data.first_place_trophy, form_data.second_place_trophy, form_data.third_place_trophy
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid trophies",
            )
        competition_queries.delete_trophy_by_competition_id(competition_id)
        competition_queries.insert_trophy(competition_id, 1, form_data.first_place_trophy)
        competition_queries.insert_trophy(competition_id, 2, form_data.second_place_trophy)
        competition_queries.insert_trophy(competition_id, 3, form_data.third_place_trophy)
    return Response(status_code=status.HTTP_200_OK)


def delete_competition(competition_id: uuid.UUID):
    result = competition_queries.delete_competition(competition_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No competition with id {competition_id} found",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def get_competition_results(competition_id: uuid.UUID):
    competition = competition_queries.get_competition(competition_id)
    if not competition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No competition with id {competition_id} found",
        )
    results = competition_queries.get_competition_results(competition_id)
    return results


def get_virtual_competition_results(competition_id: uuid.UUID):
    competition = competition_queries.get_virtual_competition(competition_id)
    if not competition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No competition with id {competition_id} found",
        )
    results = competition_queries.get_competition_results(competition_id)
    return results


def get_competitions_by_organiser(organiser_id: uuid.UUID):
    competitions = competition_queries.get_competitions_by_organiser(organiser_id)
    competitions_dtos = []
    for competition in competitions:
        problems = problem_queries.get_problems_by_competition(competition.id)
        trophies = competition_queries.get_trophies_by_competition(competition.id)

        competition_dict = competition.model_dump(exclude={"problems"})
        competition_dto = CompetitionDTO(**competition_dict)
        competition_dto.problems = [ProblemDTO(**problem.model_dump()) for problem in problems]
        competition_dto.trophies = [TrophyDTO(**trophy.model_dump()) for trophy in trophies]
        competitions_dtos.append(competition_dto)

    return competitions_dtos
