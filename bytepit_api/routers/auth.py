from typing import Annotated

from fastapi import APIRouter, Depends
from bytepit_api.models.auth_schemes import RegistrationForm, LoginForm
from bytepit_api.models.auth_schemes import Token


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
async def register(form_data: Annotated[RegistrationForm, Depends()]):
    return


@router.post("/confirm-registration/{verification_token}")
def confirm_email(verification_token: str):
    return


@router.post("/login", response_model=Token)
def login_for_access_token(form_data: Annotated[LoginForm, Depends()]):
    return
