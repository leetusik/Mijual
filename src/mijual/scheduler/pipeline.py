"""The six stages, in order, under one lock and explicit ceilings.

This module is the scheduler's whole behaviour, and it deliberately knows
**nothing** about Celery: a task, the inline ``once`` CLI and a test all call the
same :func:`run_pipeline`. Celery only decides *when* it runs (``app.py``).

Order is not a preference, it is a data dependency:

``collect`` → ``bodydoc`` → ``extract`` → ``gates`` → ``reparse`` → ``snapshot``

collection persists versions and 본문 snapshots; the 본문 layer parses those
snapshots into hints, labels and the ① 증서 verdict; extraction reads only events
the 본문 layer confirmed; and the gate layer judges only what extraction stored.
Running them out of order would not crash — it would silently gate yesterday's
corpus.

The last two are ``P5.S9``'s addition and close a gap ``P5.S3``/``P5.S20``
recorded rather than fixed: the serving precomputation the request path reads
(``offering_input`` rows, ``performance_report.lapse``, and the ``facts`` a parser
change rewrites) was refreshed **by hand**, so the ① extras and the landing
headline could age silently while 기준시각 said the corpus was fresh. Both are
offline — **0 OpenDART requests, 0 model calls** — so scheduling them costs
nothing, and ``reparse`` precedes ``snapshot`` because ``LapseRow`` is built from
``facts``.

Every run also writes itself down (:class:`~mijual.db.models.PipelineRun`): R7's
개요 tab renders 최근 실행 with per-stage counts, spend and the ▷ cost line, and
before this the record died with the worker process.

Three properties every stage keeps:

* **serving is untouched.** Nothing here is reachable from a request path; every
  stage writes persisted rows and P3 reads those rows. A worker that never runs
  leaves the board stale, never dark (the 결격 rule).
* **the ceiling is the client's, not the loop's.** ``DartClient(max_requests=…)``
  and ``GeminiClient(max_calls=…)`` refuse the next unit themselves, and both
  runners already catch that cleanly and keep what they collected — so a
  budget-exhausted stage is a *reported outcome*, not an exception that ends the
  run.
* **no secret is ever in a summary line.** Stage summaries are counts.
"""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone

from mijual.bodydoc.backfill import backfill_corrections, confirm_warrants
from mijual.calc import today_kst
from mijual.collect.runner import collect_window
from mijual.config import Settings, load_settings
from mijual.dart import DartClient
from mijual.db.models import Base, PipelineRun, utcnow
from mijual.db.schema_sync import ensure_columns
from mijual.db.session import create_all, make_engine, make_session_factory, session_scope
from mijual.estimate.runner import reparse_performance
from mijual.estimate.snapshot import refresh_serving_snapshot
from mijual.extract.client import GeminiClient
from mijual.extract.labelfields import read_label_fields
from mijual.extract.runner import run_corrections, run_extraction
from mijual.gates.runner import run_gates
from mijual.scheduler.config import PipelineConfig
from mijual.scheduler.locks import NullLock, make_lock

__all__ = [
    "PipelineResult",
    "StageResult",
    "close_run_row",
    "open_run_row",
    "run_pipeline",
    "stage_bodydoc",
    "stage_collect",
    "stage_extract",
    "stage_gates",
    "stage_reparse",
    "stage_snapshot",
    "session_factory_for",
]


@dataclass
class StageResult:
    """One stage's outcome: a status, a one-line summary, and what it spent."""

    name: str
    status: str = "ok"  # ok | budget_exhausted | error | skipped
    summary: str = ""
    requests: int = 0
    calls: int = 0
    cost_usd: float = 0.0
    seconds: float = 0.0
    detail: dict = field(default_factory=dict)

    @property
    def line(self) -> str:
        mark = {"ok": "", "budget_exhausted": " — BUDGET EXHAUSTED", "error": " — ERROR",
                "skipped": " — SKIPPED"}[self.status]
        return f"{self.name:<9}: {self.summary}{mark} [{self.seconds:.1f}s]"

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass
class PipelineResult:
    """What one scheduled run did, in numbers — the record and the log line."""

    label: str = "daily"
    window: tuple[str, str] = ("", "")
    config_line: str = ""
    started_at: str = ""
    seconds: float = 0.0
    lock: str = "none"
    skipped: bool = False
    stages: list[StageResult] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @property
    def requests(self) -> int:
        return sum(s.requests for s in self.stages)

    @property
    def calls(self) -> int:
        return sum(s.calls for s in self.stages)

    @property
    def cost_usd(self) -> float:
        return sum(s.cost_usd for s in self.stages)

    @property
    def ok(self) -> bool:
        return not self.skipped and all(s.status != "error" for s in self.stages)

    @property
    def spend_line(self) -> str:
        """The run's own spend sentence — the line ``render()`` prints, verbatim.

        A property rather than an f-string inside :meth:`render` because R7's
        최근 실행 표 stores and shows this line **verbatim**, ``▷`` included: in the
        ops panel ``▷`` is quoted pipeline output, and the boundary is the source.
        Two spellings of it would eventually disagree, and the one on the operator's
        screen would be the wrong one.
        """
        return (
            f"spend     : {self.requests} OpenDART request(s), {self.calls} LLM call(s), "
            f"▷ ${self.cost_usd:.4f} estimated  |  {self.seconds:.1f}s total"
        )

    def render(self) -> str:
        lines = [
            f"pipeline  : {self.label} {self.window[0]}~{self.window[1]} "
            f"lock={self.lock}" + (" SKIPPED (lock held)" if self.skipped else ""),
            f"config    : {self.config_line}",
        ]
        lines.extend(s.line for s in self.stages)
        lines.append(self.spend_line)
        lines.extend(f"note      : {n}" for n in self.notes)
        return "\n".join(lines)

    def as_dict(self) -> dict:
        """JSON-able — this is what a Celery task returns to the result backend."""
        return {
            "label": self.label,
            "window": list(self.window),
            "config": self.config_line,
            "started_at": self.started_at,
            "seconds": round(self.seconds, 2),
            "lock": self.lock,
            "skipped": self.skipped,
            "ok": self.ok,
            "requests": self.requests,
            "calls": self.calls,
            "cost_usd": round(self.cost_usd, 6),
            "stages": [s.as_dict() for s in self.stages],
            "notes": list(self.notes),
        }


# ---------------------------------------------------------------------------
# shared plumbing
# ---------------------------------------------------------------------------
def session_factory_for(config: PipelineConfig):
    """Engine + session factory, with the additive-column sync S3 introduced.

    ``create_all`` cannot add a column to a populated table (N27), so every entry
    point that writes runs ``ensure_columns`` first — a scheduled worker is the
    last place that should fail on a missing column at 07:30.
    """
    engine = make_engine(config.database_url)
    create_all(engine)
    ensure_columns(engine, Base)
    return make_session_factory(engine)


def _dart_client(config: PipelineConfig, settings: Settings, max_requests: int | None) -> DartClient:
    return DartClient(
        settings=settings,
        cache_dir=config.cache_dir,
        offline=config.offline,
        max_requests=max_requests,
    )


def _stage(name: str):
    """Wrap a stage body so a failure is a reported status, never a dead run."""

    def decorate(fn):
        def wrapped(config: PipelineConfig, factory, *, settings=None, log=None) -> StageResult:
            result = StageResult(name=name)
            started = time.monotonic()
            try:
                fn(config, factory, result, settings=settings, log=log)
            except Exception as exc:  # noqa: BLE001 - one stage must not kill the run
                result.status = "error"
                # Type + truncated message only: no URL, no payload, no secret.
                result.summary = f"{type(exc).__name__}: {str(exc)[:160]}"
            result.seconds = time.monotonic() - started
            if log:
                log(result.line)
            return result

        wrapped.__name__ = fn.__name__
        wrapped.__doc__ = fn.__doc__
        return wrapped

    return decorate


# ---------------------------------------------------------------------------
# stage 1 — collect
# ---------------------------------------------------------------------------
@_stage("collect")
def stage_collect(config, factory, result: StageResult, *, settings=None, log=None) -> None:
    """Roll the discovery window forward: new filings **and** 정정 of old ones.

    The window is short on purpose (14 days by default). It still catches a
    correction whose original is months old, because pairing resolves the
    original — through the corp-scoped ``list.json`` history when needed — and the
    detail fetch is then windowed on the **original's** date (N3).
    """
    settings = settings or load_settings()
    bgn, end = config.window()
    client = _dart_client(config, settings, config.collect_max_requests)
    report = collect_window(
        client,
        factory,
        bgn_de=bgn,
        end_de=end,
        markets=config.markets,
        endpoints=config.endpoints,
        max_documents=config.collect_max_documents,
        log=None,
    )
    result.requests = report.requests
    result.status = "budget_exhausted" if report.budget_exhausted else "ok"
    result.detail = {
        "window": [bgn, end],
        "list_rows": report.list_rows_scanned,
        "target_rows": report.target_rows,
        "events": report.events_planned,
        "live_events": report.live_events,
        "versions": report.versions_planned,
        "documents_fetched": report.documents_fetched,
        "db_before": list(report.db_before),
        "db_after": list(report.db_after),
        "gaps": len(report.missing_chunks),
    }
    result.summary = (
        f"{bgn}~{end} | {report.list_rows_scanned} list row(s) -> {report.target_rows} target(s) "
        f"| events {report.events_planned} (live {report.live_events}), "
        f"versions {report.versions_planned} | 본문 +{report.documents_fetched} "
        f"| db {report.db_before}->{report.db_after} | {report.requests} req"
        + (f" | gaps {len(report.missing_chunks)}" if report.missing_chunks else "")
    )


# ---------------------------------------------------------------------------
# stage 2 — 본문 (deterministic layer)
# ---------------------------------------------------------------------------
@_stage("bodydoc")
def stage_bodydoc(config, factory, result: StageResult, *, settings=None, log=None) -> None:
    """Parse what collection stored: 정정 hints, then the ① 증서 verdict.

    Both passes read snapshots first and only fetch a 본문 the database does not
    hold — the backfill's own accounting (snapshot / cache / live) says which. The
    warrants pass is what turns ``ic_mthn`` (provisional) into the 본문's final
    answer, so a newly collected ① event is never exposed on ``ic_mthn`` alone
    (N26/N30).
    """
    settings = settings or load_settings()
    client = _dart_client(config, settings, config.bodydoc_max_requests)
    # ``fetch=True`` even offline: the client decides. An offline client resolves
    # a 본문 from the on-disk response cache and raises ``CacheMiss`` otherwise,
    # which the loader reports as *missing*, not as an error — so an offline pass
    # still adopts documents an earlier budget-capped live run fetched but never
    # persisted (N34's rule, 28 documents the first time it was applied).
    backfill = backfill_corrections(
        client,
        factory,
        max_documents=config.bodydoc_max_documents,
        fetch=True,
        log=None,
    )
    warrants = confirm_warrants(
        client,
        factory,
        fetch=True,
        max_documents=config.bodydoc_max_documents,
        log=None,
    )
    result.requests = backfill.requests + warrants.requests
    result.status = (
        "budget_exhausted"
        if (backfill.budget_exhausted or warrants.budget_exhausted)
        else "ok"
    )
    result.detail = {
        "corrections_considered": backfill.considered,
        "corrections_parsed": backfill.parsed,
        "hints": backfill.hints,
        "reattached": len(backfill.reattached),
        "retired": len(backfill.retired),
        "documents_live": backfill.documents_fetched_live + warrants.documents_fetched_live,
        "warrant_events": warrants.events,
        "warrant_outcomes": dict(warrants.outcomes),
    }
    result.summary = (
        f"정정 {backfill.parsed}/{backfill.considered} parsed, hints {backfill.hints}, "
        f"reattached {len(backfill.reattached)}, retired {len(backfill.retired)} "
        f"| ① 본문 18. over {warrants.events} event(s) "
        f"{dict(sorted(warrants.outcomes.items()))} "
        f"| 본문 +{backfill.documents_fetched_live + warrants.documents_fetched_live} "
        f"| {result.requests} req"
    )


# ---------------------------------------------------------------------------
# stage 3 — extraction (the only stage that spends money)
# ---------------------------------------------------------------------------
@_stage("extract")
def stage_extract(config, factory, result: StageResult, *, settings=None, log=None) -> None:
    """Read the prose fields of versions that have none yet, under one ceiling.

    ``run_extraction`` skips a version whose fields are already stored at this
    ``schema_version`` (N42), so the steady-state cost of a scheduled run is only
    what is genuinely new — usually a handful of calls, often zero. One
    :class:`GeminiClient` serves the whole stage, so ``extract_max_calls`` is a
    ceiling on the **run**, not on each sub-pass.

    Layer 1's free half — the ``본문-label`` fields — runs first and is deliberately
    **not** under that ceiling: it makes no call, so budgeting it could only ever
    starve it.
    """
    settings = settings or load_settings()
    pieces: list[str] = []
    exhausted = False
    detail: dict = {}

    # The 본문-label tier first, and **outside every budget**: it spends nothing,
    # so a newly collected ③ must never render its 반대의사 통지 기간 while its
    # 매수예정가격 waits for a hand-run command (P5.S6 / D-15).
    labels = read_label_fields(factory, log=None)
    detail["label_fields"] = {
        "events": labels.events,
        "documents": labels.documents,
        "rows": labels.rows,
        "fields": {k: dict(v) for k, v in labels.per_field.items()},
    }
    pieces.append(f"label {labels.rows}row/0call")

    client = GeminiClient(
        settings=settings,
        max_calls=config.extract_max_calls,
        dry_run=config.offline,
        log=None,
    )

    for rights in config.extract_rights:
        report = run_extraction(client, factory, rights=rights, log=None)
        exhausted |= report.budget_exhausted
        detail[report.task] = {
            "events": report.events,
            "documents": report.documents,
            "calls": report.calls,
            "skipped_versions": report.skipped_versions,
            "failures": report.call_failures,
        }
        pieces.append(
            f"{report.task} {report.events}ev/{report.calls}call"
            + (f"/{report.call_failures}fail" if report.call_failures else "")
        )
        if report.budget_exhausted:
            break

    if config.extract_corrections and not exhausted:
        for rights in config.extract_rights:
            report = run_corrections(client, factory, rights=rights, log=None)
            exhausted |= report.budget_exhausted
            detail[f"correction_{rights.value}"] = {
                "events": report.events,
                "calls": report.calls,
                "skipped_versions": report.skipped_versions,
            }
            pieces.append(f"정정 {rights.value} {report.events}ev/{report.calls}call")
            if report.budget_exhausted:
                break

    # Money is counted from the **client's** ledger, never from a report's own
    # tally: a dry run builds prompts and reports "calls" it never made.
    result.calls = client.call_count
    result.cost_usd = client.ledger.cost_usd
    result.status = "budget_exhausted" if exhausted else "ok"
    result.detail = detail | {
        "max_calls": config.extract_max_calls,
        "dry_run": config.offline,
        "tokens": client.ledger.total_tokens,
    }
    result.summary = (
        ("[dry-run] " if config.offline else "")
        + "; ".join(pieces)
        + f" | {client.call_count} live call(s), {client.ledger.total_tokens:,} token(s), "
        f"▷ ${client.ledger.cost_usd:.4f}"
    )


# ---------------------------------------------------------------------------
# stage 4 — gates (free, and the only stage that decides what may be shown)
# ---------------------------------------------------------------------------
@_stage("gates")
def stage_gates(config, factory, result: StageResult, *, settings=None, log=None) -> None:
    """Re-derive every verdict and every event's exposure. 0 requests, 0 calls.

    Deliberately unconditional: the gate layer drops and re-derives (S5), so a
    snapshot that moved under a stored citation stops passing on the very next
    run instead of vouching for a citation that no longer exists.
    """
    report = run_gates(factory, log=None)
    totals = {"passed": 0, "tbd": 0, "failed": 0, "not_evaluable": 0}
    for counter in report.per_field.values():
        for key in totals:
            totals[key] += counter[key]
    exposable = sum(v for k, v in report.event_states.items() if k.endswith(":exposable"))
    renderable = sum(report.exposable_fields.values())
    result.detail = {
        "events": report.events,
        "rows": report.rows,
        "fields": totals,
        "exposable_events": exposable,
        "renderable_fields": renderable,
        "withdrawals": len(report.withdrawals),
        "event_states": dict(report.event_states),
    }
    result.summary = (
        f"{report.events} event(s) judged, {report.rows} field row(s) | "
        f"passed {totals['passed']} tbd {totals['tbd']} failed {totals['failed']} "
        f"n/a {totals['not_evaluable']} | exposable {exposable} event(s), "
        f"{renderable} renderable field(s)"
        # Event-level, not filing-level: one withdrawn ``rcept_no`` can sit under
        # two event keys (N21's residue), so 5 flagged events carry N47's 4
        # distinct withdrawals.
        + (f" | 철회 {len(report.withdrawals)} flagged event(s)" if report.withdrawals else "")
    )


# ---------------------------------------------------------------------------
# stage 5 — reparse (offline: re-read the stored 실적보고서 bytes)
# ---------------------------------------------------------------------------
@_stage("reparse")
def stage_reparse(config, factory, result: StageResult, *, settings=None, log=None) -> None:
    """Re-derive every stored 증권발행실적보고서's ``facts`` from its own bytes.

    **0 requests, 0 calls, idempotent.** ``facts`` is otherwise written only by
    ``estimate collect``, which needs a client to *discover* filings — so without
    this stage a parser change (``P5.S20``'s multi-addend citations, say) reaches
    the corpus only when somebody remembers to run a command. It runs before
    ``snapshot`` because ``LapseRow`` is built from ``facts``.
    """
    with session_scope(factory) as session:
        report = reparse_performance(session)
    result.detail = {
        "reports": report.reports,
        "reparsed": report.reparsed,
        "changed": report.changed,
        "no_bytes": report.no_bytes,
        "errors": report.errors,
    }
    result.summary = (
        f"{report.reparsed}/{report.reports} 실적보고서 re-read, "
        f"{report.changed} with changed facts"
        + (f", {report.no_bytes} without bytes" if report.no_bytes else "")
        + (f", {report.errors} error(s)" if report.errors else "")
    )


# ---------------------------------------------------------------------------
# stage 6 — snapshot (offline: the serving precomputation)
# ---------------------------------------------------------------------------
@_stage("snapshot")
def stage_snapshot(config, factory, result: StageResult, *, settings=None, log=None) -> None:
    """Refresh what a request path may not compute for itself (``P5.S3``).

    **0 requests, 0 calls, idempotent.** ``mijual.estimate`` imports the three
    spending modules, so the ① 발행가/할인율/배정비율 and the 소멸가치 cannot be
    derived on a request — the worker computes and the request path reads. Until
    this ran on the schedule, those numbers aged silently while the board's
    기준시각 said the corpus was fresh, which is the one way this product could
    serve a stale figure without saying so.
    """
    with session_scope(factory) as session:
        written = refresh_serving_snapshot(session, today=today_kst())
    result.detail = {
        "offerings": written.offerings,
        "priced": written.priced,
        "upcoming": written.upcoming,
        "lapse_rows": written.lapse_rows,
        "valued": written.valued,
        "notes": list(written.notes),
    }
    result.summary = (
        f"① inputs {written.offerings} ({written.priced} priced, "
        f"{written.upcoming} upcoming) | 소멸 rows {written.lapse_rows} "
        f"({written.valued} valued)"
    )


STAGE_FUNCTIONS = {
    "collect": stage_collect,
    "bodydoc": stage_bodydoc,
    "extract": stage_extract,
    "gates": stage_gates,
    "reparse": stage_reparse,
    "snapshot": stage_snapshot,
}


# ---------------------------------------------------------------------------
# the run log — R7's 최근 실행 표, written by the run itself
# ---------------------------------------------------------------------------
def open_run_row(factory, config: PipelineConfig, result: PipelineResult) -> int | None:
    """Open this run's row **now**, before the first stage. Returns its id.

    Opened at the start and closed at the end so a run that crashes leaves a row
    with no ``finished_at`` rather than no row at all: an unfinished run is
    precisely what an operator needs to see, and it is also what gives the ops
    panel's lock chip an honest 시작 시각 while a run holds the lock.

    Failure here is **swallowed** (reported as a note): a run log that can take a
    pipeline down would be worse than no run log, and the pipeline's job is the
    corpus, not the panel.
    """
    if not config.write_run_log:
        return None
    try:
        with session_scope(factory) as session:
            row = PipelineRun(
                label=config.label,
                trigger=config.trigger,
                started_at=utcnow(),
                window_bgn=result.window[0] or None,
                window_end=result.window[1] or None,
                config_line=result.config_line,
                lock=result.lock,
            )
            session.add(row)
            session.flush()
            return row.id
    except Exception as exc:  # noqa: BLE001 - the log must never fail the run
        result.notes.append(f"run log not opened ({type(exc).__name__})")
        return None


def close_run_row(factory, run_id: int | None, result: PipelineResult) -> None:
    """Close the row with what the run actually did — its own numbers, verbatim."""
    if run_id is None:
        return
    try:
        with session_scope(factory) as session:
            row = session.get(PipelineRun, run_id)
            if row is None:  # pragma: no cover - the row was just written
                return
            row.finished_at = utcnow()
            row.seconds = round(result.seconds, 2)
            row.ok = result.ok
            row.requests = result.requests
            row.calls = result.calls
            row.cost_usd = round(result.cost_usd, 6)
            # The pipeline's own sentence, ▷ and all (R7: 경계 = 출처).
            row.spend_line = result.spend_line
            row.stages = [s.as_dict() for s in result.stages]
            row.notes = list(result.notes)
    except Exception as exc:  # noqa: BLE001 - the log must never fail the run
        result.notes.append(f"run log not closed ({type(exc).__name__})")


# ---------------------------------------------------------------------------
# the run
# ---------------------------------------------------------------------------
def run_pipeline(
    config: PipelineConfig | None = None,
    *,
    factory=None,
    settings: Settings | None = None,
    log=None,
) -> PipelineResult:
    """Run the configured stages in order, at most one run at a time.

    A run that cannot take the lock returns ``skipped`` — it does not wait and it
    does not run anyway. Overlap is the one thing idempotent upserts cannot
    repair, because the cost is spent quota, not a duplicated row.
    """
    config = config or PipelineConfig()
    settings = settings or load_settings()
    result = PipelineResult(
        label=config.label,
        window=config.window(),
        config_line=config.describe(),
        started_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        notes=list(config.notes),
    )
    started = time.monotonic()

    lock = (
        make_lock(
            redis_url=(
                config.redis_url if config.redis_url is not None else settings.redis_url
            ),
            name=config.lock_name,
            ttl_s=config.lock_ttl_s,
            fallback_dir=config.lock_dir,
            log=log,
        )
        if config.use_lock
        else NullLock(name=config.lock_name)
    )
    result.lock = lock.kind
    if not lock.acquire():
        result.skipped = True
        result.seconds = time.monotonic() - started
        result.notes.append(
            f"another run holds {lock.kind} lock '{lock.name}' — this run did nothing"
        )
        if log:
            log(result.render())
        return result
    if getattr(lock, "stolen", False):
        result.notes.append(f"stale {lock.kind} lock stolen (previous run left it behind)")

    run_id: int | None = None
    try:
        if log:
            log(f"pipeline  : {config.describe()}")
        factory = factory or session_factory_for(config)
        # Opened before the first stage so an in-flight (or crashed) run is
        # visible, and **not** written at all for a skipped run: a run that could
        # not take the lock did nothing, and the lock chip is where contention
        # shows up. Counting non-runs as runs would make the 최근 실행 표 lie.
        run_id = open_run_row(factory, config, result)
        for name in config.stages:
            result.stages.append(
                STAGE_FUNCTIONS[name](config, factory, settings=settings, log=log)
            )
    finally:
        lock.release()
        result.seconds = time.monotonic() - started
        close_run_row(factory, run_id, result)
    return result
