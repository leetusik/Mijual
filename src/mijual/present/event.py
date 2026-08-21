"""One event as a surface may render it: identity, countdown, and its fields.

Three of the trust rules become structural here.

**A blocked field is absent, not blank.** :func:`field_payloads` iterates
:attr:`~mijual.gates.exposure.EventExposure.renderable_fields` — never
``fields`` — so a field whose gate failed has no key in the payload at all. There
is no shape in which it could arrive as ``null``, a dash or a "확인 필요" row
(`states-and-trust.md` §4). The same rule one level up: a blocked *event* has no
renderable fields, so its body is empty by construction.

**추후결정 means no date.** A ``tbd`` field carries ``display: "추후결정"`` and no
value, and :class:`FieldPayload` refuses to be constructed with both — the
superseded date it replaced cannot leak into the contract (`ui-traps.md` #4).

**"지남" is not one thing.** :func:`countdown_of` picks the governing anchor per
rights type and reports a machine ``window_state``; it emits no Korean word for
"past" at all, because ① 지남 is a lapsed right, ③ 지남 is a passed deadline, and
② 지남 means the conversion window is **open right now** (`ui-traps.md` #5). An
② whose 개시일 is behind us comes back ``window_state="open"`` with a ``D+n``
label, and the surface's Korean is the signed 「진행 중」 copy.

Everything is computed against a reference date in **KST** and reported with that
reference beside it, so a stale page can tell that it is stale instead of lying.
The browser only diffs; it never derives (`frontend` v0002, D-10).

The reader payload deliberately carries **no gate reason code**. Why a field is
missing is internal — surfacing it would teach a reader to distrust the rest of
the card in exchange for something they cannot act on. The operator's panel (R7)
reads :class:`~mijual.gates.exposure.EventExposure` directly and is the only
surface that sees reason codes (`states-and-trust.md` §4, D-14).
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from typing import TYPE_CHECKING, Any

from mijual.calc import OPEN, UNKNOWN, d_day, today_kst, window_state
from mijual.gates.exposure import TBD_DISPLAY_KO
from mijual.present.values import iso_day

if TYPE_CHECKING:  # pragma: no cover - imported for types only
    # ``mijual.cb`` is clean, but keeping both here documents the direction:
    # ``present`` derives over inputs a caller already loaded, and imports
    # nothing that reads a database or spends a request.
    from mijual.cb import ConvertibleFacts
    from mijual.gates.exposure import EventExposure, FieldView

__all__ = [
    "COUNTDOWN_LABELS_KO",
    "COUNTDOWN_SOURCES",
    "FIELD_NAMES_KO",
    "RENDERABLE_STATES",
    "Countdown",
    "EventView",
    "FieldPayload",
    "Identity",
    "bare_name",
    "countdown_of",
    "event_view",
    "field_payloads",
    "field_value",
    "identity_of",
]

#: The Korean label above each type's countdown. **Pre-existing copy** — the
#: three strings the P3 grounding pack was exported with (``board-snapshot.md``
#: §"The countdown each type counts down to"), which every round was designed
#: against and R3's contract names as ``countdown.label_ko``. Not invented here.
COUNTDOWN_LABELS_KO: dict[str, str] = {
    "R1": "신주인수권증서 매매 마감",
    "R2": "전환청구 개시",
    "R3": "반대의사 통지 마감",
}

#: Where each countdown's date comes from — carried in the payload so a wrong
#: date is traceable to a field rather than to "the backend".
COUNTDOWN_SOURCES: dict[str, str] = {
    "R1": "warrant_trading_period.end_date",
    "R2": "cvbdIsDecsn.cvrqpd_bgd",
    "R3": "dissent_notice_procedure.notice_end_date",
}

#: ``field_key`` → the Korean row label R3 puts in the 220px label column.
#: Copied verbatim from :data:`mijual.extract.fields.FIELDS` (the source
#: ``copy-inventory.md`` is generated from) and **pinned to it by
#: ``tests/test_present.py``**, rather than imported: importing
#: ``mijual.extract.fields`` pulls the whole extractor tree — client, runner,
#: store — into whatever imports it, and this layer sits on a request path.
FIELD_NAMES_KO: dict[str, str] = {
    "warrant_trading_period": "신주인수권증서 상장·매매기간",
    "subscription_agents": "청약 취급처 (대상자별 증권사 + 청약일)",
    "forfeited_share_method": "실권주 처리 방식",
    "excess_subscription": "초과청약 조건 (비율)",
    "issue_price_formula": "발행가액 산정방법 (1·2차·확정 산식)",
    "refixing_terms": "리픽싱 세부 조건",
    "option_schedule": "콜·풋 세부 스케줄",
    "lockup_release": "보호예수 / 전매제한 해제일",
    "dissent_notice_procedure": "반대의사 통지 방법·절차",
    "correction_interpretation": "정정 해석 (무엇이 바뀌어 D-day가 어떻게 이동했나)",
}

#: States in which an event has a reader surface at all. Everything else —
#: ``suppressed``, ``flagged``, ``no_document``, ``no_detail``,
#: ``incomplete_api_row`` — is simply not on the board and has no detail page.
RENDERABLE_STATES = frozenset({"exposable", "withdrawn"})

_LEGAL_FORMS = ("주식회사", "(주)", "㈜", "(株)")


def bare_name(name: str | None) -> str:
    """A company name without its legal-form suffix or spacing, for comparison.

    The one definition of *the same company, written differently*: it is what
    :func:`identity_of` compares a 본문 header against, and what
    :func:`mijual.web.reads.resolve_corp` matches a reader's 종목명 against, so
    ``한화솔루션(주)``, ``한화솔루션`` and ``한화 솔루션`` cannot mean one company in
    one place and three in another.
    """
    bare = name or ""
    for form in _LEGAL_FORMS:
        bare = bare.replace(form, "")
    return "".join(bare.split())


# ---------------------------------------------------------------------------
# identity
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Identity:
    """Which company a card claims to be about, and whether the filing agrees.

    ``rcept_no 20250930000508`` stores the DART master name **풍전약품** while its
    own 본문 header reads **에스씨엠생명과학 주식회사**. It is a master-data
    artifact and affects display only — the 전환가액, the 오버행 and the
    전환청구기간 are all correct — so R3's rule is to show the master name and
    **state** the disagreement rather than silently correct it (`ui-traps.md` #3).

    The ordinary case is not a disagreement: a filing routinely prints the legal
    form (``한화솔루션(주)`` against master ``한화솔루션``), and comparing bare
    names keeps that out of the payload.
    """

    #: What the card displays. Always the DART master name.
    corp_name: str | None
    #: What the current 본문 prints, when it was read.
    corp_name_in_body: str | None = None
    #: ``None`` when there is no 본문 name to compare — an unknown is not a
    #: disagreement, and ② renders with no 본문 at all.
    corp_name_agrees_with_body: bool | None = None

    def payload(self) -> dict[str, Any]:
        out: dict[str, Any] = {"corp_name": self.corp_name}
        if self.corp_name_in_body is not None:
            out["corp_name_in_body"] = self.corp_name_in_body
            out["corp_name_agrees_with_body"] = self.corp_name_agrees_with_body
        return out


def identity_of(exposure: "EventExposure", corp_name_in_body: str | None = None) -> Identity:
    """Compare the master name against the 본문's, ignoring legal-form suffixes."""
    if corp_name_in_body is None:
        return Identity(corp_name=exposure.corp_name)
    return Identity(
        corp_name=exposure.corp_name,
        corp_name_in_body=corp_name_in_body,
        corp_name_agrees_with_body=(
            bare_name(exposure.corp_name) == bare_name(corp_name_in_body)
        ),
    )


# ---------------------------------------------------------------------------
# fields
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class FieldPayload:
    """One gate-passing field, with the citation triple that answers "왜 이 값?"."""

    field_key: str
    #: The Korean row label (:data:`FIELD_NAMES_KO`).
    korean_name: str | None
    #: ``"value"`` → render ``value``; ``"추후결정"`` → render the badge alone.
    display: str
    #: ``None`` iff ``display == "추후결정"``. The extraction's normalized shape
    #: (an ISO date string, a decimal ratio, an object) — passed through, never
    #: reformatted: a quote and its value must keep saying the same thing.
    value: Any
    #: Always ``False``. A ``FieldView`` is a reading of a filing, never a
    #: derivation — carried anyway so **every** value in the contract answers the
    #: same question in the same key. See :class:`~mijual.present.values.Figure`.
    estimated: bool
    quote: str | None = None
    span: tuple[int, int] | None = None
    rcept_no: str | None = None

    def __post_init__(self) -> None:
        if self.estimated:
            raise ValueError("a field read from a filing is a fact and never carries 「추정」")
        if self.display == TBD_DISPLAY_KO and self.value is not None:
            raise ValueError(
                "추후결정 means *no date*, not an unknown one: a tbd field carries "
                "no value, and never the superseded date it replaced (ui-traps #4)"
            )

    @property
    def tbd(self) -> bool:
        return self.display == TBD_DISPLAY_KO

    def payload(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "field_key": self.field_key,
            "display": self.display,
            "estimated": self.estimated,
        }
        if self.korean_name is not None:
            out["korean_name"] = self.korean_name
        if self.value is not None:
            out["value"] = self.value
        if self.quote is not None:
            out["quote"] = self.quote
        if self.span is not None:
            out["span"] = list(self.span)
        if self.rcept_no is not None:
            out["rcept_no"] = self.rcept_no
        return out


def _field_payload(view: "FieldView") -> FieldPayload:
    return FieldPayload(
        field_key=view.field_key,
        korean_name=FIELD_NAMES_KO.get(view.field_key),
        display=view.display or "value",
        value=view.value,
        estimated=False,
        quote=view.quote,
        span=tuple(view.span) if view.span else None,
        rcept_no=view.rcept_no,
    )


def field_payloads(exposure: "EventExposure") -> dict[str, FieldPayload]:
    """Every field the product may show, keyed by ``field_key``.

    Reads ``renderable_fields``, so a gate-blocked field — and every field of a
    blocked event — is **missing from the mapping**, which is the only shape in
    which a surface can render "around the hole as if the row had never existed".
    """
    return {view.field_key: _field_payload(view) for view in exposure.renderable_fields}


def field_value(exposure: "EventExposure", field_key: str) -> Any:
    """A gate-passing field's value, or ``None``. Never a blocked field's.

    The one accessor any derivation should use to reach into an event's fields:
    it returns ``None`` for a blocked field *and* for a ``추후결정`` one, so a
    caller cannot accidentally read a value the contract says does not exist.
    """
    view = exposure.fields.get(field_key)
    if view is None or not view.exposable or view.display == TBD_DISPLAY_KO:
        return None
    return view.value


# ---------------------------------------------------------------------------
# countdown
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Countdown:
    """The one date a rights type counts down to, decided upstream and in KST.

    ``date`` is a bare calendar day and ``dday``/``days`` are computed against
    ``reference`` — the KST day the server used. Both travel together so a page
    served an hour ago can be recognised as stale rather than believed.
    """

    label_ko: str
    #: ``None`` when the schedule is 추후결정 or the field is not renderable.
    #: **No date field ever sits beside a 추후결정 badge.**
    date: str | None
    #: ``D-5`` / ``D-DAY`` / ``D+41`` — :attr:`mijual.calc.DDay.label`.
    dday: str | None
    days: int | None
    #: The governing window, ``(start, end)``. For ② this is 전환청구기간, whose
    #: **start** is the anchor: the window can be open while the anchor is past.
    window: tuple[str | None, str | None]
    #: ``upcoming`` / ``open`` / ``closed`` / ``unknown``. Machine tokens; the
    #: Korean is the surface's, and it differs per rights type.
    window_state: str
    #: The KST calendar day ``dday`` was computed against.
    reference: str
    source: str

    @property
    def is_open(self) -> bool:
        return self.window_state == OPEN

    @property
    def is_past(self) -> bool:
        """The anchor is behind the reference day. **Not** the same as 종료.

        For ② this is true of every event whose 전환청구 has opened — the
        dilution is live right now. Ask :attr:`is_open` before writing Korean.
        """
        return self.days is not None and self.days < 0

    def payload(self) -> dict[str, Any]:
        return {
            "label_ko": self.label_ko,
            "date": self.date,
            "dday": self.dday,
            "days": self.days,
            "window": list(self.window),
            "window_state": self.window_state,
            "reference": self.reference,
            "source": self.source,
        }


def _anchor(
    exposure: "EventExposure", facts: "ConvertibleFacts | None"
) -> tuple[date | None, date | None, date | None]:
    """``(anchor, window_start, window_end)`` for one event's governing date."""
    rights = exposure.rights_type
    if rights == "R1":
        value = field_value(exposure, "warrant_trading_period")
        if isinstance(value, Mapping):
            start = _as_date(value.get("start_date"))
            end = _as_date(value.get("end_date"))
            return (end, start, end)
        return (None, None, None)
    if rights == "R2":
        if facts is None:
            # Loud rather than silently dateless: an exposable ② event *always*
            # has a complete ``cvbdIsDecsn`` row (that is what makes it
            # exposable), so reaching here means the caller forgot to load it —
            # and a board row with a missing countdown looks like data, not a bug.
            raise ValueError(
                "② counts down to an API-tier date: pass facts=event_facts(session, event)"
            )
        # ②'s countdown is API tier (N6) — 전환가액·전환청구기간·오버행 all come
        # from ``cvbdIsDecsn``, never from a 본문 reading, which is why an ② event
        # renders with zero FieldViews and still has a complete countdown.
        return (facts.request_begin, facts.request_begin, facts.request_end)
    value = field_value(exposure, "dissent_notice_procedure")
    if isinstance(value, Mapping):
        start = _as_date(value.get("notice_start_date"))
        end = _as_date(value.get("notice_end_date"))
        return (end, start, end)
    return (None, None, None)


def _as_date(value: Any) -> date | None:
    text = iso_day(value)
    return date.fromisoformat(text) if text else None


def countdown_of(
    exposure: "EventExposure",
    *,
    facts: "ConvertibleFacts | None" = None,
    today: date | None = None,
) -> Countdown:
    """The governing countdown of one event. Pure; ``today`` defaults to KST now.

    ``facts`` is required for ② and ignored otherwise — pass the event's
    :func:`mijual.cb.event_facts` result. A **non-exposable** event gets a
    dateless countdown even when a date exists: 철회 replaces the card body, and
    R3 is explicit that it shows "no fields, no countdown, no old dates".
    """
    rights = exposure.rights_type
    label = COUNTDOWN_LABELS_KO.get(rights, "")
    source = COUNTDOWN_SOURCES.get(rights, "")
    reference = today or today_kst()
    if not exposure.exposable:
        return Countdown(
            label_ko=label,
            date=None,
            dday=None,
            days=None,
            window=(None, None),
            window_state=UNKNOWN,
            reference=reference.isoformat(),
            source=source,
        )

    anchor, start, end = _anchor(exposure, facts)
    countdown = d_day(anchor, reference)
    return Countdown(
        label_ko=label,
        date=iso_day(anchor),
        dday=countdown.label if countdown else None,
        days=countdown.days if countdown else None,
        window=(iso_day(start), iso_day(end)),
        window_state=window_state(start, end, reference) if anchor else UNKNOWN,
        reference=reference.isoformat(),
        source=source,
    )


# ---------------------------------------------------------------------------
# the whole event
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class EventView:
    """One event as a board row or a detail page reads it. No reason codes."""

    event_id: int
    corp_code: str
    rights_type: str
    rcept_no: str | None
    original_rcept_dt: str | None
    #: ``exposable`` or ``withdrawn`` on any surface a reader can reach.
    state: str
    #: The locked 철회 sentence for this rights type, on a withdrawn event only.
    notice_ko: str | None
    identity: Identity
    countdown: Countdown
    fields: dict[str, FieldPayload]

    @property
    def renderable(self) -> bool:
        """Does a reader surface exist for this event at all?

        ``False`` means "not on the board and no detail page" — a suppressed,
        flagged or incomplete event. A caller serving a detail route answers
        ``404`` rather than rendering an empty page: an event that is not
        exposed must not become a surface that explains why it is not exposed.
        """
        return self.state in RENDERABLE_STATES

    def payload(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "event_id": self.event_id,
            "corp_code": self.corp_code,
            "rights_type": self.rights_type,
            "rcept_no": self.rcept_no,
            "original_rcept_dt": self.original_rcept_dt,
            "state": self.state,
            "countdown": self.countdown.payload(),
            "fields": {key: value.payload() for key, value in self.fields.items()},
        }
        out.update(self.identity.payload())
        if self.notice_ko is not None:
            out["notice_ko"] = self.notice_ko
        return out


def event_view(
    exposure: "EventExposure",
    *,
    facts: "ConvertibleFacts | None" = None,
    corp_name_in_body: str | None = None,
    today: date | None = None,
) -> EventView:
    """Compose identity + countdown + fields for one already-loaded event."""
    return EventView(
        event_id=exposure.event_id,
        corp_code=exposure.corp_code,
        rights_type=exposure.rights_type,
        rcept_no=exposure.rcept_no,
        original_rcept_dt=iso_day(exposure.original_rcept_dt),
        state=exposure.state,
        notice_ko=exposure.notice_ko,
        identity=identity_of(exposure, corp_name_in_body),
        countdown=countdown_of(exposure, facts=facts, today=today),
        fields=field_payloads(exposure),
    )
