import os
from urllib.parse import quote
from datetime import timedelta, timezone, datetime
from typing import Union
from jose import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Response

import bytepit_api.database.auth_queries as auth_queries

from bytepit_api.models.dtos import LoginDTO


SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

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
    user = auth_queries.get_user_by_email(identifier) if is_email else auth_queries.get_user_by_username(identifier)
    return user


def login(form_data: LoginDTO, response: Response):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect identifier (email/username) or password. If you have not verified your account, please do so before logging in.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Users account inactive. Please verify your email before logging in.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.approved_by_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Users account not approved by admin. Please wait for admin approval before logging in.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    token_value = quote(f"Bearer {access_token}")
    response.set_cookie(key="access_token", value=token_value, httponly=True, samesite="none", secure=True)
    return {"access_token": access_token, "token_type": "bearer"}


def logout(response: Response):
    expires = datetime.utcnow() + timedelta(seconds=1)
    # this is needed because otherwise the Set-Cookie header is not properly propagated by azure
    response.set_cookie(
        key="access_token",
        value="",
        secure=True,
        httponly=True,
        samesite='none',
        expires=expires.strftime("%a, %d %b %Y %H:%M:%S GMT"),
    )
    return {"message": "Logged out"}
