import bytepit_api.database.conformation_queries as confirmation_queries
from fastapi import HTTPException, status


def activate_user(verification_token: str):
    user = confirmation_queries.get_user_by_verification_token(verification_token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wrong verification token"
        )
    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already activated"
        )
    result = confirmation_queries.set_verified_user(user.id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user.id} not found"
        )
    return {"message": "User activated"}
