"""Exercise the public HTTP contract without starting a real network listener."""

from fastapi.testclient import TestClient


def test_health_is_public_and_returns_a_small_json_response(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    assert response.json() == {"status": "ok"}


def test_interactive_documentation_and_openapi_are_available(client: TestClient) -> None:
    docs = client.get("/docs")
    schema = client.get("/openapi.json")

    assert docs.status_code == 200
    assert "text/html" in docs.headers["content-type"]
    assert schema.status_code == 200
    assert "get" in schema.json()["paths"]["/health"]
