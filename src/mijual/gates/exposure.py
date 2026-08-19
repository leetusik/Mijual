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

The two are independent on purpose: a blocked event can still hold perfectly
gated fields (they are simply not rendered), and an exposable event can hold
blocked fields (the rest of the card still renders). Both counts are reported.

Only the event's **current readable version** is ever read — the newest version
that has a stored 본문 — because a superseded version's gate verdicts are true
about superseded values, and the countdown must never fall back to them (N4).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from mijual.db.models import Event, Extraction, FilingVersion, RightsType
from mijual.gates.outcome import EXPOSABLE_STATUSES, TBD

__all__ = [
    "BLOCKING_FLAGS",
    "EventExposure",
    "FieldView",
    "WITHDRAWN_NOTICE_KO",
    "current_version",
    "event_exposure",
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


def current_version(session: Session, event: Event) -> FilingVersion | None:
    """The newest version of the event that has a stored 본문 — the only one read.

    Identical selection to the extractor's (``P2.S4``), so the gate judges exactly
    the values the product would show and never a sibling version's.
    """
    from mijual.extract.runner import document_of, readable_versions

    for version in reversed(readable_versions(event)):
        if document_of(session, version) is not None:
            return version
    return None


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
    """
    version = current_version(session, event)
    rows: list[Extraction] = []
    if version is not None:
        rows = list(
            session.scalars(
                select(Extraction).where(Extraction.filing_version_id == version.id)
            ).all()
        )

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

    state, reason, note = _event_state(event, version)
    return EventExposure(
        event_id=event.id,
        corp_code=event.corp_code,
        corp_name=event.corp.corp_name if event.corp else None,
        rights_type=event.rights_type.value if event.rights_type else "?",
        original_rcept_dt=event.original_rcept_dt,
        rcept_no=version.rcept_no if version else None,
        state=state,
        reason_code=reason,
        note=note,
        fields=fields,
    )


def _event_state(event: Event, version: FilingVersion | None) -> tuple[str, str | None, str | None]:
    if event.suppressed_reason:
        return ("suppressed", event.suppressed_reason, event.suppressed_note)
    if "withdrawn" in event.flags:
        return ("withdrawn", "withdrawn", event.exposure_note)
    flag = _blocking_flag(event)
    if flag:
        return ("flagged", flag, BLOCKING_FLAGS[flag])
    if version is None:
        return ("no_document", "no_document", "본문 스냅샷이 없습니다")
    return ("exposable", None, None)


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
