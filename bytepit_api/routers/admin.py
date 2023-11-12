import uuid

from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from bytepit_api.dependencies.auth_dependencies import get_current_admin_user
from bytepit_api.helpers.admin_helpers import save_role_to_db, verify_role
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
def change_role(
        user_id: uuid.UUID, new_role: Annotated[Role, "new_role"],
        current_admin_user: User = Depends(get_current_admin_user)):
    if not verify_role(new_role):
        all_roles = [role.value for role in Role]
        message = f"Requested role doesn't exist. Possible roles are {', '.join(all_roles)}"
        return Response(status_code=status.HTTP_200_OK, content=message)

    if save_role_to_db(user_id, new_role):
        message = f"Role successfully changed to {new_role}"
        return Response(status_code=status.HTTP_200_OK, content=message)

    message = "User with given id doesn't exist."
    return Response(status_code=status.HTTP_200_OK, content=message)
