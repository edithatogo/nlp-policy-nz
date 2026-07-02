"""RFC 7807 error parsing for the API client SDK."""

from __future__ import annotations

from enum import StrEnum

import httpx
from pydantic import BaseModel, Field


class ErrorCode(StrEnum):
    """Structured client-side API error codes."""

    AUTH_INVALID_KEY = "AUTH_INVALID_KEY"
    AUTH_INSUFFICIENT_SCOPE = "AUTH_INSUFFICIENT_SCOPE"
    MODEL_NOT_LOADED = "MODEL_NOT_LOADED"
    PIPELINE_FAILURE = "PIPELINE_FAILURE"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    RATE_LIMITED = "RATE_LIMITED"
    NOT_FOUND = "NOT_FOUND"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class ProblemError(BaseModel):
    """Field-level problem detail."""

    loc: list[str | int] = Field(default_factory=list)
    msg: str
    type: str


class ProblemDetail(BaseModel):
    """RFC 7807 problem detail payload."""

    type: str
    title: str
    status: int
    detail: str | None = None
    instance: str | None = None
    code: ErrorCode
    errors: list[ProblemError] | None = None
    request_id: str | None = None


class APIError(Exception):
    """HTTP error raised by the client SDK with parsed RFC 7807 content."""

    def __init__(
        self,
        message: str,
        *,
        request: httpx.Request | None,
        response: httpx.Response | None,
        problem: ProblemDetail | None = None,
    ) -> None:
        super().__init__(message)
        self.request = request
        self.response = response
        self.problem = problem
        self.message = message

    @property
    def code(self) -> ErrorCode | None:
        """Return the structured API error code, if available."""
        return None if self.problem is None else self.problem.code


def parse_problem_detail(response: httpx.Response) -> ProblemDetail | None:
    """Parse a problem+json response body, returning None when unavailable."""
    content_type = response.headers.get("content-type", "")
    if "application/problem+json" not in content_type:
        return None
    try:
        return ProblemDetail.model_validate(response.json())
    except Exception:
        return None


def raise_for_problem(response: httpx.Response) -> None:
    """Raise a client error carrying any parsed RFC 7807 payload."""
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        problem = parse_problem_detail(response)
        raise APIError(
            message=str(exc),
            request=exc.request,
            response=exc.response,
            problem=problem,
        ) from exc


__all__ = [
    "APIError",
    "ErrorCode",
    "ProblemDetail",
    "ProblemError",
    "parse_problem_detail",
    "raise_for_problem",
]
