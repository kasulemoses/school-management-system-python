"""Configuration must fail safely and consistently before deployment."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.application import create_app
from app.core.settings import Settings


def test_environment_values_override_dotenv_and_do_not_depend_on_working_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("SMS_ENVIRONMENT=development\nSMS_ENABLE_LEARNING_ENDPOINTS=true\n")
    monkeypatch.setenv("SMS_ENVIRONMENT", "test")
    monkeypatch.chdir(tmp_path)

    settings = Settings(_env_file=env_file)

    assert settings.environment == "test"
    assert settings.enable_learning_endpoints is True


@pytest.mark.parametrize("environment", ["staging", "production"])
@pytest.mark.parametrize("option", ["debug", "enable_learning_endpoints"])
def test_deployed_settings_reject_development_features(environment: str, option: str) -> None:
    with pytest.raises(ValidationError, match="cannot enable"):
        Settings(_env_file=None, environment=environment, **{option: True})


@pytest.mark.parametrize(
    "origin",
    [
        "*",
        "https://*.example.com",
        "https://example.com/path",
        "https://user:secret@example.com",
        "https://example.com?token=secret",
        "https://example.com:99999",
        "https://exa\nmple.com",
    ],
)
def test_cors_requires_exact_origins(origin: str) -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, cors_origins=[origin])


def test_deployed_cors_requires_https() -> None:
    with pytest.raises(ValidationError, match="HTTPS"):
        Settings(_env_file=None, environment="production", cors_origins=["http://example.com"])


def test_production_has_no_learning_routes_or_public_api_schema() -> None:
    app = create_app(Settings(_env_file=None, environment="production"))
    with TestClient(app) as client:
        assert client.get("/health").status_code == 200
        for path in ["/docs", "/openapi.json", "/api/v1/examples/student-validation"]:
            assert client.post(path).status_code == 404
        assert client.get("/docs").status_code == 404
        assert client.get("/openapi.json").status_code == 404


def test_learning_endpoints_are_opt_in_even_in_development() -> None:
    app = create_app(Settings(_env_file=None))
    assert "/api/v1/examples/student-validation" not in app.openapi()["paths"]
