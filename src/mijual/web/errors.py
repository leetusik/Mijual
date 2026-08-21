"""The error envelope — one JSON shape for every failure this service returns.

**The shape.** Every non-2xx response, without exception, is::

    {"error": {"code": "not_found",
               "message": "no route matches this path",
               "message_ko": "…",          # OPTIONAL — see below
               "fields": [ … ]}}           # OPTIONAL — 422 only

* ``code`` — a stable machine token in English ``snake_case``. This is what a
  client branches on; it is part of the contract and does not change to improve
  wording.
* ``message`` — English, **developer-facing**. It goes in a log or a dev console
  and is never rendered to a user. It never carries a stack trace, a SQL string,
  a URL with a credential in it, or an upstream exception's text (see
  :func:`_unhandled`): an error body is an outward surface.
* ``message_ko`` — **present only when the product already owns a Korean string
  for this condition**, and absent otherwise.
* ``fields`` — request-validation detail, 422 only, English. A 422 from this API
  means *our own client* sent something malformed, so the audience is a
  developer.

**Why ``message_ko`` is usually absent.** Korean-only product surface is a
constraint, and its other half is that *inventing a Korean string is a design
change*, not an implementation detail: user copy is locked and comes from
`grounding/copy-inventory.md`. The signed design writes no HTTP-error copy — it
writes **state** copy (철회 / 추후결정 / 발행사 기재 불일치), which reaches the user
through the normal 200 payload, not through an error. So the envelope carries
Korean only where the product genuinely has it — an :class:`ApiError` raised with
an existing string such as ``WITHDRAWN_NOTICE_KO`` — and otherwise ships the
``code`` alone and lets the surface decide, once, in the design's own words.

Absent, not ``null``: an optional key is **omitted** when it has no value, the
same discipline the exposure contract applies to a gate-blocked field. A client
that sees ``message_ko`` at all can trust it.

**Registration.** :func:`register_error_handlers` wires the handlers onto the app
factory so *unhandled* exceptions, 404/405, and validation errors all come back
in this envelope. A client can therefore parse one shape; there is no second
FastAPI-default ``{"detail": …}`` body hiding behind an edge case.
"""

from __future__ import annotations

import logging
from typing import Any, Mapping

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

__all__ = [
    "ApiError",
    "NotFound",
    "envelope",
    "error_response",
    "register_error_handlers",
]

log = logging.getLogger(__name__)

#: HTTP status → the envelope ``code`` for errors this service did not raise
#: itself (a 404 from the router, a 405 from the method matcher, …). Anything
#: unmapped falls back to ``http_error`` rather than to an invented token.
_STATUS_CODES: Mapping[int, str] = {
    400: "bad_request",
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    405: "method_not_allowed",
    409: "conflict",
    422: "invalid_request",
    429: "too_many_requests",
    500: "internal_error",
    503: "unavailable",
}


class ApiError(Exception):
    """A failure this service reports deliberately, in the envelope.

    Endpoints raise this instead of ``HTTPException`` when they want to name the
    ``code`` a client branches on. ``message_ko`` is passed **only** when the
    product already owns that Korean string; the default is no Korean at all.
    """

    def __init__(
        self,
        code: str,
        message: str,
        *,
        status_code: int = 400,
        message_ko: str | None = None,
        **extra: Any,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.message_ko = message_ko
        self.extra = extra


class NotFound(ApiError):
    """404 for a resource that genuinely is not there (an unknown 종목, event …).

    Distinct from the router's own 404 for an unknown path, which carries code
    ``not_found`` with no ``resource``.
    """

    def __init__(self, resource: str, *, message_ko: str | None = None) -> None:
        super().__init__(
            "not_found",
            f"{resource} not found",
            status_code=404,
            message_ko=message_ko,
            resource=resource,
        )


def envelope(
    code: str, message: str, *, message_ko: str | None = None, **extra: Any
) -> dict[str, Any]:
    """The envelope body. Optional keys are omitted, never set to ``null``."""
    body: dict[str, Any] = {"code": code, "message": message}
    if message_ko is not None:
        body["message_ko"] = message_ko
    body.update({k: v for k, v in extra.items() if v is not None})
    return {"error": body}


def error_response(
    status_code: int,
    code: str,
    message: str,
    *,
    message_ko: str | None = None,
    headers: Mapping[str, str] | None = None,
    **extra: Any,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=envelope(code, message, message_ko=message_ko, **extra),
        headers=dict(headers) if headers else None,
    )


async def _api_error(_: Request, exc: ApiError) -> JSONResponse:
    return error_response(
        exc.status_code,
        exc.code,
        exc.message,
        message_ko=exc.message_ko,
        **exc.extra,
    )


async def _http_exception(_: Request, exc: StarletteHTTPException) -> JSONResponse:
    """404/405 and any ``HTTPException`` — rewrapped out of FastAPI's ``detail``."""
    detail = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    return error_response(
        exc.status_code,
        _STATUS_CODES.get(exc.status_code, "http_error"),
        detail or f"http {exc.status_code}",
        headers=getattr(exc, "headers", None),
    )


async def _validation(_: Request, exc: RequestValidationError) -> JSONResponse:
    """422 — our own client sent a malformed request. English detail, by design."""
    fields = [
        {"loc": [str(part) for part in err.get("loc", ())], "msg": err.get("msg", "")}
        for err in exc.errors()
    ]
    return error_response(
        422, "invalid_request", "request failed validation", fields=fields or None
    )


async def _unhandled(request: Request, exc: Exception) -> JSONResponse:
    """500 — logged in full here, told to the client as nothing but a code.

    The traceback is operator information: it names tables, paths and query
    shapes. It goes to the log with the request line attached, and the body says
    only that the request failed.
    """
    log.exception("unhandled error serving %s %s", request.method, request.url.path)
    return error_response(500, "internal_error", "the request could not be served")


def register_error_handlers(app: FastAPI) -> None:
    """Wire every failure path onto ``app`` so one envelope covers all of them."""
    app.add_exception_handler(ApiError, _api_error)  # type: ignore[arg-type]
    app.add_exception_handler(StarletteHTTPException, _http_exception)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, _validation)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, _unhandled)
