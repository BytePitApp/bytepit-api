from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from bytepit_api.models.auth_schemes import RegistrationForm
from bytepit_api.models.auth_schemes import Token


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
async def register(form_data: Annotated[RegistrationForm, Depends()]):
    return


@router.post("/confirm_registration/{verification_token}")
def confirm_email(verification_token: str):
    return


@router.post("/login", response_model=Token)
def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    return
