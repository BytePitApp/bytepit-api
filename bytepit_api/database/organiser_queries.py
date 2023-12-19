import uuid
from typing import List

from bytepit_api.database import db
from bytepit_api.models.dtos import ProblemDTO, TrophyDTO


def get_organisers_problems(organiser_id: uuid.UUID):
    query_tuple = ("SELECT * FROM problems WHERE organiser_id = %s", (organiser_id,))
    result = db.execute_one(query_tuple)
    if result["result"]:
        return [ProblemDTO(**problem) for problem in result["result"]]
    else:
        return None


def get_competitions_by_organiser_id(organiser_id: uuid.UUID):
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
            c.organiser_id = %s
        GROUP BY
            c.id
        """, (organiser_id,))
    result = db.execute_one(query_tuple)
    if result["result"]:
        return result["result"]
    else:
        return None

