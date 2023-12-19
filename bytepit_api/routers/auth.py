from typing import Annotated
from fastapi import APIRouter, Depends, Response

import bytepit_api.services.login_service as login_service
import bytepit_api.services.register_service as register_service
import bytepit_api.services.confirmation_service as confirmation_service

from bytepit_api.models.dtos import LoginDTO, RegisterDTO, TokenDTO


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
async def register(form_data: Annotated[RegisterDTO, Depends()]):
    return await register_service.register_user(form_data)


@router.post("/confirm-registration/{verification_token}")
def confirm_email(verification_token: str):
    return confirmation_service.activate_user(verification_token)


@router.post("/login", response_model=TokenDTO)
def login_for_access_token(response: Response, form_data: Annotated[LoginDTO, Depends()]):
    return login_service.login(form_data, response)


@router.post("/logout")
def logout(response: Response):
    return login_service.logout(response)
