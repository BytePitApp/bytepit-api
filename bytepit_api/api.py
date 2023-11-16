from fastapi import APIRouter, FastAPI, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    formatted_errors = [] 
    error_details = exc.errors()
    for error in error_details:
        print(error)
        error_message = error["msg"]
        if "value is not a valid email address: " in error_message:
            error_message = error_message.replace("value is not a valid email address: ", "")
            formatted_message = f"{error_message}"
        else:
            error_field_name = error["loc"][1]
            formatted_message = f"{error_message}: {error_field_name}"
        formatted_errors.append(formatted_message)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"errors": formatted_errors},
    )