"""Stable error responses and server-generated request identifiers."""

import logging
from http import HTTPStatus
from uuid import uuid4

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.exceptions import HTTPException
from starlette.middleware.base import RequestResponseEndpoint

logger = logging.getLogger(__name__)


class ValidationIssue(BaseModel):
    location: list[str | int]
    message: str
    type: str


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: list[ValidationIssue]


class ErrorResponse(BaseModel):
    error: ErrorDetail
    request_id: str


def error_response(
    request: Request,
    *,
    status_code: int,
    code: str,
    message: str,
    details: list[ValidationIssue] | None = None,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    content = ErrorResponse(
        error=ErrorDetail(code=code, message=message, details=details or []),
        request_id=request.state.request_id,
    )
    return JSONResponse(content.model_dump(mode="json"), status_code=status_code, headers=headers)


def install_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        issues = [
            ValidationIssue(location=list(item["loc"]), message=item["msg"], type=item["type"])
            for item in exc.errors()
        ]
        # Do not return Pydantic's raw input/context, which can contain private values.
        return error_response(
            request,
            status_code=422,
            code="validation_error",
            message="The request did not pass validation",
            details=issues,
        )

    @app.exception_handler(HTTPException)
    async def http_error(request: Request, exc: HTTPException) -> JSONResponse:
        codes = {
            400: "bad_request",
            401: "authentication_required",
            403: "forbidden",
            404: "not_found",
            405: "method_not_allowed",
            409: "conflict",
            429: "rate_limited",
        }
        try:
            default_message = HTTPStatus(exc.status_code).phrase
        except ValueError:
            default_message = "Request failed"
        message = exc.detail if isinstance(exc.detail, str) else default_message
        if exc.status_code >= 500:
            message = "An unexpected server error occurred"
        return error_response(
            request,
            status_code=exc.status_code,
            code=codes.get(exc.status_code, "http_error"),
            message=message,
            headers=exc.headers,
        )

    @app.middleware("http")
    async def sanitize_unexpected_errors(
        request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        try:
            return await call_next(request)
        except Exception as exc:
            # Log correlation and exception type without body, token, or exception text.
            logger.error(
                "Unhandled request error request_id=%s exception_type=%s",
                request.state.request_id,
                type(exc).__name__,
            )
            return error_response(
                request,
                status_code=500,
                code="internal_error",
                message="An unexpected server error occurred",
            )


def install_request_context(app: FastAPI) -> None:
    @app.middleware("http")
    async def request_context(request: Request, call_next: RequestResponseEndpoint) -> Response:
        request.state.request_id = str(uuid4())
        response = await call_next(request)
        response.headers["X-Request-ID"] = request.state.request_id
        return response
