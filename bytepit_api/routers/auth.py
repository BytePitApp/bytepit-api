from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Response

from bytepit_api.helpers.login_helpers import authenticate_user, create_access_token
from bytepit_api.models.auth_schemes import LoginForm, RegistrationForm, Token


router = APIRouter(prefix="/auth", tags=["auth"])

ACCESS_TOKEN_EXPIRE_MINUTES = 30


@router.post("/register")
async def register(form_data: Annotated[RegistrationForm, Depends()]):
    return


@router.post("/confirm-registration/{verification_token}")
def confirm_email(verification_token: str):
    return


@router.post("/login", response_model=Token)
def login_for_access_token(response: Response, form_data: Annotated[LoginForm, Depends()]):
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
            detail="Account inactive. Please verify your email before logging in.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return {"access_token": access_token, "token_type": "bearer"}
