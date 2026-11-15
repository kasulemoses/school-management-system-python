"""Application entry point: Uvicorn imports the `app` object from this module."""

from app.application import create_app

app = create_app()
