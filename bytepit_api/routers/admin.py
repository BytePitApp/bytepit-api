import uuid

from typing import Annotated

from fastapi import APIRouter, HTTPException

from bytepit_api.dependencies.auth_dependencies import get_current_admin_user
from bytepit_api.models.auth_schemes import Role, User, UserInDB, Users, UsersInDB
from bytepit_api.database.queries import get_users, get_unverified_organisers


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/list-users")
def list_users() -> list[UserInDB]:
    users = get_users()
    if users is None:
        raise HTTPException(status_code=500, detail="Internal server error")
    if len(users.users) == 0:
        raise HTTPException(status_code=404, detail="No users found")
    return users.users


@router.get(
    "/unverified-organisers",
)
def list_unverified_organisers() -> list[UserInDB]:
    organizers = get_unverified_organisers()
    if organizers is None:
        raise HTTPException(status_code=500, detail="Internal server error")
    if len(organizers.users) == 0:
        raise HTTPException(status_code=404, detail="No unverified organisers found")
    return organizers.users


@router.post("/confirm-organiser/{user_id}")
def confirm_organiser(user_id: uuid.UUID):
    return


@router.post("/change-role/{user_id}/{new_role}")
def change_role(user_id: uuid.UUID, new_role: Annotated[Role, "new_role"]):
    return
