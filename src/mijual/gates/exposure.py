"""The exposure contract: the single derivation ``P3`` reads.

This is the durable boundary between P2 and P3, and it is deliberately one
function rather than a convention every renderer re-implements. **P3 must never
decide exposure for itself** — it renders what this says, and nothing else.

An **event** is exposable iff *all* of:

* it is not suppressed (``Event.suppressed_reason is None`` — 제3자배정/일반공모
  유증, 소규모합병, unpaired placeholders … all keep their evidence and stay out);
* it is not **withdrawn** (a 정정사항 row retracted the decision — N39);
* it carries no unresolved **identity / rights conflict** flag. Today that is
  ``warrant_conflict`` (본문 ``18.`` denies the 증서 that ``ic_mthn`` implies, O-8),
  ``detail_conflict`` (the detail rows on one event key disagree about whether a
  right exists) and ``event_key_collision`` / ``hint_split_evidence`` (the key
  provably holds 2+ events, N20/N32). **Conflicting evidence is not a reason to
  delete an event and not a reason to publish it** — S2/S3's rule (never suppress
  on a conflict) and this rule (never expose on a conflict) are the two halves of
  the same conservative default.

A **field** is exposable iff its gate said ``passed`` (render the value) or
``tbd`` (render ``추후결정`` — never the superseded date it replaced, N40).
Everything else stays recorded with its reason code and is never shown.

**② is the one rights type whose countdown is not a 본문 reading** (N6): 전환가액,
전환청구기간 and the 오버행 수량·비율 are all `API` tier, so requiring a stored 본문
would block a perfectly renderable event for the sake of prose it does not need.
Its arm therefore replaces the *document* requirement with an *API completeness*
requirement — every field of :data:`mijual.cb.R2_REQUIRED_API_FIELDS` present and
parseable on the current version's detail row — and is otherwise identical
(suppression, 철회 and the blocking flags all apply unchanged). ``P2.S7``'s
prose fields 6–8 are additive colour on top: an event renders with none of them.

The two are independent on purpose: a blocked event can still hold perfectly
gated fields (they are simply not rendered), and an exposable event can hold
blocked fields (the rest of the card still renders). Both counts are reported.

Only the event's **current readable version** is ever read — the newest version
that has a stored 본문 — because a superseded version's gate verdicts are true
about superseded values, and the countdown must never fall back to them (N4).
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.orm import Session

if TYPE_CHECKING:  # pragma: no cover - imported for types only
    # ``mijual.cb`` imports this module, so the type is not imported at runtime.
    from mijual.cb import ConvertibleFacts

from mijual.db.models import Event, Extraction, FilingVersion, RightsType
from mijual.db.repository import current_version
from mijual.gates.outcome import EXPOSABLE_STATUSES, TBD

__all__ = [
    "BLOCKING_FLAGS",
    "EventExposure",
    "FieldView",
    "WITHDRAWN_NOTICE_KO",
    "current_version",
    "event_exposure",
    "exposure_of",
    "exposure_of_all",
]

#: Event-level flags that block exposure until a human or a later slice resolves
#: them. Plain strings (the flags themselves are plain strings — N15/N16).
BLOCKING_FLAGS: dict[str, str] = {
    "warrant_conflict": "본문 18. 신주인수권양도여부가 증서 발행을 부인합니다",
    "detail_conflict": "같은 이벤트 키의 상세 행들이 권리 존재 여부에 대해 엇갈립니다",
    "event_key_collision": "이벤트 키가 둘 이상의 공시를 담고 있습니다",
    "hint_split_evidence": "본문 최초제출일이 서로 달라 둘 이상의 이벤트로 확인됩니다",
}

#: What the board says instead of a countdown when a filing is withdrawn.
#: A demo asset in its own right, like the 소규모합병 suppression.
WITHDRAWN_NOTICE_KO: dict[str, str] = {
    "R1": "이 유상증자는 철회되었습니다",
    "R2": "이 사채 발행은 철회되었습니다",
    "R3": "이 합병은 철회되었습니다",
}
#: What the board shows for a ``tbd`` field.
TBD_DISPLAY_KO = "추후결정"


@dataclass(frozen=True)
class FieldView:
    """One field as the product may (or may not) render it."""

    field_key: str
    gate_status: str | None
    reason_code: str | None
    exposable: bool
    #: ``value`` → render the stored value; ``추후결정`` → render the notice.
    display: str | None
    value: object | None
    quote: str | None
    span: tuple[int, int] | None
    rcept_no: str | None


@dataclass
class EventExposure:
    """The verdict on one event, plus the fields it may show."""

    event_id: int
    corp_code: str
    corp_name: str | None
    rights_type: str
    original_rcept_dt: date | None
    rcept_no: str | None
    state: str
    reason_code: str | None
    note: str | None = None
    fields: dict[str, FieldView] = field(default_factory=dict)

    @property
    def exposable(self) -> bool:
        return self.state == "exposable"

    @property
    def exposable_fields(self) -> list[FieldView]:
        """Fields that passed their gate — a *field*-level fact, on any event."""
        return [f for f in self.fields.values() if f.exposable]

    @property
    def renderable_fields(self) -> list[FieldView]:
        """What P3 may actually put on a card: gate-passing fields of an
        exposable event. A blocked event renders its notice and nothing else."""
        return self.exposable_fields if self.exposable else []

    @property
    def notice_ko(self) -> str | None:
        if self.state == "withdrawn":
            return WITHDRAWN_NOTICE_KO.get(self.rights_type)
        return None

    def render(self) -> str:
        mark = {"exposable": "[+]", "withdrawn": "[철회]"}.get(self.state, "[-]")
        head = (
            f"{mark} {self.rights_type} {self.corp_name or self.corp_code} "
            f"{self.rcept_no or '-'} {self.state}"
        )
        if self.reason_code:
            head += f":{self.reason_code}"
        shown = ", ".join(
            f"{f.field_key}{'(추후결정)' if f.display == TBD_DISPLAY_KO else ''}"
            for f in self.renderable_fields
        )
        blocked = ", ".join(
            f"{f.field_key}:{f.reason_code}" for f in self.fields.values() if not f.exposable
        )
        if self.exposable:
            body = f"\n      노출 {len(self.renderable_fields)}: {shown or '-'}"
        else:
            body = (
                f"\n      노출 없음 ({self.notice_ko or self.reason_code}) — "
                f"게이트 통과 {len(self.exposable_fields)}건은 기록만"
            )
        return head + body + (f"\n      차단 {blocked}" if blocked else "")


def _blocking_flag(event: Event) -> str | None:
    """The most explanatory blocking flag, in :data:`BLOCKING_FLAGS` order.

    Declaration order is priority order (rights conflict → detail conflict →
    proven split → bare collision), because an event routinely carries several
    and the reason code the operator reads should be the specific one.
    """
    carried = set(event.flags)
    for flag in BLOCKING_FLAGS:
        if flag in carried:
            return flag
    return None


def event_exposure(session: Session, event: Event) -> EventExposure:
    """Derive one event's exposure from persisted state alone. No re-gating.

    Reads only what a run already wrote (``Event.exposure_state`` is refreshed by
    :mod:`mijual.gates.runner`; the flags and gate verdicts are the evidence), so
    P3 can call this on a read-only replica in the request path — the phase
    forbids an OpenDART call there, and this makes none.

    This is the *loading* half; :func:`exposure_of` is the derivation. A caller
    that has already loaded a page of events (``P5.S3``'s board, which batches its
    queries instead of running four per row) calls that one directly — with the
    same inputs, so there is exactly one definition of what an event's exposure is.
    """
    version = current_version(session, event)
    rows: list[Extraction] = []
    if version is not None:
        rows = list(
            session.scalars(
                select(Extraction).where(Extraction.filing_version_id == version.id)
            ).all()
        )
    facts = None
    if event.rights_type is RightsType.CONVERTIBLE_OVERHANG:
        # Local import: ``mijual.cb`` imports this package, so the dependency is
        # resolved at call time.
        from mijual.cb import event_facts

        facts = event_facts(session, event)
    return exposure_of(event, version=version, rows=rows, facts=facts)


def exposure_of(
    event: Event,
    *,
    version: FilingVersion | None,
    rows: "Iterable[Extraction]",
    facts: "ConvertibleFacts | None" = None,
) -> EventExposure:
    """The exposure derivation itself, over rows a caller has already loaded.

    Pure — no session, no query. ``version`` is the event's current readable
    version (:func:`mijual.db.repository.current_version`), ``rows`` are that
    version's :class:`~mijual.db.models.Extraction` rows and ``facts`` is
    :func:`mijual.cb.event_facts` for a ② event (``None`` elsewhere; ``None`` on a
    ② means "no stored detail row", exactly as an absent snapshot does).

    A caller may hand over a **subset** of the version's rows — the board loads
    only the governing countdown field, because a board row renders no field
    values — and gets an exposure whose ``fields`` hold exactly what was passed.
    The event-level verdict does not depend on the rows at all.
    """
    fields: dict[str, FieldView] = {}
    for row in sorted(rows, key=lambda r: r.field_key):
        exposable = row.gate_status in EXPOSABLE_STATUSES
        fields[row.field_key] = FieldView(
            field_key=row.field_key,
            gate_status=row.gate_status,
            reason_code=row.gate_reason_code,
            exposable=exposable,
            display=(TBD_DISPLAY_KO if row.gate_status == TBD else ("value" if exposable else None)),
            value=row.value if exposable and row.gate_status != TBD else None,
            quote=row.quote if exposable else None,
            span=row.span if exposable else None,
            rcept_no=row.rcept_no,
        )

    state, reason, note = _event_state(event, version, facts)
    return EventExposure(
        event_id=event.id,
        corp_code=event.corp_code,
        corp_name=event.corp.corp_name if event.corp else None,
        rights_type=event.rights_type.value if event.rights_type else "?",
        original_rcept_dt=event.original_rcept_dt,
        # The readable version's ``rcept_no``, falling back to the newest one:
        # ② renders with no 본문 at all, and a card with no filing number on it
        # would be unciteable.
        rcept_no=(version or event.latest_version).rcept_no
        if (version or event.latest_version)
        else None,
        state=state,
        reason_code=reason,
        note=note,
        fields=fields,
    )


def _event_state(
    event: Event, version: FilingVersion | None, facts: "ConvertibleFacts | None" = None
) -> tuple[str, str | None, str | None]:
    if event.suppressed_reason:
        return ("suppressed", event.suppressed_reason, event.suppressed_note)
    if "withdrawn" in event.flags:
        return ("withdrawn", "withdrawn", event.exposure_note)
    flag = _blocking_flag(event)
    if flag:
        return ("flagged", flag, BLOCKING_FLAGS[flag])
    if event.rights_type is RightsType.CONVERTIBLE_OVERHANG:
        return _convertible_state(facts)
    if version is None:
        return ("no_document", "no_document", "본문 스냅샷이 없습니다")
    return ("exposable", None, None)


def _convertible_state(facts: "ConvertibleFacts | None") -> tuple[str, str | None, str | None]:
    """②'s arm: the countdown is `API` tier, so the detail row is the requirement.

    Conservative in both directions, like every other rule here: an event with no
    stored detail row is *not* exposed (nothing to render) and *not* suppressed
    (the row may simply not have been fetched yet), and a row missing any
    countdown field names exactly which one in the note rather than rendering a
    card with a blank price or a blank window.
    """
    if facts is None:  # no detail snapshot was loaded for this event at all
        return ("no_detail", "no_detail", "상세 API 스냅샷을 읽을 수 없습니다")
    if facts.complete:
        return ("exposable", None, None)
    if facts.rcept_no is None:
        # No stored detail snapshot at all — not the same thing as a row that
        # says nothing, and it is usually just an uncollected event.
        return ("no_detail", "no_detail", "cvbdIsDecsn 상세 스냅샷이 없습니다")
    # A row exists and is blank or partial. Both are real and both block:
    # 비트플래닛 ``20260616000274`` files a CB row whose 전환 fields are **all** ``-``,
    # and 파이온엑스 ``20260722000285`` states a 38.45 % 오버행 with **no**
    # 전환청구기간 — a dilution whose date the filing does not give.
    names = ", ".join(f"{name}({key})" for key, name in facts.missing)
    return ("incomplete_api_row", "incomplete_api_row", f"필수 API 값 누락: {names}")


def exposure_of_all(
    session: Session, *, rights: RightsType | None = None, include_suppressed: bool = False
) -> list[EventExposure]:
    """Every event's exposure, in a stable order. The report's one source."""
    query = select(Event)
    if rights is not None:
        query = query.where(Event.rights_type == rights)
    if not include_suppressed:
        query = query.where(Event.suppressed_reason.is_(None))
    events = session.scalars(query).all()
    return sorted(
        (event_exposure(session, e) for e in events),
        key=lambda x: (x.rights_type, x.corp_code, x.original_rcept_dt or date.min),
    )
