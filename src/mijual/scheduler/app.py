"""The Celery app, its five tasks, and the beat schedule.

Celery decides **when**; :mod:`mijual.scheduler.pipeline` decides **what**. That
split is the point of this module's small size — everything a task does is one
call to :func:`~mijual.scheduler.pipeline.run_pipeline`, so the schedule can be
read, tested and reasoned about without a broker, and the same behaviour is
reachable from the CLI when a broker is not running.

Run it (Redis first — ``compose.yaml`` reserves host **6380** behind the
``scheduling`` profile so it never collides with another project's 6379)::

    docker compose --profile scheduling up -d redis
    .venv/bin/celery -A mijual.scheduler.app worker -l info -c 1
    .venv/bin/celery -A mijual.scheduler.app beat   -l info -s var/celerybeat-schedule

``-s var/celerybeat-schedule`` keeps beat's own last-run state out of the repo
root (``var/`` is gitignored). ``-c 1`` is the honest concurrency: the run lock
would make a second slot skip anyway.

**Timezone is Asia/Seoul, explicitly** (``enable_utc = False``). Every date this
product prints is a Korean calendar date — a 청약 window, a D-day — so a beat
entry that says 07:30 must mean 07:30 KST on a worker running anywhere.

**Serving stays decoupled.** Nothing here is imported by a request path. P3's
FastAPI layer reads the rows these tasks persist; a dead worker leaves the board
stale, never dark (the 결격 rule). No task returns anything a page renders.

``P2.S7`` registers its ② collection task the same way: add a task with
``@app.task(name="mijual.collect_cb")`` and one :data:`BEAT_SCHEDULE` entry
beside these — the schedule is a plain dict on purpose.
"""

from __future__ import annotations

from celery import Celery
from celery.schedules import crontab

from mijual.config import load_settings
from mijual.scheduler.config import (
    DEFAULT_WINDOW_DAYS,
    RESYNC_WINDOW_DAYS,
    PipelineConfig,
)
from mijual.scheduler.pipeline import run_pipeline

__all__ = [
    "BEAT_SCHEDULE",
    "TIMEZONE",
    "app",
    "bodydoc_sync",
    "collect_recent",
    "daily_pipeline",
    "extract_new",
    "gates_run",
    "make_app",
]

#: Korean market time. Not a default — a decision (see the module docstring).
TIMEZONE = "Asia/Seoul"

#: The periodic jobs. Times are KST.
#:
#: * **07:30** — before the market opens: yesterday evening's filings are in, so
#:   the board is current for the day that matters to a 청약 deadline.
#: * **19:30** — after 공시 접수 closes (18:00) plus a margin: the day's filings
#:   and 정정 land the same evening instead of waiting until the next morning.
#: * **Sunday 04:30** — the straggler pass over a 90-day window: corrections
#:   whose original sits outside the daily window, and events whose corp-scoped
#:   pairing query only resolves once more filings exist.
BEAT_SCHEDULE: dict[str, dict] = {
    "daily-pipeline-morning": {
        "task": "mijual.daily_pipeline",
        "schedule": crontab(hour=7, minute=30),
        "kwargs": {"window_days": DEFAULT_WINDOW_DAYS, "label": "daily-morning"},
    },
    "daily-pipeline-evening": {
        "task": "mijual.daily_pipeline",
        "schedule": crontab(hour=19, minute=30),
        "kwargs": {"window_days": DEFAULT_WINDOW_DAYS, "label": "daily-evening"},
    },
    "weekly-resync": {
        "task": "mijual.daily_pipeline",
        "schedule": crontab(hour=4, minute=30, day_of_week=0),
        "kwargs": {
            "window_days": RESYNC_WINDOW_DAYS,
            "label": "weekly-resync",
            # A quarter of filings costs more discovery + detail calls than two
            # weeks does; still ~10% of one day's 20,000-request quota (O-1).
            "collect_max_requests": 1500,
            "bodydoc_max_requests": 600,
            "collect_max_documents": 400,
        },
    },
}


def make_app(*, broker_url: str | None = None, backend_url: str | None = None) -> Celery:
    """Build the Celery app from ``Settings.redis_url`` (broker **and** backend)."""
    settings = load_settings()
    url = broker_url or settings.redis_url
    app = Celery("mijual", broker=url, backend=backend_url or url)
    app.conf.update(
        timezone=TIMEZONE,
        enable_utc=False,
        beat_schedule=BEAT_SCHEDULE,
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"],
        result_expires=7 * 24 * 3600,
        # One pipeline at a time is the design (the run lock enforces it anyway);
        # prefetching would only queue work behind a long collection.
        worker_prefetch_multiplier=1,
        task_acks_late=True,
        # A full run is minutes, not hours. The soft limit lets a stage unwind
        # and report instead of being killed mid-write.
        task_soft_time_limit=50 * 60,
        task_time_limit=60 * 60,
    )
    return app


app = make_app()


def _run(**kwargs) -> dict:
    """Every task body: kwargs → config → one run → a JSON-able record."""
    return run_pipeline(PipelineConfig.from_kwargs(**kwargs), log=print).as_dict()


@app.task(name="mijual.daily_pipeline")
def daily_pipeline(**kwargs) -> dict:
    """collect → bodydoc → extract → gates, in order, under one lock.

    The four stages run **in-process, in order** rather than as a Celery
    ``chain``: one lock has to span the whole run, and a chain's links are
    separate tasks that could interleave with another run's links. Ordering is a
    data dependency (each stage consumes what the previous one persisted), so
    parallelism here would buy nothing and cost correctness.
    """
    return _run(**kwargs)


@app.task(name="mijual.collect_recent")
def collect_recent(**kwargs) -> dict:
    """Discovery + pairing + detail + 본문 snapshots for the rolling window."""
    return _run(**{"stages": ("collect",), "label": "collect", **kwargs})


@app.task(name="mijual.bodydoc_sync")
def bodydoc_sync(**kwargs) -> dict:
    """<CORRECTION> hint backfill + the ① 본문 18. 신주인수권양도여부 verdict."""
    return _run(**{"stages": ("bodydoc",), "label": "bodydoc", **kwargs})


@app.task(name="mijual.extract_new")
def extract_new(**kwargs) -> dict:
    """Prose fields of versions that have none yet, under the call ceiling."""
    return _run(**{"stages": ("extract",), "label": "extract", **kwargs})


@app.task(name="mijual.gates_run")
def gates_run(**kwargs) -> dict:
    """Re-derive every gate verdict and every event's exposure. Free."""
    return _run(**{"stages": ("gates",), "label": "gates", **kwargs})


def describe_schedule(schedule: dict[str, dict] | None = None) -> str:
    """The beat schedule as text — what ``python -m mijual.scheduler schedule`` prints."""
    entries = schedule if schedule is not None else BEAT_SCHEDULE
    lines = [f"timezone   : {TIMEZONE} (enable_utc=False)"]
    for name, entry in entries.items():
        kwargs = entry.get("kwargs") or {}
        lines.append(f"  {name:<24} {entry['task']:<24} {entry['schedule']}")
        if kwargs:
            lines.append(f"  {'':<24} kwargs {kwargs}")
    lines.append(f"tasks      : {sorted(k for k in app.tasks if k.startswith('mijual.'))}")
    return "\n".join(lines)
