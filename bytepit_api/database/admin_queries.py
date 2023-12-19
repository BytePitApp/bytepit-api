import uuid
from bytepit_api.models.dtos import UserDTO
from bytepit_api.models.db_models import User
from bytepit_api.database import db
from bytepit_api.models.enums import RegisterRole


def get_users():
    query_tuple = ("SELECT * FROM users", ())
    result = db.execute_one(query_tuple)
    if result["result"]:
        return [UserDTO(**user) for user in result["result"]]
    return None


def get_user_by_id(user_id: uuid.UUID):
    query_tuple = ("SELECT * FROM users WHERE id = %s", (user_id,))
    result = db.execute_one(query_tuple)

    if result["result"]:
        return User(**result["result"][0])
    else:
        return None


def get_unverified_organisers():
    query_tuple = ("SELECT * FROM users WHERE role = 'organiser' AND approved_by_admin = false", ())
    result = db.execute_one(query_tuple)
    if result["result"]:
        return [UserDTO(**user) for user in result["result"]]
    return None


def set_approved_organiser(username: str):
    query_tuple = ("UPDATE users SET approved_by_admin = true WHERE username = %s", (username,))
    result = db.execute_one(query_tuple)
    return result["affected_rows"] == 1


def set_user_role(username: str, new_role: RegisterRole):
    approved_by_admin = False if new_role == RegisterRole.organiser else True
    query_tuple = (
        "UPDATE users SET role = %s, approved_by_admin = %s WHERE username = %s",
        (new_role, approved_by_admin, username),
    )
    result = db.execute_one(query_tuple)
    return result["affected_rows"] == 1
