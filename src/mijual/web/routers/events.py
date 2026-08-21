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

from mijual.gates.withdrawal import detect_withdrawal
from mijual.present import (
    convertible_view,
    issuer_disagreement,
    lapse_result,
    offering_inputs,
)
from mijual.web import clock
from mijual.web.deps import DbSession
from mijual.web.errors import NotFound
from mijual.web.reads import Detail, load_detail, resolve_event

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
    detail = _detail(db, rcept_no)
    payload = detail.view.payload()

    if detail.view.state == "withdrawn":
        # 철회 replaces the body: "no fields, no countdown, no old dates" (R3).
        # The exposure contract already empties the fields and the countdown;
        # the money block, the ② fact strip and the 정정 teaser would put the old
        # card back one key at a time, so a withdrawn event gets its notice and
        # its evidence and nothing else.
        evidence = _withdrawal(db, detail)
        if evidence:
            payload["withdrawal"] = evidence
        return payload

    story = detail.story
    payload["corrections"] = {
        "corrected": story.corrected,
        "versions": len(story.versions),
    }
    # The 정정 strip's teaser: the summary and the schedule sentence, verbatim.
    # The rail itself is one more request away — it is a separate view.
    for key in ("summary", "schedule_impact"):
        value = getattr(story, key)
        if value is not None:
            payload["corrections"][key] = value

    if detail.view.rights_type == "R1":
        _add_offering(payload, detail)
    if detail.view.rights_type == "R2":
        strip = convertible_view(detail.facts)
        if strip is not None:
            payload["convertible"] = strip.payload()
    return payload


@router.get(
    "/events/{rcept_no}/corrections", summary="The version rail and what the 정정 moved"
)
def corrections(db: DbSession, rcept_no: str) -> dict[str, Any]:
    detail = _detail(db, rcept_no)
    payload = detail.story.payload()
    payload["event_id"] = detail.view.event_id
    payload["rcept_no_current"] = detail.view.rcept_no
    return payload


def _add_offering(payload: dict[str, Any], detail: Detail) -> None:
    """①'s money: the 환산 블록's inputs, and the 청약 결과 once it exists.

    Both come from what the worker precomputed — the request path cannot build
    either (:mod:`mijual.estimate` imports the three spending modules). An
    offering with no stored inputs simply has no ``offering`` key: absent, never
    an empty object, and never a zero.
    """
    if detail.offering is not None:
        payload["offering"] = offering_inputs(detail.exposure, detail.offering).payload()
    report = detail.performance
    if report is None:
        return
    facts = report.facts if isinstance(report.facts, dict) else {}
    if isinstance(report.lapse, dict):
        payload["lapse_result"] = lapse_result(report.lapse, facts=facts).payload()
    # 발행사 기재 불일치: two readings, both cited, no verdict. It exists only
    # when the filing genuinely disagrees with itself.
    disagreement = issuer_disagreement(facts, rcept_no=report.rcept_no) if facts else None
    if disagreement is not None:
        payload["issuer_disagreement"] = disagreement.payload()


def _withdrawal(db: Session, detail: Detail) -> dict[str, Any]:
    """The 철회 evidence: the 정정사항 row that retracted the decision.

    R3's 철회 page is the locked notice plus *one sentence naming the evidence and
    a Citation with the withdrawal quote* — so the payload carries the row's own
    words (항목 · 정정 전 → 정정 후) and the span they were read at, and the
    surface writes the sentence. ``notice_ko`` is already on the view.

    Re-detected on the request rather than parsed out of the stored operator note:
    the note is one prose line for a person, and a Citation needs the parts. This
    reads stored bytes only — no OpenDART request, no model call — and a 철회 page
    is 11 events in the whole corpus.
    """
    found = detect_withdrawal(db, detail.event)
    if found is None:
        return {}
    out: dict[str, Any] = {
        "rcept_no": found.rcept_no,
        "item": found.item,
        "before": found.before,
        "after": found.after,
    }
    if found.span is not None:
        out["span"] = list(found.span)
    return out
