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
