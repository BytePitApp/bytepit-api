from fastapi import APIRouter, FastAPI

from bytepit_api.routers.admin import router as admin_router
from bytepit_api.routers.auth import router as auth_router


router = APIRouter()
router.include_router(admin_router)
router.include_router(auth_router)

app = FastAPI()
app.include_router(router)
