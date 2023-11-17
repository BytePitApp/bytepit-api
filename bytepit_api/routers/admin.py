import uuid

from typing import Annotated, List

from fastapi import APIRouter, Depends, Response, status, HTTPException

from bytepit_api.dependencies.auth_dependencies import get_current_admin_user
from bytepit_api.models.auth_schemes import Role, User
from bytepit_api.database.queries import get_unverified_organisers, get_users, set_approved_organiser, set_user_role


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/list-users", response_model=List[User])
def list_users(current_admin_user: Annotated[User, Depends(get_current_admin_user)]):
    return get_users()


@router.get("/unverified-organisers", response_model=List[User])
def list_unverified_organisers(current_admin_user: Annotated[User, Depends(get_current_admin_user)]):
    return get_unverified_organisers()


@router.post("/confirm-organiser/{username}")
def confirm_organiser(username: str, current_admin_user: Annotated[User, Depends(get_current_admin_user)]):
    result = set_approved_organiser(username)
    if result:
        return {"detail": f"Organiser {username} is now approved"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


@router.post("/change-role/{username}/{new_role}")
def change_role(
    username: str,
    new_role: Annotated[Role, "new_role"],
    current_admin_user: Annotated[User, Depends(get_current_admin_user)],
):
    result = set_user_role(username, new_role)
    if result:
        return {"detail": f"Role successfully changed to {new_role}"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
