"""CSRF for a cookie-authenticated JSON API: one required header, service-wide.

**The posture, decided here** (`security` listed CSRF handling as an apply-phase
decision) and applied to **every** unsafe method this service serves — not only
the ones ``P5.S7`` adds:

1. the session cookie is ``SameSite=Lax``, so a browser will not attach it to a
   cross-site ``POST`` at all;
2. **and** every ``POST`` / ``PUT`` / ``PATCH`` / ``DELETE`` must carry the
   header :data:`CSRF_HEADER`. Requests without it are refused before the route
   runs, with the ordinary error envelope and code ``csrf_required``.

The second half is what makes the first half's failure survivable. A custom
request header cannot be set by a cross-origin form, an image, a link or a
``<form target>``; a script *can* set one, but only after a **CORS preflight**
the server has to approve — and this service configures no CORS at all today
(``P5.S10`` owns the origin question when the frontend gets an origin). So the
header is a capability only same-origin code has, no token has to be minted,
stored, rotated or leaked into a page, and there is nothing for a reader's
browser to get wrong.

**Why service-wide rather than per-route.** A CSRF guard that each new route has
to remember to add is a guard that a later slice forgets. ``P5.S8``'s holdings
and 챙긴 돈 marks, and anything else that mutates, inherit this without opting
in. A route that ever genuinely needs an exception (a machine-to-machine
callback, say) must state the exception out loud — which is the right amount of
friction for punching a hole in this.

The guard adds no header of its own and reads no body; it only refuses. Its
answer is the same envelope as everything else, so a client parses one shape.
"""

from __future__ import annotations

from typing import Awaitable, Callable

from fastapi import FastAPI, Request, Response

from mijual.web.errors import error_response

__all__ = ["CSRF_HEADER", "UNSAFE_METHODS", "register_csrf_guard"]

#: Any non-empty value is accepted — the header's *presence* is the proof, and a
#: value the client has to compute would be a token scheme with extra steps.
CSRF_HEADER = "X-Mijual-CSRF"
#: The state-changing half of HTTP. ``GET``/``HEAD``/``OPTIONS`` are exempt
#: because they do not change state — a rule this service also enforces from the
#: other side (:func:`mijual.web.deps.get_write_session` refuses a safe method).
UNSAFE_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})


def register_csrf_guard(app: FastAPI) -> None:
    """Refuse every unsafe request that does not carry :data:`CSRF_HEADER`."""

    @app.middleware("http")
    async def _csrf_guard(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        if request.method.upper() in UNSAFE_METHODS and not request.headers.get(
            CSRF_HEADER
        ):
            return error_response(
                403,
                "csrf_required",
                f"state-changing requests must carry the {CSRF_HEADER} header",
            )
        return await call_next(request)
