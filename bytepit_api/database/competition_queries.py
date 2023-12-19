import uuid
from typing import List, Union
from bytepit_api.database import db
from bytepit_api.models.dtos import ProblemDTO, CompetitionDTO, TrophyDTO


def get_competitions():
    query_tuple = (
        """
        SELECT
            c.id AS competition_id,
            c.name AS competition_name,
            c.description AS competition_description,
            c.start_time AS competition_start_time,
            c.end_time AS competition_end_time,
            c.parent_id AS competition_parent_id,   
            c.organiser_id AS competition_organiser_id,
            jsonb_agg(DISTINCT jsonb_build_object(
                'problem_id', p.id,
                'problem_name', p.name,
                'problem_example_input', p.example_input,
                'problem_example_output', p.example_output,
                'problem_is_hidden', p.is_hidden,
                'problem_num_of_points', p.num_of_points,
                'problem_runtime_limit', p.runtime_limit,
                'problem_description', p.description,
                'problem_organiser_id', p.organiser_id,
                'problem_is_private', p.is_private,
                'problem_created_on', p.created_on
            )) AS problems,
            array_agg(DISTINCT t.id) AS trophies
        FROM
            competition c
        LEFT JOIN
            problems p ON p.id = ANY(c.problems)
        LEFT JOIN
            trophies t ON t.competition_id = c.id
        GROUP BY
            c.id
        """, ())
    result = db.execute_one(query_tuple)
    if result["result"]:
        return result["result"]
    else:
        return None


def insert_competition(name: str, description: str, start_time: str, end_time: str, problems: List[uuid.UUID], organiser_id: uuid.UUID, parent_id: Union[uuid.UUID, None] = None):
    problems_array = "{" + ",".join(map(str, problems)) + "}" if problems else None    
    competition_insert_query = (
        """
        INSERT INTO competition (name, description, start_time, end_time, parent_id, organiser_id, problems)
        VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id
        """,
        (name, description, start_time, end_time, parent_id, organiser_id, problems_array),
    )
    result = db.execute_one(competition_insert_query)
    if result["affected_rows"] == 1:
        return result["result"][0]["id"]
    else:
        return None


def get_problems(problem_ids: List[uuid.UUID]):
    query_tuple = (f"SELECT * FROM problems WHERE id IN ({', '.join(['%s']*len(problem_ids))});", tuple(problem_ids))   
    result = db.execute_one(query_tuple)
    if result["result"]:
        return [ProblemDTO(**problem) for problem in result["result"]]
    else:
        return []


def get_active_competitions():
    query_tuple = (
        """
        SELECT
            c.id AS competition_id,
            c.name AS competition_name,
            c.description AS competition_description,
            c.start_time AS competition_start_time,
            c.end_time AS competition_end_time,
            c.parent_id AS competition_parent_id,
            c.organiser_id AS competition_organiser_id,
            jsonb_agg(DISTINCT jsonb_build_object(
                'problem_id', p.id,
                'problem_name', p.name,
                'problem_example_input', p.example_input,
                'problem_example_output', p.example_output,
                'problem_is_hidden', p.is_hidden,
                'problem_num_of_points', p.num_of_points,
                'problem_runtime_limit', p.runtime_limit,
                'problem_description', p.description,
                'problem_organiser_id', p.organiser_id,
                'problem_is_private', p.is_private,
                'problem_created_on', p.created_on
            )) AS problems,
            array_agg(DISTINCT t.id) AS trophies
        FROM
            competition c
        LEFT JOIN
            problems p ON p.id = ANY(c.problems)
        LEFT JOIN
            trophies t ON t.competition_id = c.id
        WHERE
            c.start_time <= NOW() AND c.end_time >= NOW()
        GROUP BY
            c.id
        """, ())
    result = db.execute_one(query_tuple)
    return result["result"]


def get_random_competition():
    query_tuple = (
        """
        SELECT
            c.id AS competition_id,
            c.name AS competition_name,
            c.description AS competition_description,
            c.start_time AS competition_start_time,
            c.end_time AS competition_end_time,
            c.parent_id AS competition_parent_id,
            c.organiser_id AS competition_organiser_id,
            jsonb_agg(DISTINCT jsonb_build_object(
                'problem_id', p.id,
                'problem_name', p.name,
                'problem_example_input', p.example_input,
                'problem_example_output', p.example_output,
                'problem_is_hidden', p.is_hidden,
                'problem_num_of_points', p.num_of_points,
                'problem_runtime_limit', p.runtime_limit,
                'problem_description', p.description,
                'problem_organiser_id', p.organiser_id,
                'problem_is_private', p.is_private,
                'problem_created_on', p.created_on
            )) AS problems,
            array_agg(DISTINCT t.id) AS trophies
        FROM
            competition c
        LEFT JOIN
            problems p ON p.id = ANY(c.problems)
        LEFT JOIN
            trophies t ON t.competition_id = c.id
        GROUP BY
            c.id
        ORDER BY
            RANDOM()
        LIMIT 1
        """, ())
    result = db.execute_one(query_tuple)
    if result["result"]:
        return result["result"][0]
    else:
        return None


def get_competition(competition_id: uuid.UUID):
    query_tuple = (
        """
        SELECT
            c.id AS competition_id,
            c.name AS competition_name,
            c.description AS competition_description,
            c.start_time AS competition_start_time,
            c.end_time AS competition_end_time,
            c.parent_id AS competition_parent_id,
            c.organiser_id AS competition_organiser_id,
            jsonb_agg(DISTINCT jsonb_build_object(
                'problem_id', p.id,
                'problem_name', p.name,
                'problem_example_input', p.example_input,
                'problem_example_output', p.example_output,
                'problem_is_hidden', p.is_hidden,
                'problem_num_of_points', p.num_of_points,
                'problem_runtime_limit', p.runtime_limit,
                'problem_description', p.description,
                'problem_organiser_id', p.organiser_id,
                'problem_is_private', p.is_private,
                'problem_created_on', p.created_on
            )) AS problems,
            array_agg(DISTINCT t.id) AS trophies
        FROM
            competition c
        LEFT JOIN
            problems p ON p.id = ANY(c.problems)
        LEFT JOIN
            trophies t ON t.competition_id = c.id
        WHERE
            c.id = %s
        GROUP BY
            c.id
        """, (competition_id,))
    result = db.execute_one(query_tuple)
    if result["result"]:
        return result["result"][0]
    else:
        return None


def set_user_trophy(competition_id: uuid.UUID, user_id: uuid.UUID, position: int):
    query_tuple = (
        """
        UPDATE trophies
        SET user_id = %s
        WHERE competition_id = %s AND position = %s
        """,
        (user_id, competition_id, position),
    )
    result = db.execute_one(query_tuple)
    return result["affected_rows"] == 1


def modify_competition(competition_id: uuid.UUID, competition: CompetitionDTO):
    query_tuple = (
        """
        UPDATE competition
        SET name = %s, description = %s, start_time = %s, end_time = %s, parent_id = %s, organiser_id = %s, problems = %s
        WHERE id = %s
        """,
        (competition.name, competition.description, competition.start_time, competition.end_time, competition.parent_id, competition.organiser_id, competition.problems, competition_id),
    )
    result = db.execute_one(query_tuple)
    return result["affected_rows"] == 1


def delete_competition(competition_id: uuid.UUID):
    query_tuple = ("DELETE FROM competition WHERE id = %s", (competition_id,))
    result = db.execute_one(query_tuple)
    return result["affected_rows"] == 1


def get_competition_without_trophies(competition_id: uuid.UUID):
    query_tuple = (
        """
        SELECT
            c.id AS id,
            c.name AS name,
            c.description AS description,
            c.start_time AS start_time,
            c.end_time AS end_time,
            c.parent_id AS parent_id,
            c.organiser_id AS organiser_id,
            c.problems AS problems
        FROM
            competition c
        WHERE
            c.id = %s
        GROUP BY
            c.id
        """, (competition_id,))
    result = db.execute_one(query_tuple)
    if result["result"]:
        return CompetitionDTO(**result["result"][0])
    else:
        return None
