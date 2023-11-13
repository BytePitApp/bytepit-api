import uuid

from bytepit_api.database import db
from bytepit_api.models.auth_schemes import UserInDB


def get_user_by_username(username: str):
    query_tuple = ("SELECT * FROM users WHERE username = %s", (username,))
    result = db.execute_one(query_tuple)
    if result["result"]:
        return UserInDB(**result["result"][0])
    else:
        return None


def get_user_by_email(email: str):
    query_tuple = ("SELECT * FROM users WHERE email = %s", (email,))
    result = db.execute_one(query_tuple)
    if result["result"]:
        return UserInDB(**result["result"][0])
    else:
        return None


def create_user(username, password_hash, name, surname, email, role, confirmation_token):
    approved_by_admin = False if role == "organiser" else True
    
    user_insert_query = (
        "INSERT INTO users (username, password_hash, name, surname, email, role, is_verified, approved_by_admin) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
        (username, password_hash, name, surname, email, role, False, approved_by_admin),
    )

    token_insert_query = (
        "INSERT INTO verification_tokens (token, email) " "VALUES (%s, %s)",
        (confirmation_token, email),
    )
    result = db.execute_many([user_insert_query, token_insert_query])
    return result["affected_rows"] == 2


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
        return UserInDB(**result["result"][0])
    else:
        return None
