from fastapi import APIRouter


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users")
def list_users():
    return


@router.post("/confirm-organizer/{user_id}")
def confirm_organizer(user_id: int):
    return


@router.patch("/change-role/{user_id}")
def change_role(user_id: int):
    return
