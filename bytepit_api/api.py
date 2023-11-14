from fastapi import APIRouter, Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from bytepit_api.dependencies.auth_dependencies import get_current_admin_user
from bytepit_api.routers.admin import router as admin_router
from bytepit_api.routers.auth import router as auth_router
from bytepit_api.routers.user import router as user_router


router = APIRouter()
router.include_router(admin_router)
router.include_router(auth_router)
router.include_router(user_router)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
