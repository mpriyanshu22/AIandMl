"""
app/routers/health.py
Health check and system status endpoint.
"""

from fastapi import APIRouter, status
from app.models.schemas import HealthResponse
from app.config import settings

# APIRouter acts like a mini-FastAPI app for grouping related endpoints
router = APIRouter(
    prefix="/health",
    tags=["System & Health"]
)


@router.get(
    "",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Returns the operational status and version of the API."
)
async def get_health():
    """Returns 200 OK along with app details."""
    return HealthResponse(
        status="ok",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION
    )