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

**② rides these entries; it did not get its own** (``P2.S7``). The collector's
target registry drives ``PipelineConfig.endpoints``
(``mijual.collect.targets.DEFAULT_ENDPOINTS``), so registering ``cvbdIsDecsn``
there put ② inside the existing ``collect`` stage — same window, same lock, same
ceilings — instead of adding a second schedule that could interleave with this
one. ``extract_rights`` is deliberately left at ``(R1, R3)``: ②'s countdown is
``API`` tier and needs **zero** LLM (N6), and its optional prose fields are run
by hand under their own cap (``python -m mijual.cb extract``). The 2025-H2
backfill is likewise a one-off CLI (``python -m mijual.collect --bgn 20250601
… --endpoints cvbdIsDecsn``) and never a beat entry — a scheduled job's window
rolls forward, so a fixed historical window has no business in one.
"""

from __future__ import annotations

from celery import Celery
from celery.schedules import crontab

from mijual.beat import BEAT_ENTRIES, TIMEZONE, BeatEntry
from mijual.config import load_settings
from mijual.scheduler.config import PipelineConfig
from mijual.scheduler.pipeline import run_pipeline

__all__ = [
    "BEAT_ENTRIES",
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


def _crontab(entry: BeatEntry):
    """One :class:`~mijual.beat.BeatEntry` as the ``crontab`` beat fires it."""
    if entry.day_of_week is None:
        return crontab(hour=entry.hour, minute=entry.minute)
    return crontab(hour=entry.hour, minute=entry.minute, day_of_week=entry.day_of_week)


#: The periodic jobs, built from :data:`mijual.beat.BEAT_ENTRIES` — the one
#: declaration of when this pipeline runs. It lives outside this module because
#: R7's 개요 tab renders the schedule ("설정이 곧 진실") and a request path may not
#: import this package: :mod:`mijual.scheduler.pipeline` pulls the collector and
#: the extractor, and nothing in a request path may reach a spending module. Add
#: or move an entry in :mod:`mijual.beat` and both the worker and the ops panel
#: change together.
BEAT_SCHEDULE: dict[str, dict] = {
    entry.name: {
        "task": entry.task,
        "schedule": _crontab(entry),
        "kwargs": dict(entry.kwargs),
    }
    for entry in BEAT_ENTRIES
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
