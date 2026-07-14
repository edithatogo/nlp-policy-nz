"""RFC 7807 problem-detail helpers for the API."""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from nlp_policy_nz.api.observability import current_request_id

PROBLEM_JSON_MEDIA_TYPE = "application/problem+json"


class ProblemCode(StrEnum):
    """Standardized API error codes."""

    AUTH_INVALID_KEY = "AUTH_INVALID_KEY"
    AUTH_INSUFFICIENT_SCOPE = "AUTH_INSUFFICIENT_SCOPE"
    MODEL_NOT_LOADED = "MODEL_NOT_LOADED"
    PIPELINE_FAILURE = "PIPELINE_FAILURE"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    RATE_LIMITED = "RATE_LIMITED"
    NOT_FOUND = "NOT_FOUND"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class ProblemError(BaseModel):
    """Field-level validation error payload."""

    loc: list[str | int] = Field(default_factory=list)
    msg: str
    type: str


class ProblemDetail(BaseModel):
    """RFC 7807 problem detail payload with an API-specific error code."""

    type: str
    title: str
    status: int
    detail: str | None = None
    instance: str | None = None
    code: ProblemCode
    errors: list[ProblemError] | None = None
    request_id: str | None = None


def _problem_type(code: ProblemCode) -> str:
    return f"https://nlp-policy-nz.local/problems/{code.value.lower()}"


def _title_for_status(status: int) -> str:
    return {
        400: "Bad Request",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        413: "Content Too Large",
        422: "Unprocessable Entity",
        429: "Too Many Requests",
        500: "Internal Server Error",
        503: "Service Unavailable",
    }.get(status, "Error")


def _code_for_http_exception(request: Request, exc: HTTPException) -> ProblemCode:
    detail = str(exc.detail).upper()
    code = ProblemCode.PIPELINE_FAILURE
    if exc.status_code == 401:
        code = ProblemCode.AUTH_INVALID_KEY
    elif exc.status_code == 403:
        code = ProblemCode.AUTH_INSUFFICIENT_SCOPE
    elif exc.status_code == 404:
        code = ProblemCode.NOT_FOUND
    elif exc.status_code == 429:
        code = ProblemCode.RATE_LIMITED
    elif exc.status_code == 503 and ("MODEL" in detail or "EMBED" in request.url.path.upper()):
        code = ProblemCode.MODEL_NOT_LOADED
    return code


def problem_response(
    *,
    status_code: int,
    code: ProblemCode,
    detail: str | None,
    instance: str | None,
    errors: list[ProblemError] | None = None,
) -> JSONResponse:
    """Build a problem+json response."""
    payload = ProblemDetail(
        type=_problem_type(code),
        title=_title_for_status(status_code),
        status=status_code,
        detail=detail,
        instance=instance,
        code=code,
        errors=errors,
        request_id=current_request_id(),
    )
    response = JSONResponse(
        status_code=status_code,
        content=payload.model_dump(mode="json"),
        media_type=PROBLEM_JSON_MEDIA_TYPE,
    )
    if payload.request_id:
        response.headers["X-Request-ID"] = payload.request_id
    return response


def _validation_errors(exc: RequestValidationError) -> list[ProblemError]:
    return [
        ProblemError(
            loc=[str(part) for part in error.get("loc", [])],
            msg=str(error.get("msg", "Validation error")),
            type=str(error.get("type", "validation_error")),
        )
        for error in exc.errors()
    ]


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Convert FastAPI HTTP exceptions into RFC 7807 responses."""
    detail = None if exc.detail is None else str(exc.detail)
    return problem_response(
        status_code=exc.status_code,
        code=_code_for_http_exception(request, exc),
        detail=detail,
        instance=request.url.path,
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Convert validation failures into RFC 7807 responses."""
    return problem_response(
        status_code=422,
        code=ProblemCode.VALIDATION_ERROR,
        detail="Request validation failed.",
        instance=request.url.path,
        errors=_validation_errors(exc),
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Convert unhandled exceptions into RFC 7807 responses."""
    return problem_response(
        status_code=500,
        code=ProblemCode.INTERNAL_ERROR,
        detail=str(exc) or "Internal server error.",
        instance=request.url.path,
    )


def register_problem_handlers(app: FastAPI) -> None:
    """Register RFC 7807 exception handlers on the FastAPI app."""
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)


def response_schema_ref() -> dict[str, Any]:
    """Return an OpenAPI schema reference for problem details."""
    return {"$ref": "#/components/schemas/ProblemDetail"}
