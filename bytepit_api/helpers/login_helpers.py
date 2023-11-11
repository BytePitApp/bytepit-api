import os

from datetime import datetime, timedelta, timezone
from typing import Union

from jose import jwt
from passlib.context import CryptContext

from bytepit_api.database.queries import get_user_by_email, get_user_by_username

SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = "HS256"


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, password_hash):
    return pwd_context.verify(plain_password, password_hash)


def check_if_email(identifier: str) -> bool:
    return "@" in identifier


def authenticate_user(identifier: str, password: str):
    user = get_user_by_email_or_username(identifier)
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_user_by_email_or_username(identifier: str):
    is_email = check_if_email(identifier)
    user = (
        get_user_by_email(identifier) if is_email else get_user_by_username(identifier)
    )
    return user
