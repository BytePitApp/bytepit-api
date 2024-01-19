from datetime import timedelta, datetime
from urllib.parse import quote
import uuid

from fastapi import HTTPException, status, Response

from bytepit_api.database import auth_queries
from bytepit_api.helpers import auth_helpers, email_helpers
from bytepit_api.models.dtos import LoginDTO, RegisterDTO


ACCESS_TOKEN_EXPIRE_MINUTES = 30


async def register(form_data: RegisterDTO):
    if auth_queries.get_user_by_email(form_data.email) or auth_queries.get_user_by_username(form_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already in use",
        )
    confirmation_token = auth_helpers.generate_confirmation_token()
    password_hash = auth_helpers.get_password_hash(form_data.password)
    result = auth_queries.create_user(
        form_data.username,
        password_hash,
        form_data.name,
        form_data.surname,
        form_data.email,
        form_data.role,
        confirmation_token,
        form_data.image,
    )
    if not result or not confirmation_token:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong. Please try again.",
        )
    await email_helpers.send_verification_email(form_data.email, confirmation_token)
    return Response(status_code=status.HTTP_201_CREATED)


def login(form_data: LoginDTO, response: Response):
    user = auth_helpers.authenticate_user(form_data.username, form_data.password)
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
    access_token = auth_helpers.create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
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
        samesite="none",
        expires=expires.strftime("%a, %d %b %Y %H:%M:%S GMT"),
    )
    return {"message": "Logged out"}


def confirm_email(verification_token: str):
    user = auth_queries.get_user_by_verification_token(verification_token)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong verification token")
    if user.is_verified:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already activated")
    result = auth_queries.set_verified_user(user.id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {user.id} not found")
    return {"message": "User activated"}


def get_user(username: str):
    user = auth_queries.get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {id} not found")
    return user
