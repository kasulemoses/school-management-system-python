"""Check errors, correlation, and the browser-origin boundary through real HTTP calls."""

from uuid import UUID

from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.application import create_app
from app.core.settings import Settings


def test_not_found_uses_the_error_contract(client: TestClient) -> None:
    response = client.get("/missing")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"
    assert response.json()["request_id"] == response.headers["X-Request-ID"]


def test_request_ids_are_generated_by_the_server_and_change_per_request(client: TestClient) -> None:
    first = client.get("/health", headers={"X-Request-ID": "untrusted-caller-value"})
    second = client.get("/health")

    assert UUID(first.headers["X-Request-ID"]).version == 4
    assert first.headers["X-Request-ID"] != second.headers["X-Request-ID"]


def test_allowed_browser_preflight_exposes_only_the_configured_origin(client: TestClient) -> None:
    response = client.options(
        "/api/v1/examples/student-validation",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type,authorization",
        },
    )

    assert response.status_code == 200
    assert response.headers["Access-Control-Allow-Origin"] == "http://localhost:3000"
    assert "Access-Control-Allow-Credentials" not in response.headers
    assert UUID(response.headers["X-Request-ID"]).version == 4


def test_unlisted_browser_origin_fails_preflight(client: TestClient) -> None:
    response = client.options(
        "/health",
        headers={"Origin": "https://unlisted.example", "Access-Control-Request-Method": "GET"},
    )

    assert response.status_code == 400
    assert "Access-Control-Allow-Origin" not in response.headers


def test_unexpected_errors_are_sanitized_and_correlated(settings: Settings) -> None:
    app = create_app(settings)

    @app.get("/_test/raise")
    def raise_error() -> None:
        raise RuntimeError("private-internal-value")

    with TestClient(app) as client:
        response = client.get("/_test/raise", headers={"Origin": "http://localhost:3000"})

    assert response.status_code == 500
    assert "private-internal-value" not in response.text
    assert response.json()["error"]["code"] == "internal_error"
    assert response.json()["request_id"] == response.headers["X-Request-ID"]
    assert response.headers["Access-Control-Allow-Origin"] == "http://localhost:3000"
    assert "X-Request-ID" in response.headers["Access-Control-Expose-Headers"]


def test_http_errors_preserve_authentication_headers(settings: Settings) -> None:
    app = create_app(settings)

    @app.get("/_test/protected")
    def protected() -> None:
        raise HTTPException(401, "Sign in required", headers={"WWW-Authenticate": "Bearer"})

    with TestClient(app) as client:
        response = client.get("/_test/protected")

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"
    assert response.json()["error"]["code"] == "authentication_required"
