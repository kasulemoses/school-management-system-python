"""Process health: this endpoint makes no claims about database readiness."""

from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["System"])


class HealthResponse(BaseModel):
    """The public response contract for the health endpoint."""

    status: Literal["ok"] = "ok"


@router.get("/health", response_model=HealthResponse, summary="Check API process health")
def health_check() -> HealthResponse:
    """Return successfully when the Python application can handle requests."""
    return HealthResponse()
