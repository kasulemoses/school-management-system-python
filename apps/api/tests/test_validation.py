"""Test the HTTP validation boundary, including attempts to submit protected fields."""

from uuid import UUID

import pytest
from fastapi.testclient import TestClient

PATH = "/api/v1/examples/student-validation"
STUDENT = {"first_name": "Amina", "last_name": "Example", "admission_number": "DEMO-0042"}


def test_valid_input_is_normalized_without_claiming_to_save_a_student(client: TestClient) -> None:
    response = client.post(PATH, json={**STUDENT, "first_name": "  Amina  "})

    assert response.status_code == 200
    assert response.json() == {"valid": True, "persisted": False, "student": STUDENT}
    assert UUID(response.headers["X-Request-ID"]).version == 4


@pytest.mark.parametrize(
    ("payload", "field", "error_type"),
    [
        ({"last_name": "Example", "admission_number": "DEMO-0042"}, "first_name", "missing"),
        ({**STUDENT, "first_name": "   "}, "first_name", "string_too_short"),
        ({**STUDENT, "last_name": 42}, "last_name", "string_type"),
        ({**STUDENT, "last_name": None}, "last_name", "string_type"),
        ({**STUDENT, "last_name": "x" * 101}, "last_name", "string_too_long"),
        ({**STUDENT, "admission_number": "x" * 51}, "admission_number", "string_too_long"),
        ({**STUDENT, "school_id": "another-school"}, "school_id", "extra_forbidden"),
        ({**STUDENT, "roles": ["administrator"]}, "roles", "extra_forbidden"),
    ],
)
def test_invalid_or_protected_input_is_rejected(
    client: TestClient, payload: dict, field: str, error_type: str
) -> None:
    response = client.post(PATH, json=payload)

    assert response.status_code == 422
    content = response.json()
    assert content["error"]["code"] == "validation_error"
    assert any(
        item["location"] == ["body", field] and item["type"] == error_type
        for item in content["error"]["details"]
    )
    assert content["request_id"] == response.headers["X-Request-ID"]


def test_validation_errors_do_not_echo_private_input(client: TestClient) -> None:
    marker = "fictional-private-value-never-echo"
    response = client.post(PATH, json={**STUDENT, "unknown_field": marker})

    assert response.status_code == 422
    assert marker not in response.text
    assert all(
        "input" not in detail and "ctx" not in detail
        for detail in response.json()["error"]["details"]
    )


def test_malformed_json_has_the_same_error_contract(client: TestClient) -> None:
    response = client.post(PATH, content="{", headers={"Content-Type": "application/json"})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"
    assert response.json()["error"]["details"][0]["type"] == "json_invalid"


def test_openapi_describes_the_validation_error_contract(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()
    responses = schema["paths"][PATH]["post"]["responses"]

    assert responses["422"]["content"]["application/json"]["schema"]["$ref"].endswith(
        "/ErrorResponse"
    )
