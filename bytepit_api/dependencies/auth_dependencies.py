import os

from urllib.parse import unquote

from typing import Annotated, Dict, Optional

from fastapi import Depends, HTTPException, status, Request
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param

from jose import JWTError, jwt

from bytepit_api.helpers.login_helpers import get_user_by_email_or_username
from bytepit_api.models.dtos import UserDTO
from bytepit_api.models.shared import TokenData

class OAuth2PasswordBearerWithCookie(OAuth2):
    def __init__(
        self,
        tokenUrl: str,
        scheme_name: Optional[str] = None,
        scopes: Optional[Dict[str, str]] = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {} 
        flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        authorization: str = request.cookies.get("access_token")
        authorization = unquote(authorization)

        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        return param


oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/api/auth/login")

SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = "HS256"


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = get_user_by_email_or_username(identifier=token_data.email)
    if user is None:
        raise credentials_exception
    return user


def get_current_verified_user(current_user: Annotated[UserDTO, Depends(get_current_user)]):
    if not current_user.is_verified:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_current_admin_user(current_user: Annotated[UserDTO, Depends(get_current_verified_user)]):
    if not current_user.role == "admin":
        raise HTTPException(status_code=400, detail="User is not admin")
    return current_user
