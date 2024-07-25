from fastapi import APIRouter
from starlette.responses import JSONResponse

from schemas.base import HealthResponse


router = APIRouter(prefix="/monitoring")


@router.get("/health", response_model=HealthResponse)
def check_system_health():
    return JSONResponse(content={"msg": "This is working perfectly"}, status_code=200)
