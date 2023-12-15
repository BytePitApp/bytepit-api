import uuid

from fastapi import APIRouter, status, HTTPException

from bytepit_api.database.queries import get_organisers_problems

router = APIRouter(prefix="/organiser", tags=["organiser"])


@router.get("/{organiser_id}/problems")
async def get_problems_by_organiser_id(organiser_id: uuid.UUID):
    problems = get_organisers_problems(organiser_id)
    if problems:
        return problems
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No problems found")
