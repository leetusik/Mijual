"""``GET /health`` — is the process up and is its clock what we think it is.

**It does not touch the database, on purpose.** A liveness check that fails when
Postgres is unreachable turns one outage into two: the process gets restarted or
pulled from the load balancer while it is still perfectly able to serve the last
known board. The product's rule is that a dead worker leaves the board **stale,
never dark**, and this endpoint is the operational half of that promise.

So it answers exactly two questions — the process is serving, and its idea of
*now* is Korean (`+09:00`) — which is also the smallest thing that proves the app
factory, the error envelope and the time policy are wired together.

**Data freshness is a different question with a different answer**: the 기준시각
the landing page shows comes from the summary endpoint (`P5.S3`), because
freshness is a fact about the corpus and belongs beside the corpus, not in a
liveness probe.
"""

from __future__ import annotations

from fastapi import APIRouter

from mijual import __version__
from mijual.web import clock

router = APIRouter(tags=["health"])


@router.get("/health", summary="Liveness — no database, no upstream")
def health() -> dict[str, str]:
    return {"status": "ok", "version": __version__, "now_kst": clock.iso(clock.now())}
