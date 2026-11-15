"""Learning endpoints never register students or write records."""

from fastapi import APIRouter

from app.core.errors import ErrorResponse
from app.schemas.learning import StudentInput, StudentValidationResponse

router = APIRouter(prefix="/examples", tags=["Learning examples"])


@router.post(
    "/student-validation",
    response_model=StudentValidationResponse,
    responses={422: {"model": ErrorResponse}},
    summary="Validate fictional student details without saving them",
    description="Development/test example. No database write, enrollment, or access grant occurs.",
)
def validate_student(payload: StudentInput) -> StudentValidationResponse:
    return StudentValidationResponse(student=payload)
