import secrets
from fastapi import HTTPException, status, Response

import bytepit_api.database.auth_queries as auth_queries
import bytepit_api.services.email_service as email_service

from passlib.context import CryptContext
from bytepit_api.models.dtos import RegisterDTO


def get_password_hash(password):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)


def generate_confirmation_token():
    return secrets.token_urlsafe(20)


async def register_user(form_data: RegisterDTO):
    if auth_queries.get_user_by_email(form_data.email) or auth_queries.get_user_by_username(form_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already in use",
        )
    confirmation_token = generate_confirmation_token()
    password_hash = get_password_hash(form_data.password)
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
    await email_service.send_verification_email(form_data.email, confirmation_token)
    return Response(status_code=status.HTTP_201_CREATED)