"""Assemble versioned routes using validated application configuration."""

from fastapi import APIRouter

from app.api.v1.examples import router as examples_router


def create_api_router(*, enable_learning_endpoints: bool) -> APIRouter:
    router = APIRouter(prefix="/api/v1")
    if enable_learning_endpoints:
        router.include_router(examples_router)
    return router
