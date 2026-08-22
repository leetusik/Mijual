"""One event's page, and its 정정 story.

``GET /events/{rcept_no}``
    The whole detail card: identity (with the 본문 disagreement stated, never
    corrected), the governing countdown, every gate-passing field with its
    citation, and the per-type content R3 specifies — ①'s 환산 블록 inputs and its
    청약 결과 inset, ②'s API fact strip, ③'s two-step windows (which live inside
    the ``dissent_notice_procedure`` field, verbatim).

``GET /events/{rcept_no}/corrections``
    The CorrectionStory: the version rail with the current readable version
    marked, and that version's reading of what the last 정정 moved.

**The route key is ``rcept_no``, and it resolves against every version.** It is
what the design links by — the board row, the DART link and the 정정 rail all
speak filing numbers — and it survives the thing that makes ``rcept_no`` awkward
as a key: it *mutates* to the newest version (N2), so yesterday's link names a
superseded filing. Resolving against every stored version keeps that link
working while the page still renders **today's** reading. (``event_id`` travels in
every payload for a client that wants a stable handle.)

**Only a renderable event has a page.** ``exposable`` renders the card;
``withdrawn`` renders the 철회 notice with its evidence — that is a surface, not
an error. Everything else — suppressed, flagged, ``no_document``, ``no_detail``,
``incomplete_api_row`` — answers **404**. An event the contract does not expose
must not become a page that explains why it is not exposed: the reason is
internal, the operator's panel is where it is visible (`states-and-trust.md` §4).
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from sqlalchemy.orm import Session

from mijual.web import clock
from mijual.web.deps import DbSession
from mijual.web.errors import NotFound
from mijual.web.reads import Detail, event_payload, load_detail, resolve_event

router = APIRouter(tags=["events"])


def _detail(db: Session, rcept_no: str) -> Detail:
    event = resolve_event(db, rcept_no)
    if event is None:
        raise NotFound("event")
    detail = load_detail(db, event, today=clock.now().date())
    if not detail.view.renderable:
        # Not on the board, no page. The state is deliberately not disclosed.
        raise NotFound("event")
    return detail


@router.get("/events/{rcept_no}", summary="One event, as its detail page reads it")
def event(db: DbSession, rcept_no: str) -> dict[str, Any]:
    """The card, assembled by :func:`mijual.web.reads.event_payload`.

    The assembly moved into the read layer in `P6.S2` because a second caller
    arrived: the agent's ``get_event`` tool returns this exact payload, so the
    model may quote nothing this page would not show.
    """
    return event_payload(db, _detail(db, rcept_no))


@router.get(
    "/events/{rcept_no}/corrections", summary="The version rail and what the 정정 moved"
)
def corrections(db: DbSession, rcept_no: str) -> dict[str, Any]:
    detail = _detail(db, rcept_no)
    payload = detail.story.payload()
    payload["event_id"] = detail.view.event_id
    payload["rcept_no_current"] = detail.view.rcept_no
    return payload
