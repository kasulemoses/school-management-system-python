"""Application entry point: Uvicorn imports the `app` object from this module."""

from fastapi import FastAPI

from app.api.health import router as health_router

app = FastAPI(
    title="School Management API",
    description=(
        "Python backend for the student management system. "
        "Checkpoint 1 provides process health and interactive API documentation."
    ),
    version="0.1.0",
)

app.include_router(health_router)
