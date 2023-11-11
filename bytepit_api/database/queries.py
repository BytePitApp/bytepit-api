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


def create_user(
    username, password_hash, name, surname, email, role, image, confirmation_token
):
    user_insert_query = (
        "INSERT INTO users (username, password_hash, name, surname, email, role, image, is_verified) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
        (username, password_hash, name, surname, email, role, image, False),
    )

    token_insert_query = (
        "INSERT INTO verification_tokens (token, user_id) "
        "VALUES (%s, (SELECT id FROM users WHERE email = %s))",
        (confirmation_token, email),
    )
    db.execute_many(user_insert_query, token_insert_query)
