"""Create isolated application instances instead of inheriting a developer's .env."""

import os
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.application import create_app
from app.core.settings import Settings


@pytest.fixture(autouse=True)
def isolated_settings_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in list(os.environ):
        if name.upper().startswith("SMS_"):
            monkeypatch.delenv(name)


@pytest.fixture
def settings() -> Settings:
    return Settings(
        _env_file=None,
        environment="test",
        enable_learning_endpoints=True,
        cors_origins=["http://localhost:3000"],
    )


@pytest.fixture
def client(settings: Settings) -> Iterator[TestClient]:
    with TestClient(create_app(settings)) as test_client:
        yield test_client
