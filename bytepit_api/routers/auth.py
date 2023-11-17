from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Response

from bytepit_api.helpers.confirmation_helpers import activate_user
from bytepit_api.helpers.email_helpers import send_verification_email
from bytepit_api.helpers.login_helpers import authenticate_user, create_access_token
from bytepit_api.helpers.register_helpers import register_user
from bytepit_api.models.auth_schemes import LoginForm, RegistrationForm, Token
from bytepit_api.database.queries import get_user_by_email, get_user_by_username

router = APIRouter(prefix="/auth", tags=["auth"])

ACCESS_TOKEN_EXPIRE_MINUTES = 30


@router.post("/register")
async def register(form_data: Annotated[RegistrationForm, Depends()]):
    if get_user_by_email(form_data.email) or get_user_by_username(form_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already in use.",
        )

    confirmation_token = register_user(
        form_data.username,
        form_data.password,
        form_data.name,
        form_data.surname,
        form_data.email,
        form_data.role,
        # form_data.image,
    )

    if not confirmation_token:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong. Please try again.",
        )

    await send_verification_email(form_data.email, confirmation_token)
    return Response(status_code=status.HTTP_201_CREATED)


@router.post("/confirm-registration/{verification_token}")
def confirm_email(verification_token: str):
    activation_result = activate_user(verification_token)
    if activation_result:
        return {"message": "User activated"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong verification token or user already activated"
        )


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
            detail="Users account inactive. Please verify your email before logging in.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"message": "Logged out"}
