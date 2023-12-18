import uuid

from typing import List, Union

from bytepit_api.database import db
from bytepit_api.models.db_models import User
from bytepit_api.models.dtos import UserDTO, ProblemDTO, CompetitionDTO, TrophyDTO
from bytepit_api.models.enums import RegisterRole

def get_user_by_username(username: str):
    query_tuple = ("SELECT * FROM users WHERE username = %s", (username,))
    result = db.execute_one(query_tuple)
    if result["result"]:
        return User(**result["result"][0])
    else:
        return None


def get_user_by_email(email: str):
    query_tuple = ("SELECT * FROM users WHERE email = %s", (email,))
    result = db.execute_one(query_tuple)
    if result["result"]:
        return User(**result["result"][0])
    else:
        return None


def get_user_by_id(user_id: uuid.UUID):
    query_tuple = ("SELECT * FROM users WHERE id = %s", (user_id,))
    result = db.execute_one(query_tuple)

    if result["result"]:
        return User(**result["result"][0])
    else:
        return None


def create_user(username, password_hash, name, surname, email, role, image, confirmation_token):
    approved_by_admin = False if role == "organiser" else True
    image_binary = image.file.read() if image else None

    user_insert_query = (
        """
        INSERT INTO users (username, password_hash, name, surname, email, role, image, is_verified, approved_by_admin)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (username, password_hash, name, surname, email, role, image_binary, False, approved_by_admin),
    )

    token_insert_query = (
        "INSERT INTO verification_tokens (token, email) " "VALUES (%s, %s)",
        (confirmation_token, email),
    )
    result = db.execute_many([user_insert_query, token_insert_query])
    return result["affected_rows"] == 2


def get_users():
    query_tuple = ("SELECT * FROM users", ())
    result = db.execute_one(query_tuple)
    return [UserDTO(**user) for user in result["result"]]


def get_unverified_organisers():
    query_tuple = ("SELECT * FROM users WHERE role = 'organiser' AND approved_by_admin = false", ())
    result = db.execute_one(query_tuple)
    return [UserDTO(**user) for user in result["result"]]


def set_verified_user(user_id: uuid.UUID):
    query_tuple = (
        """
        UPDATE users
        SET is_verified = TRUE
        WHERE id = %s
        """,
        (user_id,),
    )
    result = db.execute_one(query_tuple)
    return result["affected_rows"] == 1


def get_user_by_verification_token(verification_token: str):
    query_tuple = (
        """
        SELECT * FROM verification_tokens
        JOIN users
        ON verification_tokens.email = users.email
        WHERE token = %s AND expiry_date > NOW()
        """,
        (verification_token,),
    )
    result = db.execute_one(query_tuple)
    if result["result"]:
        return User(**result["result"][0])
    else:
        return None


def set_user_role(username: str, new_role: RegisterRole):
    approved_by_admin = False if new_role == RegisterRole.organiser else True
    query_tuple = (
        "UPDATE users SET role = %s, approved_by_admin = %s WHERE username = %s",
        (new_role, approved_by_admin, username),
    )
    result = db.execute_one(query_tuple)
    return result["affected_rows"] == 1


def set_approved_organiser(username: str):
    query_tuple = ("UPDATE users SET approved_by_admin = true WHERE username = %s", (username,))
    result = db.execute_one(query_tuple)
    return result["affected_rows"] == 1


def get_all_problems():
    query_tuple = ("SELECT * FROM problems", ())
    result = db.execute_one(query_tuple)
    return [ProblemDTO(**problem) for problem in result["result"]]


def get_problem_by_id(problem_id: uuid.UUID):
    query_tuple = ("SELECT * FROM problems WHERE id = %s", (problem_id,))
    result = db.execute_one(query_tuple)
    if result["result"]:
        return ProblemDTO(**result["result"][0])
    else:
        return None
    

def insert_problem(name: str, example_input: str, example_output: str, is_hidden: bool, num_of_points: float, runtime_limit: str, organiser_id: uuid.UUID, description: str, is_private: bool):
    problem_insert_query = (
        """
        INSERT INTO problems (name, example_input, example_output, is_hidden, num_of_points, runtime_limit, organiser_id, description, is_private)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
        """,
        (name, example_input, example_output, is_hidden, num_of_points, runtime_limit, organiser_id, description, is_private),
    )
    result = db.execute_one(problem_insert_query)
    if result["affected_rows"] == 1:
        return result["result"][0]["id"]
    else:
        return result["affected_rows"] == 1


def delete_problem_by_problem_id(problem_id: uuid.UUID):
    query_tuple = ("DELETE FROM problems WHERE id = %s", (problem_id,))
    result = db.execute_one(query_tuple)
    return result["affected_rows"] == 1


def get_organisers_problems(organiser_id: uuid.UUID):
    query_tuple = ("SELECT * FROM problems WHERE organiser_id = %s", (organiser_id,))
    result = db.execute_one(query_tuple)
    if result["result"]:
        return [ProblemDTO(**problem) for problem in result["result"]]
    else:
        return None


def modify_problem_by_id(problem_id: uuid.UUID, problem: ProblemDTO):
    query_tuple = (
        """
        UPDATE problems
        SET name = %s, example_input = %s, example_output = %s, is_hidden = %s, num_of_points = %s, runtime_limit = %s, description = %s, is_private = %s
        WHERE id = %s
        """,
        (problem.name, problem.example_input, problem.example_output, problem.is_hidden, problem.num_of_points, problem.runtime_limit, problem.description, problem.is_private, problem_id),
    )
    result = db.execute_one(query_tuple)
    return result["affected_rows"] == 1


def get_problems_by_ids(problem_ids: List[uuid.UUID]):
    query_tuple = (f"SELECT * FROM problems WHERE id IN ({', '.join(['%s']*len(problem_ids))});", tuple(problem_ids))   
    result = db.execute_one(query_tuple)
    if result["result"]:
        return [ProblemDTO(**problem) for problem in result["result"]]
    else:
        return []
    

def get_all_competitions():
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
    return result["result"]


def get_all_active_competitions():
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


def get_competition_by_id(competition_id: uuid.UUID):
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
    

def get_competition_by_id_without_trophies(competition_id: uuid.UUID):
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


def get_every_competition_by_organiser_id(organiser_id: uuid.UUID):
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


def insert_trophy(competition_id: uuid.UUID, position: int, icon):
    icon_binary = icon.file.read() if icon else None
    if not icon:
        return False
    trophy_insert_query = (
        """
        INSERT INTO trophies (competition_id, position, icon)
        VALUES (%s, %s, %s)
        """,
        (competition_id, position, icon_binary),
    )
    result = db.execute_one(trophy_insert_query)
    return result["affected_rows"] == 1


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


def modify_competition_by_id(competition_id: uuid.UUID, competition: CompetitionDTO):
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


def delete_trophy_by_competition_id(competition_id: uuid.UUID):
    query_tuple = ("DELETE FROM trophies WHERE competition_id = %s", (competition_id,))
    result = db.execute_one(query_tuple)
    return result["affected_rows"] == 1


def delete_competition_by_id(competition_id: uuid.UUID):
    query_tuple = ("DELETE FROM competition WHERE id = %s", (competition_id,))
    result = db.execute_one(query_tuple)
    return result["affected_rows"] == 1


def get_trophies_by_ids(trophy_ids: List[uuid.UUID]):
    query_tuple = (f"SELECT * FROM trophies WHERE id IN ({', '.join(['%s']*len(trophy_ids))});", tuple(trophy_ids))   
    result = db.execute_one(query_tuple)
    if result["result"]:
        return [TrophyDTO(**trophy) for trophy in result["result"]]
    else:
        return []
