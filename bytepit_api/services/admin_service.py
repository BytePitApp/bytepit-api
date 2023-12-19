from fastapi import HTTPException, status

import bytepit_api.database.admin_queries as admin_queries

from bytepit_api.models.enums import Role


def get_users():
    result = admin_queries.get_users()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not find any users"
        )
    return result


def get_unverified_organisers():
    result = admin_queries.get_unverified_organisers()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No unverified organisers found"
        )
    return result


def set_approved_organiser(username: str):
    result = admin_queries.set_approved_organiser(username)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with {username} not found")
    return {"detail": f"Organiser {username} is now approved"}


def set_user_role(username: str, new_role: Role):
    result = admin_queries.set_user_role(username, new_role)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with {username} not found")
    return {"detail": f"Role successfully changed to {new_role} for user {username}"}
