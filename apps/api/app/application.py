"""Construct the application from settings without starting it at import time."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.v1.router import create_api_router
from app.core.errors import install_error_handlers, install_request_context
from app.core.settings import Settings


def create_app(settings: Settings | None = None) -> FastAPI:
    configuration = settings if settings is not None else Settings()
    application = FastAPI(
        title="School Management API",
        description="Python backend: process health, validated requests, and application settings.",
        version="0.1.0",
        debug=configuration.debug,
        docs_url="/docs" if configuration.is_local else None,
        redoc_url=None,
        openapi_url="/openapi.json" if configuration.is_local else None,
    )
    application.state.settings = configuration
    # CORS wraps sanitized errors so the browser can read error responses too.
    install_error_handlers(application)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=configuration.cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
        expose_headers=["X-Request-ID"],
    )
    # Registered last so request IDs also wrap CORS preflight responses.
    install_request_context(application)
    application.include_router(health_router)
    application.include_router(
        create_api_router(enable_learning_endpoints=configuration.enable_learning_endpoints)
    )
    return application
