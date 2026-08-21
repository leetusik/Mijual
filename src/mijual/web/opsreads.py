"""The read layer behind 운영 관제 — every number from a source that already owns it.

R7's hard rule for this panel is the shortest one in the whole design:
**발명 수치 금지 — 모든 숫자는 CLI/report/설정에서.** So nothing here computes a
figure of its own. Each block names the source it re-reads:

===================  =======================================================
개요 tiles           the persisted exposure contract (:mod:`mijual.gates`) —
                     the same rows ``python -m mijual.gates summary`` renders
beat 스케줄          :data:`mijual.beat.BEAT_ENTRIES`, the one declaration the
                     Celery beat schedule is built from ("설정이 곧 진실")
최근 실행 표         :class:`~mijual.db.models.PipelineRun`, written by the
                     scheduler from its own report — ▷ line verbatim
lock 칩              Redis, live, under :func:`mijual.beat.lock_key`
게이트 대기열        stored :class:`~mijual.db.models.Extraction` rows and the
                     Korean the gate layer already owns
                     (:data:`mijual.gates.outcome.REASON_LABELS_KO`)
정확도               ``mijual.evalset``'s two **frozen JSON artifacts** — no DB
LLM 스펜드           :class:`~mijual.db.models.ExtractionCall` aggregates
DART 요청 스펜드     the run log's own per-run request counts, per KST day
독자 계정            :class:`~mijual.db.models.Account` + its own tables
===================  =======================================================

Four prohibitions this module keeps structurally rather than carefully:

* **Read-only.** Not one function here writes. §6.5: the panel has no mutation
  endpoint at all, because a click that could override a deterministic gate
  verdict would make the "a failed field is never shown" guarantee worthless.
* **Suppression and reason codes travel raw.** A code the gate layer has Korean
  for carries it (that Korean is the code's own, from
  ``REASON_LABELS_KO``); a code it does not carries **no** ``reason_ko`` key at
  all. §6.1: 한국어 렌더 함수를 만들지 말 것; 미지 코드도 코드 그대로, 폴백 문구
  금지.
* **``▷`` stays ``▷``.** In this panel it is pipeline output quoted verbatim, and
  swapping it for 「추정」 would move the estimate mark across the boundary that
  defines it (경계 = 출처). Everywhere else in the product 「추정」 is the only mark.
* **No 계정↔대화 join exists, at any level.** The 사용자 tab is two independent
  reads: :func:`reader_accounts` here and
  :meth:`mijual.web.conversations.Conversations.sessions` from the port. There is
  no query in this module that touches both.

A note on cost, because the panel is desktop-only and one operator deep: the
비싼 block is :func:`gate_summary`, which walks the exposable events the same way
``/board`` does (batched current versions, one extraction query). Everything else
is one or two aggregates.
"""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload, selectinload

from mijual.beat import BEAT_ENTRIES, PIPELINE_LOCK_NAME, TIMEZONE, lock_key
from mijual.config import Settings
from mijual.db.models import (
    Account,
    Event,
    Extraction,
    ExtractionCall,
    Holding,
    NotificationPref,
    PipelineRun,
)
from mijual.db.repository import current_versions
from mijual.gates.exposure import BLOCKING_FLAGS, WITHDRAWN_NOTICE_KO, event_exposure
from mijual.gates.outcome import REASON_LABELS_KO
from mijual.present import FIELD_NAMES_KO
from mijual.web import clock
from mijual.web.portfolio import DEFAULT_LEAD_DAYS, lead_days_of

__all__ = [
    "DART_DAILY_QUOTA",
    "DART_VIEWER",
    "EXPOSABLE_STATUSES",
    "RUN_LOG_LIMIT",
    "accuracy",
    "beat_view",
    "gate_rows",
    "gate_summary",
    "lock_state",
    "reader_accounts",
    "run_log",
    "spend",
]

#: The operator's stated OpenDART ceiling (decisions **O-1** / `operations`):
#: 20,000 requests per key per day. It is an operator fact, not a scraped or
#: measured one, and it is served with that provenance so the tab's quota bar can
#: say where the denominator came from.
DART_DAILY_QUOTA = 20_000
#: Where a filing number resolves. The panel links every ``rcept_no`` (R7:
#: "rcept_no verbatim + DART 링크").
DART_VIEWER = "https://dart.fss.or.kr/dsaf001/main.do?rcpNo="
#: Only these two are ever shown (``mijual.gates.outcome``); everything else is a
#: withheld field with a recorded reason, which is what this panel exists to list.
EXPOSABLE_STATUSES = ("passed", "tbd")
#: How many runs the 최근 실행 표 asks for by default. A schedule fires three times
#: a day, so this is about a fortnight — enough to see a missed beat in context.
RUN_LOG_LIMIT = 40
#: How far back :func:`beat_view` reports the schedule's due times. The 개요 tab
#: derives R7's 「실행 기록 없음」 row by matching these against the run log.
BEAT_LOOKBACK = timedelta(days=3)


# ---------------------------------------------------------------------------
# 개요 — the four status tiles
# ---------------------------------------------------------------------------
def _reason_entry(code: str | None, count: int, **extra: Any) -> dict[str, Any]:
    """One reason/suppression code row: the code raw, its own Korean if it has one.

    ``reason_ko`` is **absent** for a code the gate layer has no Korean for — not
    an empty string and not a fallback phrase. §6.1 signs the raw code as the
    rendering, so a missing translation is a rendering the design already chose.
    """
    row: dict[str, Any] = {"code": code or "", "count": count}
    korean = REASON_LABELS_KO.get(code or "")
    if korean:
        row["reason_ko"] = korean
    row.update({k: v for k, v in extra.items() if v is not None})
    return row


def _event_state_counts(session: Session) -> tuple[Counter, Counter, Counter, int, int]:
    """Per-``rights:state`` counts, blocked reasons, suppression reasons, totals.

    Read off the **persisted** exposure columns, which is what ``gates summary``
    reports and what "마지막 측정 시각" times: this tab shows what the last gate run
    measured, not what a fresh derivation would say this second. (A reader surface
    does the opposite — ``P5.S3`` note 12 — because a reader must never be shown a
    row the contract would refuse.)
    """
    by_state: Counter = Counter()
    blocked: Counter = Counter()
    suppressed: Counter = Counter()
    considered = exposable = 0
    for rights, state, reason, suppress_reason, count in session.execute(
        select(
            Event.rights_type,
            Event.exposure_state,
            Event.exposure_reason,
            Event.suppressed_reason,
            func.count(),
        ).group_by(
            Event.rights_type,
            Event.exposure_state,
            Event.exposure_reason,
            Event.suppressed_reason,
        )
    ).all():
        rights_id = rights.value if rights is not None else "?"
        if suppress_reason is not None:
            suppressed[suppress_reason] += count
            continue
        # ``gates summary``'s own universe: suppressed events are counted apart.
        considered += count
        by_state[f"{rights_id}:{state or 'unmeasured'}"] += count
        if state == "exposable":
            exposable += count
        elif reason:
            blocked[reason] += count
    return by_state, blocked, suppressed, considered, exposable


def _renderable_fields(session: Session) -> tuple[Counter, Counter]:
    """Gate-passing fields on the current version of each exposable event.

    The same rule the board loads rows with (:func:`current_versions`): a field
    only counts if it sits on the version the product would actually render.
    """
    events = list(
        session.scalars(
            select(Event)
            .where(Event.exposure_state == "exposable")
            .options(selectinload(Event.versions))
        ).all()
    )
    version_ids = [v.id for v in current_versions(session, events).values()]
    shown: Counter = Counter()
    tbd: Counter = Counter()
    if not version_ids:
        return shown, tbd
    for field_key, status, count in session.execute(
        select(Extraction.field_key, Extraction.gate_status, func.count())
        .where(
            Extraction.filing_version_id.in_(version_ids),
            Extraction.gate_status.in_(EXPOSABLE_STATUSES),
        )
        .group_by(Extraction.field_key, Extraction.gate_status)
    ).all():
        shown[field_key] += count
        if status == "tbd":
            tbd[field_key] += count
    return shown, tbd


def gate_summary(session: Session) -> dict[str, Any]:
    """The four 개요 tiles — ``gates summary`` 값 그대로, as structured facts.

    Events 노출/고려 (and per rights type) · field verdict split · renderable
    fields · when the gate layer last measured any of it.
    """
    by_state, blocked, suppressed, considered, exposable = _event_state_counts(session)
    verdicts: Counter = Counter()
    for status, count in session.execute(
        select(Extraction.gate_status, func.count()).group_by(Extraction.gate_status)
    ).all():
        verdicts[status or "unjudged"] += count
    shown, tbd = _renderable_fields(session)
    measured_at = session.scalar(select(func.max(Event.exposure_checked_at)))

    body: dict[str, Any] = {
        "events": {
            "considered": considered,
            "exposable": exposable,
            "suppressed": sum(suppressed.values()),
            "by_state": dict(sorted(by_state.items())),
            # Raw English, both of them (§6.1). ``blocked`` is a flag or 철회 on an
            # event the corpus keeps; ``suppressed`` is an event the collector's
            # filter set aside, and P5.S5 added ``foreign_correction_head`` to it.
            "blocked": [
                _reason_entry(code, count)
                for code, count in sorted(blocked.items(), key=lambda kv: (-kv[1], kv[0]))
            ],
            "suppressed_reasons": [
                {"code": code, "count": count}
                for code, count in sorted(suppressed.items(), key=lambda kv: (-kv[1], kv[0]))
            ],
            # The four blocking flags, with the Korean the **code** carries
            # (``BLOCKING_FLAGS``) — not a rendering invented for this panel.
            "blocking_flags": [
                {"code": code, "reason_ko": korean} for code, korean in BLOCKING_FLAGS.items()
            ],
        },
        "fields": {
            "verdicts": {
                key: verdicts.get(key, 0)
                for key in ("passed", "tbd", "failed", "not_evaluable", "unjudged")
            },
            "stored_rows": sum(verdicts.values()),
            "renderable": {
                "total": sum(shown.values()),
                "by_field": [
                    {
                        "field_key": key,
                        "korean_name": FIELD_NAMES_KO.get(key),
                        "count": count,
                        "tbd": tbd.get(key, 0),
                    }
                    for key, count in sorted(shown.items())
                ],
            },
        },
    }
    if measured_at is not None:
        body["measured_at"] = clock.iso(measured_at)
    return body


# ---------------------------------------------------------------------------
# 개요 — the beat schedule, rendered from the configuration itself
# ---------------------------------------------------------------------------
def beat_view(*, now: datetime | None = None, lookback: timedelta = BEAT_LOOKBACK) -> dict[str, Any]:
    """The beat schedule and, per entry, when it was due in the recent past.

    R7 requires the table to be rendered **from the Celery beat configuration**
    (하드코딩 금지), and requires a scheduled beat that did not run to show as an
    「실행 기록 없음」 row in alert ink, *derived from its due time*. This serves the
    schedule's half of that derivation — every instant an entry was due — and the
    run log serves the other half. **No row is fabricated here**: a gap is the
    client's join of two truthful lists, not a record the backend minted.
    """
    reference = now or clock.now()
    since = reference - lookback
    return {
        "timezone": TIMEZONE,
        "as_of": clock.iso(reference),
        "entries": [
            entry.as_dict()
            | {"due": [clock.iso(moment) for moment in entry.due_between(since, reference)]}
            for entry in BEAT_ENTRIES
        ],
        "due_since": clock.iso(since),
    }


# ---------------------------------------------------------------------------
# 개요 — the run log
# ---------------------------------------------------------------------------
def _run_payload(row: PipelineRun) -> dict[str, Any]:
    body: dict[str, Any] = {
        "id": row.id,
        "label": row.label,
        "trigger": row.trigger,
        "started_at": clock.iso(row.started_at),
        "window": [row.window_bgn, row.window_end],
        "lock": row.lock,
        "requests": row.requests or 0,
        "calls": row.calls or 0,
        "stages": list(row.stages or []),
    }
    # A run in flight has no finished_at, no verdict and no spend line yet — and
    # says so by omission rather than by a zero that would read as "cost nothing".
    for key, value in (
        ("finished_at", clock.iso(row.finished_at) if row.finished_at else None),
        ("seconds", row.seconds),
        ("ok", row.ok),
        ("cost_usd", row.cost_usd),
        # Verbatim, ▷ included: this is the pipeline's own sentence (경계 = 출처).
        ("spend_line", row.spend_line),
        ("config", row.config_line),
    ):
        if value is not None:
            body[key] = value
    if row.notes:
        body["notes"] = list(row.notes)
    return body


def run_log(session: Session, *, limit: int = RUN_LOG_LIMIT) -> dict[str, Any]:
    """최근 실행 표 — newest first, each row the run's own report."""
    rows = list(
        session.scalars(
            select(PipelineRun).order_by(PipelineRun.started_at.desc(), PipelineRun.id.desc()).limit(limit)
        ).all()
    )
    total = session.scalar(select(func.count()).select_from(PipelineRun)) or 0
    return {"count": total, "limit": limit, "rows": [_run_payload(row) for row in rows]}


def _open_run(session: Session) -> PipelineRun | None:
    """The most recent run that opened a row and never closed it."""
    return session.scalars(
        select(PipelineRun)
        .where(PipelineRun.finished_at.is_(None))
        .order_by(PipelineRun.started_at.desc())
        .limit(1)
    ).first()


# ---------------------------------------------------------------------------
# 개요 — the lock chip
# ---------------------------------------------------------------------------
def lock_state(
    settings: Settings, session: Session | None = None, *, name: str = PIPELINE_LOCK_NAME
) -> dict[str, Any]:
    """``mijual:lock:pipeline``, live from Redis — degraded honestly, never a 500.

    Redis is optional at request time: the panel is a **read** of the pipeline's
    state, and a broker that is down is one more thing an operator wants to see,
    not a reason for the tab to fail. So an unreachable Redis is reported as
    ``state: "unknown"`` with the reason, and the rest of the tab renders.

    ``since`` comes from the run log, not from the lock: the lock value is an
    owner token and holds no start time, so inventing one from its TTL would be a
    fabricated number. An in-flight run has a row with no ``finished_at``, and
    that row's ``started_at`` is a real fact about the run holding the lock.
    """
    body: dict[str, Any] = {"name": name, "key": lock_key(name), "source": "redis"}
    try:
        import redis  # local import: the package is only needed here

        client = redis.Redis.from_url(
            settings.redis_url, socket_connect_timeout=1, socket_timeout=1
        )
        raw = client.get(lock_key(name))
        ttl = client.ttl(lock_key(name))
    except Exception as exc:  # noqa: BLE001 - any redis/transport failure degrades
        body["state"] = "unknown"
        body["reason"] = type(exc).__name__
        return body

    if raw is None:
        body["state"] = "free"
        return body
    body["state"] = "held"
    body["holder"] = raw.decode("utf-8", "replace") if isinstance(raw, bytes) else str(raw)
    if isinstance(ttl, int) and ttl >= 0:
        body["ttl_seconds"] = ttl
        body["expires_at"] = clock.iso(clock.now() + timedelta(seconds=ttl))
    if session is not None:
        open_run = _open_run(session)
        if open_run is not None:
            body["since"] = clock.iso(open_run.started_at)
            body["run_id"] = open_run.id
    return body


# ---------------------------------------------------------------------------
# 게이트 대기열
# ---------------------------------------------------------------------------
def _gate_basis(session: Session) -> tuple[list[tuple], int, int]:
    """Every stored gate verdict as ``(status, reason, rcept_no, field_key)``.

    One small query over four columns, counted in Python, because the rate's
    denominator is **distinct ``(rcept_no, field_key)``** and a portable
    multi-column ``COUNT(DISTINCT …)`` is not worth a dialect branch here. R7
    states the basis explicitly (중복 16행 주의), so the panel serves the
    denominator beside the counts and never leaves a rate's basis implicit.
    """
    rows = session.execute(
        select(
            Extraction.gate_status,
            Extraction.gate_reason_code,
            Extraction.rcept_no,
            Extraction.field_key,
        )
    ).all()
    stored = len(rows)
    distinct = len({(r[2], r[3]) for r in rows})
    return list(rows), stored, distinct


def _blocked_field(view) -> dict[str, Any]:
    """One withheld field of an event: which field, and the reason code raw."""
    body: dict[str, Any] = {
        "field_key": view.field_key,
        "gate_status": view.gate_status or "unjudged",
    }
    korean = FIELD_NAMES_KO.get(view.field_key)
    if korean:
        body["korean_name"] = korean
    if view.reason_code:
        body["reason_code"] = view.reason_code
        reason_ko = REASON_LABELS_KO.get(view.reason_code)
        if reason_ko:
            body["reason_ko"] = reason_ko
    return body


def _withdrawal_rows(session: Session) -> list[dict[str, Any]]:
    """철회 이벤트 검사 — notice + note verbatim, and what stays recorded-only."""
    events = list(
        session.scalars(
            select(Event)
            .where(Event.exposure_state == "withdrawn")
            .options(joinedload(Event.corp), selectinload(Event.versions))
        ).unique().all()
    )
    out: list[dict[str, Any]] = []
    for event in sorted(events, key=lambda e: (e.rights_type.value, e.corp_code)):
        exposure = event_exposure(session, event)
        row: dict[str, Any] = {
            "event_id": event.id,
            "corp_code": event.corp_code,
            "corp_name": event.corp.corp_name if event.corp else None,
            "rights_type": event.rights_type.value,
            "rcept_no": exposure.rcept_no,
            # The product's own string for this state, from the code that owns it.
            "notice_ko": WITHDRAWN_NOTICE_KO.get(event.rights_type.value),
            # The evidence line the gate run wrote, verbatim.
            "note": event.exposure_note,
            # Gate-passing fields that will never render: the whole point of the
            # 철회 page is that the notice replaces the body (R3).
            "gate_passed_unrendered": len(exposure.exposable_fields),
            "blocked": [
                _blocked_field(view)
                for view in sorted(exposure.fields.values(), key=lambda f: f.field_key)
                if not view.exposable
            ],
        }
        if exposure.rcept_no:
            row["dart_url"] = f"{DART_VIEWER}{exposure.rcept_no}"
        out.append(row)
    return out


def gate_queue(session: Session) -> dict[str, Any]:
    """reason_code counts, the distinct-basis rates, event states and 철회 inspect.

    §6.5 순수 관찰: no action, no status bit, nothing that could change a verdict.
    """
    rows, stored, distinct_total = _gate_basis(session)
    stored_counts: Counter = Counter()
    distinct_pairs: dict[tuple[str | None, str | None], set] = {}
    for status, reason, rcept_no, field_key in rows:
        key = (status, reason)
        stored_counts[key] += 1
        distinct_pairs.setdefault(key, set()).add((rcept_no, field_key))

    reasons = []
    for (status, reason), count in sorted(
        stored_counts.items(), key=lambda kv: (-kv[1], str(kv[0]))
    ):
        seen = len(distinct_pairs[(status, reason)])
        reasons.append(
            _reason_entry(
                reason,
                count,
                gate_status=status or "unjudged",
                distinct_count=seen,
                # Exact string, not a rounded float: the same serialization rule
                # every ratio in this product follows.
                rate=f"{seen / distinct_total:.4f}" if distinct_total else None,
            )
        )
    withdrawn = _withdrawal_rows(session)
    return {
        "basis": {
            "stored_rows": stored,
            "distinct_rows": distinct_total,
            "duplicates": stored - distinct_total,
            "key": "(rcept_no, field_key)",
        },
        "reasons": reasons,
        "events": gate_summary(session)["events"],
        "withdrawn": {"count": len(withdrawn), "rows": withdrawn},
    }


def gate_rows(
    session: Session,
    *,
    field_key: str | None = None,
    reason_code: str | None = None,
    gate_status: str | None = None,
    rcept_no: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> dict[str, Any]:
    """행 검사 — one page of stored gate verdicts, with their evidence or its absence.

    A blocked row usually has no quote and no span. Both keys are then **absent**
    from the payload: R7 says 「없음」 is a state to render and forbids a
    placeholder, and the contract-wide rule is that an absent value is an absent
    key rather than a ``null`` the client has to special-case.
    """
    query = (
        select(Extraction, Event)
        .join(Event, Extraction.event_id == Event.id)
        .options(joinedload(Event.corp))
    )
    if field_key:
        query = query.where(Extraction.field_key == field_key)
    if reason_code:
        query = query.where(Extraction.gate_reason_code == reason_code)
    if gate_status:
        query = query.where(Extraction.gate_status == gate_status)
    if rcept_no:
        query = query.where(Extraction.rcept_no == rcept_no)

    total = session.scalar(select(func.count()).select_from(query.subquery())) or 0
    records = session.execute(
        query.order_by(Extraction.field_key, Extraction.rcept_no, Extraction.id)
        .limit(limit)
        .offset(offset)
    ).all()

    out: list[dict[str, Any]] = []
    for row, event in records:
        body: dict[str, Any] = {
            "id": row.id,
            "rcept_no": row.rcept_no,
            "event_id": row.event_id,
            "rights_type": event.rights_type.value if event.rights_type else None,
            "corp_code": event.corp_code,
            "corp_name": event.corp.corp_name if event.corp else None,
            "field_key": row.field_key,
            "gate_status": row.gate_status or "unjudged",
            "status": row.status,
            "span_status": row.span_status,
            "exposable": row.gate_status in EXPOSABLE_STATUSES,
        }
        korean = FIELD_NAMES_KO.get(row.field_key)
        if korean:
            body["korean_name"] = korean
        if row.gate_reason_code:
            body["reason_code"] = row.gate_reason_code
            reason_ko = REASON_LABELS_KO.get(row.gate_reason_code)
            if reason_ko:
                body["reason_ko"] = reason_ko
        if row.gate_note:
            body["gate_note"] = row.gate_note
        if row.value_summary:
            body["value_summary"] = row.value_summary
        if row.quote:
            body["quote"] = row.quote
        if row.span is not None:
            body["span"] = list(row.span)
        if row.rcept_no:
            body["dart_url"] = f"{DART_VIEWER}{row.rcept_no}"
        out.append(body)
    return {"count": total, "limit": limit, "offset": offset, "rows": out}


# ---------------------------------------------------------------------------
# 정확도 — the evalset report, from its frozen artifacts
# ---------------------------------------------------------------------------
def _bucket(bucket) -> dict[str, Any]:
    body: dict[str, Any] = {
        "judged": bucket.judged,
        "correct": bucket.correct,
        "partial": bucket.partial,
        "wrong": bucket.wrong,
        "skipped": bucket.skipped,
        "unlabelled": bucket.unlabelled,
    }
    for key, value in (("strict", bucket.strict), ("lenient", bucket.lenient)):
        if value is not None:
            body[key] = f"{value:.4f}"
    interval = bucket.interval()
    if interval is not None:
        body["interval"] = [f"{interval[0]:.4f}", f"{interval[1]:.4f}"]
    return body


def _blocked_bucket(bucket) -> dict[str, Any]:
    """A blocked bucket plus 과차단 — the share the judge called correct anyway."""
    body = _bucket(bucket)
    if bucket.judged:
        body["over_block_rate"] = f"{bucket.correct / bucket.judged:.4f}"
    return body


def _field_score(score) -> dict[str, Any]:
    """One field's row, with every decomposition R7 requires beside its rate.

    A rate is never served alone: ``shown``/``blocked`` carry their n and their
    interval, ``block_rate`` carries ``corpus_blocked``/``corpus_total``, and
    ``over_blocked_estimate`` (the ▷ count of corpus rows withheld though correct)
    carries the rate it came from. "분해 없이 단독 인용되는 레이아웃 금지."
    """
    blocked = _blocked_bucket(score.blocked)
    if score.over_blocked_estimate is not None:
        # Beside the rate it was computed from, never on its own: this is a ▷
        # projection of the judged sample onto ``corpus_blocked``, and quoting the
        # count without the rate and the denominator is the layout R7 forbids.
        blocked["over_blocked_estimate"] = f"{score.over_blocked_estimate:.1f}"
    body: dict[str, Any] = {
        "field_key": score.field_key,
        "korean_name": score.field_ko,
        "shown": _bucket(score.shown),
        "blocked": blocked,
        "corpus_total": score.corpus_total,
        "corpus_blocked": score.corpus_blocked,
        "corpus_reasons": [
            _reason_entry(code, count)
            for code, count in sorted(score.corpus_reasons.items(), key=lambda kv: (-kv[1], kv[0]))
        ],
    }
    if score.block_rate is not None:
        body["block_rate"] = f"{score.block_rate:.4f}"
    return body


def accuracy() -> dict[str, Any]:
    """What ``python -m mijual.evalset report`` prints, plus its own decomposition.

    **The frozen JSON artifacts, never the database** (R7: 프로즌 JSON 2개, DB 접근
    금지) — a label is only true about the reading it was made on, so the report is
    regenerable long after the corpus has moved.

    Two things travel together on purpose. ``markdown`` is the CLI's exact output,
    so the tab can never quote a number the command does not print; ``judged_by``
    is served **beside every rate**, because R7 forbids rendering the headline
    accuracy without its 판정 출처 — and the block is read off ``labels.json``, so
    a re-judging updates it with no code change. Each rate also carries its own
    decomposition (n, the interval, the corpus denominator) because R7 forbids a
    layout that quotes one alone.
    """
    # Imported here rather than at module import: ``mijual.evalset`` is a CLI
    # package and the app must not pay for it on every import. It reaches no
    # database and spends nothing (verified by the smoke test's import scan).
    from mijual.evalset import build_report, load_labels, load_sample

    try:
        sample = load_sample()
        labels = load_labels()
    except (FileNotFoundError, ValueError) as exc:
        # No artifact yet is a state, not a failure: the tab renders the empty
        # accuracy panel rather than 500-ing the whole page.
        return {"available": False, "reason": type(exc).__name__}

    report = build_report(sample, labels)
    shown, blocked = report.totals()
    stamp = labels.provenance
    body: dict[str, Any] = {
        "available": True,
        "sample": {
            "units": sample.units,
            "rows": len(sample.rows),
            "seed": sample.seed,
            "generated_at": sample.generated_at,
            "labelled": len(labels.labelled),
            "coverage": dict(report.coverage),
        },
        "shown": _bucket(shown),
        "blocked": _blocked_bucket(blocked),
        "fields": [_field_score(score) for score in report.ordered],
        "correction_recall": dict(sample.correction_recall),
        "hard_cases": [
            {
                "hard_case": row.hard_case,
                "corp_name": row.corp_name,
                "rcept_no": row.rcept_no,
                "field_ko": row.field_ko,
                "label": label,
                "dart_url": row.dart_url,
            }
            for row, label in sorted(report.hard_cases, key=lambda rl: (rl[0].hard_case, rl[0].row_id))
        ],
        # The command's own output, so the tab and the CLI cannot disagree.
        "markdown": report.render(),
    }
    if stamp is not None:
        body["judged_by"] = {
            "judge": stamp.judge,
            "basis": stamp.basis,
            "imported_at": stamp.imported_at,
        }
    # Absent ``judged_by`` is the honest state of an unstamped artifact, and the
    # surface must then refuse to render the headline (R7 hard rule). The rates
    # are still served: the panel decides what it may show, and hiding the numbers
    # here would hide the fact that they exist unstamped.
    return body


# ---------------------------------------------------------------------------
# 비용 — LLM spend, and the OpenDART request quota
# ---------------------------------------------------------------------------
def spend(session: Session) -> dict[str, Any]:
    """``extraction_call`` aggregates + the run log's own per-day request counts.

    Two windows, each labelled, because R7 forbids showing a cumulative figure as
    if it were a daily one: the LLM aggregate is **cumulative** over every call
    this corpus ever paid for (with the first and last call's KST instants beside
    it), and the OpenDART request figures are **daily**, measured from the run
    log's own per-run counts. The 20,000/day denominator is an operator-stated
    quota (O-1), served with that provenance rather than as a measured fact.
    """
    calls, tokens, cost, first_at, last_at = session.execute(
        select(
            func.count(ExtractionCall.id),
            func.sum(ExtractionCall.total_tokens),
            func.sum(ExtractionCall.cost_usd),
            func.min(ExtractionCall.created_at),
            func.max(ExtractionCall.created_at),
        )
    ).one()
    failures = (
        session.scalar(
            select(func.count()).select_from(ExtractionCall).where(ExtractionCall.status != "ok")
        )
        or 0
    )
    by_model = [
        {"model": model or "", "calls": count, "tokens": int(model_tokens or 0)}
        for model, count, model_tokens in session.execute(
            select(
                ExtractionCall.model, func.count(), func.sum(ExtractionCall.total_tokens)
            ).group_by(ExtractionCall.model)
        ).all()
    ]
    total_cost = float(cost or 0.0)

    llm: dict[str, Any] = {
        "window": "cumulative",
        "calls": int(calls or 0),
        "failures": failures,
        "tokens": int(tokens or 0),
        "cost_usd": f"{total_cost:.6f}",
        # Verbatim in the pipeline's own format — ▷ is the source's mark here.
        "cost_line": f"▷ ${total_cost:.4f}",
        "by_model": sorted(by_model, key=lambda m: (-m["calls"], m["model"])),
    }
    if first_at is not None:
        llm["since"] = clock.iso(first_at)
    if last_at is not None:
        llm["until"] = clock.iso(last_at)

    days: dict[str, dict[str, int]] = {}
    for started_at, requests, run_calls in session.execute(
        select(PipelineRun.started_at, PipelineRun.requests, PipelineRun.calls)
    ).all():
        if started_at is None:
            continue
        key = clock.to_kst(started_at).date().isoformat()
        bucket = days.setdefault(key, {"requests": 0, "calls": 0, "runs": 0})
        bucket["requests"] += int(requests or 0)
        bucket["calls"] += int(run_calls or 0)
        bucket["runs"] += 1

    return {
        "llm": llm,
        "dart": {
            "window": "daily",
            "quota": {
                "requests_per_day": DART_DAILY_QUOTA,
                # Provenance, because the number is not measurable from here.
                "source": "operator (decisions O-1)",
            },
            # Measured from the run log only, so it starts the day the log did.
            "measured_from": "pipeline_run",
            "days": [
                {"date": day} | counts for day, counts in sorted(days.items(), reverse=True)
            ],
        },
    }


# ---------------------------------------------------------------------------
# 사용자 — the 독자 계정 half. The 익명 세션 half comes from the port, unjoined.
# ---------------------------------------------------------------------------
def reader_accounts(
    session: Session, *, limit: int = 50, offset: int = 0
) -> dict[str, Any]:
    """독자 계정: 이메일 · 가입일 · 포트폴리오 종목 **개수** · 알림 설정.

    **최소 열람 is the rule and it is enforced by what this function selects.** The
    portfolio's *contents* (종목, 수량) are never opened — only how many rows there
    are; the password is not mentioned at all, not even as "a hash exists"; and
    nothing here can reach a conversation, because P5 stores none and this query
    touches no table that could.

    R7's fifth column, **샘플 로드 여부, has no backing fact and is therefore
    absent** rather than served as ``false``. R5's sample is anonymous end to end
    (``P5.S8`` note 13: no anonymous write endpoint exists; a 샘플→계정 이전 is the
    client making ordinary authenticated ``POST /portfolio/holdings`` calls), so
    nothing server-side ever learns that a reader loaded it. Serving ``false``
    would be asserting something this build cannot know. Recorded as an open
    question rather than papered over.
    """
    total = session.scalar(select(func.count()).select_from(Account)) or 0
    accounts = list(
        session.scalars(
            select(Account).order_by(Account.created_at.desc(), Account.id.desc())
            .limit(limit)
            .offset(offset)
        ).all()
    )
    ids = [a.id for a in accounts]
    counts: dict[int, int] = {}
    prefs: dict[int, Any] = {}
    if ids:
        counts = {
            account_id: count
            for account_id, count in session.execute(
                select(Holding.account_id, func.count())
                .where(Holding.account_id.in_(ids))
                .group_by(Holding.account_id)
            ).all()
        }
        prefs = {
            row.account_id: row
            for row in session.scalars(
                select(NotificationPref).where(NotificationPref.account_id.in_(ids))
            ).all()
        }

    rows = []
    for account in accounts:
        stored = prefs.get(account.id)
        rows.append(
            {
                "id": account.id,
                "email": account.email,
                "created_at": clock.iso(account.created_at),
                "holdings": counts.get(account.id, 0),
                "notifications": {
                    # An absent row means the default (7일 + 1일), not "off" —
                    # ``P5.S8`` note 9. The panel must render it that way, so the
                    # payload says which of the two it is looking at.
                    "lead_days": (
                        lead_days_of(session, account)
                        if stored is not None
                        else list(DEFAULT_LEAD_DAYS)
                    ),
                    "stored": stored is not None,
                },
            }
        )
    return {"count": total, "limit": limit, "offset": offset, "rows": rows}
