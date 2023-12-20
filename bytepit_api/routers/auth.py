from typing import Annotated

from fastapi import APIRouter, Depends, Response

from bytepit_api.services import auth_service
from bytepit_api.dependencies.auth_dependencies import get_current_verified_user
from bytepit_api.models.db_models import User
from bytepit_api.models.dtos import LoginDTO, RegisterDTO, TokenDTO, UserDTO


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
async def register(form_data: Annotated[RegisterDTO, Depends()]):
    return await auth_service.register(form_data)


@router.post("/confirm-registration/{verification_token}")
def confirm_email(verification_token: str):
    return auth_service.confirm_email(verification_token)


@router.post("/login", response_model=TokenDTO)
def login(response: Response, form_data: Annotated[LoginDTO, Depends()]):
    return auth_service.login(form_data, response)


@router.post("/logout")
def logout(response: Response):
    return auth_service.logout(response)


@router.get("/current", response_model=UserDTO)
def get_current_user(current_user: Annotated[User, Depends(get_current_verified_user)]):
    return current_user
