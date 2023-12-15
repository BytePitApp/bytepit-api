import uuid

from bytepit_api.database import db
from bytepit_api.models.db_models import User
from bytepit_api.models.dtos import UserDTO, ProblemDTO
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
