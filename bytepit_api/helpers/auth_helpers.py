import os
import secrets

from datetime import datetime, timedelta, timezone
from typing import Union

from jose import jwt
from passlib.context import CryptContext

from bytepit_api.database import auth_queries


SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    return pwd_context.hash(password)


def generate_confirmation_token():
    return secrets.token_urlsafe(20)


def verify_password(plain_password, password_hash):
    return pwd_context.verify(plain_password, password_hash)


def check_if_email(identifier: str) -> bool:
    return "@" in identifier


def get_user_by_email_or_username(identifier: str):
    is_email = check_if_email(identifier)
    user = auth_queries.get_user_by_email(identifier) if is_email else auth_queries.get_user_by_username(identifier)
    return user


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
