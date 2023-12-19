import uuid
from bytepit_api.database import db
from bytepit_api.models.db_models import User


def set_verified_user(user_id: uuid.UUID):
    query_tuple = ("UPDATE users SET is_verified = TRUE WHERE id = %s", (user_id,))
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