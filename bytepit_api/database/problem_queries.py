import uuid

from bytepit_api.database import db
from bytepit_api.models.dtos import ProblemDTO, CreateProblemDTO


def get_all_problems():
    query_tuple = ("SELECT * FROM problems", ())
    result = db.execute_one(query_tuple)
    if result["result"]:
        return [ProblemDTO(**problem) for problem in result["result"]]
    else:
        return None


def get_problem(problem_id: uuid.UUID):
    query_tuple = ("SELECT * FROM problems WHERE id = %s", (problem_id,))
    result = db.execute_one(query_tuple)
    if result["result"]:
        return ProblemDTO(**result["result"][0])
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
        (problem.name, problem.example_input, problem.example_output, problem.is_hidden, problem.num_of_points, problem.runtime_limit, organiser_id, problem.description, problem.is_private,)
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
        (problem.name, problem.example_input, problem.example_output, problem.is_hidden, problem.num_of_points, problem.runtime_limit, problem.description, problem.is_private, problem_id,),
    )
    result = db.execute_one(query_tuple)
    return result["affected_rows"] == 1