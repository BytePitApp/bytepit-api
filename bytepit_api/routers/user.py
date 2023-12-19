from typing import Annotated
from fastapi import APIRouter, Depends

from bytepit_api.dependencies.auth_dependencies import get_current_verified_user
from bytepit_api.models.db_models import User


router = APIRouter(prefix="/user", tags=["user"])


@router.get("/current", response_model=User)
def get_current_user(current_user: Annotated[User, Depends(get_current_verified_user)]):
    return current_user
