import uuid

from typing import Annotated

from fastapi import APIRouter

from bytepit_api.dependencies.auth_dependencies import get_current_admin_user
from bytepit_api.models.auth_schemes import Role, User


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users")
def list_users():
    return


@router.get(
    "/unverified-organisers",
)
def list_unverified_organisers():
    return


@router.post("/confirm-organiser/{user_id}")
def confirm_organiser(user_id: uuid.UUID):
    return


@router.post("/change-role/{user_id}/{new_role}")
def change_role(user_id: uuid.UUID, new_role: Annotated[Role, "new_role"]):
    return
