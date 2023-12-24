from typing import Union
import uuid

from bytepit_api.database import db
from bytepit_api.models.db_models import Problem
from bytepit_api.models.dtos import ProblemDTO, CreateProblemDTO


def get_problems_by_competition(competition_id: uuid.UUID):
    query_tuple = (
        """SELECT * FROM problems WHERE id IN (SELECT unnest(problems) FROM competitions WHERE id = %s);""",
        (competition_id,),
    )
    result = db.execute_one(query_tuple)
    if result["result"]:
        return [Problem(**problem) for problem in result["result"]]
    else:
        return []


def get_all_problems():
    query_tuple = ("SELECT * FROM problems", ())
    result = db.execute_one(query_tuple)
    if result["result"]:
        return [Problem(**problem) for problem in result["result"]]
    else:
        return None


def get_problem(problem_id: uuid.UUID):
    query_tuple = ("SELECT * FROM problems WHERE id = %s", (problem_id,))
    result = db.execute_one(query_tuple)
    if result["result"]:
        return Problem(**result["result"][0])
    else:
        return None


def delete_problem(problem_id: uuid.UUID):
    query_tuple = ("DELETE FROM problems WHERE id = %s", (problem_id,))
    result = db.execute_one(query_tuple)
    return result["affected_rows"] == 1


def insert_problem(problem: CreateProblemDTO, organiser_id: uuid.UUID):
    insert_query = (
        """
        INSERT INTO problems (name, example_input, example_output, is_hidden, num_of_points, runtime_limit, organiser_id, description, is_private)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
        """,
        (
            problem.name,
            problem.example_input,
            problem.example_output,
            problem.is_hidden,
            problem.num_of_points,
            problem.runtime_limit,
            organiser_id,
            problem.description,
            problem.is_private,
        ),
    )
    result = db.execute_one(insert_query)
    if result["affected_rows"] == 1:
        return result["result"][0]["id"]
    else:
        return False


def modify_problem(problem_id: uuid.UUID, problem: ProblemDTO):
    query_tuple = (
        """
        UPDATE problems
        SET name = %s, example_input = %s, example_output = %s, is_hidden = %s, num_of_points = %s, runtime_limit = %s, description = %s, is_private = %s
        WHERE id = %s
        """,
        (
            problem.name,
            problem.example_input,
            problem.example_output,
            problem.is_hidden,
            problem.num_of_points,
            problem.runtime_limit,
            problem.description,
            problem.is_private,
            problem_id,
        ),
    )
    result = db.execute_one(query_tuple)
    return result["affected_rows"] == 1


def insert_problem_result(
    problem_id: uuid.UUID,
    competition_id: Union[uuid.UUID, None],
    user_id: uuid.UUID,
    average_runtime: float,
    is_correct: bool,
    num_of_points: float,
    source_code: str,
    language: str,
):
    if competition_id:
        query_tuple = (
            """
            INSERT INTO problem_results (problem_id, competition_id, user_id, average_runtime, is_correct, num_of_points, source_code, language)
            VALUES (%(problem_id)s, %(competition_id)s, %(user_id)s, %(average_runtime)s, %(is_correct)s, %(num_of_points)s, %(source_code)s, %(language)s)
            ON CONFLICT (problem_id, competition_id, user_id) WHERE competition_id IS NOT NULL DO UPDATE
            SET average_runtime = %(average_runtime)s, is_correct = %(is_correct)s, num_of_points = %(num_of_points)s, source_code = %(source_code)s
            WHERE problem_results.num_of_points < %(num_of_points)s OR (problem_results.num_of_points = %(num_of_points)s AND problem_results.average_runtime > %(average_runtime)s)
            """,
            (
                {
                    "problem_id": problem_id,
                    "competition_id": competition_id,
                    "user_id": user_id,
                    "average_runtime": average_runtime,
                    "is_correct": is_correct,
                    "num_of_points": num_of_points,
                    "source_code": source_code,
                    "language": language,
                }
            ),
        )
    else:
        query_tuple = (
            """
            INSERT INTO problem_results (problem_id, user_id, average_runtime, is_correct, num_of_points, source_code, language)
            VALUES (%(problem_id)s, %(user_id)s, %(average_runtime)s, %(is_correct)s, %(num_of_points)s, %(source_code)s, %(language)s)
            ON CONFLICT (problem_id, user_id) WHERE competition_id IS NULL DO UPDATE
            SET average_runtime = %(average_runtime)s, is_correct = %(is_correct)s, num_of_points = %(num_of_points)s, source_code = %(source_code)s
            WHERE problem_results.num_of_points < %(num_of_points)s OR (problem_results.num_of_points = %(num_of_points)s AND problem_results.average_runtime > %(average_runtime)s)
            """,
            {
                "problem_id": problem_id,
                "user_id": user_id,
                "average_runtime": average_runtime,
                "is_correct": is_correct,
                "num_of_points": num_of_points,
                "source_code": source_code,
                "language": language,
            },
        )
    result = db.execute_one(query_tuple)
    return result["affected_rows"] == 1
