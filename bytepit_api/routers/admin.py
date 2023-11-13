import uuid

from typing import Annotated, List

from fastapi import APIRouter

from bytepit_api.dependencies.auth_dependencies import get_current_admin_user
from bytepit_api.models.auth_schemes import Role, User
from bytepit_api.database.queries import get_users, get_unverified_organisers


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get(
    "/list-users",
    response_model=List[User],
)
def list_users():
    return get_users()


@router.get(
    "/unverified-organisers",
    response_model=List[User],
)
def list_unverified_organisers():
    return get_unverified_organisers()


@router.post("/confirm-organiser/{user_id}")
def confirm_organiser(user_id: uuid.UUID):
    return


@router.post("/change-role/{user_id}/{new_role}")
def change_role(user_id: uuid.UUID, new_role: Annotated[Role, "new_role"]):
    return
