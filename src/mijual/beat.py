"""What the scheduled pipeline is configured to do — declared without Celery.

The beat schedule used to live inside :mod:`mijual.scheduler.app` as a dict of
``crontab`` objects. R7's 개요 tab has to render it (「beat 스케줄 표는 Celery beat
설정에서 렌더 — 하드코딩 금지, 설정이 곧 진실」), and a request path may not import
:mod:`mijual.scheduler` at all: that package pulls
:mod:`mijual.collect`/:mod:`mijual.extract`/:mod:`mijual.dart` through
:mod:`mijual.scheduler.pipeline`, and nothing in a request path may reach a module
that can spend an OpenDART request or a model call (`architecture`).

So the declaration moved **down**, not sideways. This module is stdlib-only and
imports nothing from this package, which makes it importable from both ends:

* :mod:`mijual.scheduler.app` turns :data:`BEAT_ENTRIES` into the ``crontab``
  entries Celery beat actually fires;
* :mod:`mijual.web.opsreads` renders the same objects on the 개요 tab.

There is therefore exactly **one** statement of when the pipeline runs, and the
ops panel cannot show a schedule the worker is not running. The same reasoning
applies to :data:`LOCK_KEY_PREFIX`: the lock chip reads
``mijual:lock:pipeline`` from Redis, and it must be the key
:mod:`mijual.scheduler.locks` writes, not a second spelling of it.

**Nothing here runs anything.** It is a declaration plus the arithmetic that says
when an entry was *due* — which is what lets the 개요 tab derive R7's
「실행 기록 없음」 row from the schedule and the run log rather than from a
fabricated row.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta

__all__ = [
    "BEAT_ENTRIES",
    "BeatEntry",
    "DEFAULT_WINDOW_DAYS",
    "LOCK_KEY_PREFIX",
    "PIPELINE_LOCK_NAME",
    "RESYNC_WINDOW_DAYS",
    "TIMEZONE",
    "lock_key",
]

#: Korean market time. Not a default — a decision: every date this product prints
#: is a Korean calendar date, so a beat entry that says 07:30 must mean 07:30 KST
#: on a worker running anywhere (``enable_utc=False`` in the Celery app).
TIMEZONE = "Asia/Seoul"

#: Rolling discovery window of the daily run, in days back from today (KST).
DEFAULT_WINDOW_DAYS = 14
#: The weekly straggler pass. Wide enough to re-reach a quarter of filings.
RESYNC_WINDOW_DAYS = 90

#: Redis key prefix for the run lock. One namespace for the whole workspace.
LOCK_KEY_PREFIX = "mijual:lock:"
#: The lock every corpus-writing entry point takes, and the one the ops panel
#: shows: ``mijual:lock:pipeline``.
PIPELINE_LOCK_NAME = "pipeline"


def lock_key(name: str = PIPELINE_LOCK_NAME) -> str:
    """The Redis key a named lock lives under. One spelling, two readers."""
    return f"{LOCK_KEY_PREFIX}{name}"


#: Celery's ``day_of_week`` numbering — ``0`` is Sunday — mapped onto Python's
#: ``date.weekday()``, where Monday is ``0``. Getting this backwards would make
#: the ops panel say the weekly pass is due on the wrong day, which is precisely
#: the kind of quiet wrongness the 「실행 기록 없음」 row exists to catch.
_CELERY_DOW_TO_PYTHON = {0: 6, 1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 7: 6}


@dataclass(frozen=True)
class BeatEntry:
    """One periodic job: which task, at what KST wall-clock time, with what kwargs."""

    name: str
    task: str
    hour: int
    minute: int
    #: Celery numbering (``0`` = Sunday). ``None`` means every day.
    day_of_week: int | None = None
    kwargs: dict = field(default_factory=dict)

    @property
    def spec(self) -> str:
        """``07:30 daily`` / ``04:30 Sun`` — the schedule as one readable token.

        English and machine-ish on purpose: R7 renders 크롬 라벨 in Korean and
        leaves 코드·식별자·스테이지 출력 raw, and a beat entry is configuration.
        """
        when = f"{self.hour:02d}:{self.minute:02d}"
        if self.day_of_week is None:
            return f"{when} daily"
        names = ("Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat")
        return f"{when} {names[self.day_of_week % 7]}"

    def runs_on(self, moment: datetime) -> bool:
        """Does this entry fire on ``moment``'s calendar day?"""
        if self.day_of_week is None:
            return True
        return moment.weekday() == _CELERY_DOW_TO_PYTHON[self.day_of_week % 8]

    def due_between(self, start: datetime, end: datetime) -> list[datetime]:
        """Every instant this entry was due in ``[start, end]``, oldest first.

        Both bounds are KST-aware datetimes and the returned instants carry
        ``start``'s tzinfo, so the caller never has to re-attach one. This is the
        *schedule's* half of R7's 「스케줄된 beat가 안 돌았으면 실행 기록 없음 행」:
        the panel matches these against the run log and renders a missing one in
        alert ink. The backend states when a run was due and what ran; it never
        fabricates a run row for the gap.
        """
        if end < start:
            return []
        due: list[datetime] = []
        day = start.replace(hour=self.hour, minute=self.minute, second=0, microsecond=0)
        if day < start:
            day += timedelta(days=1)
        while day <= end:
            if self.runs_on(day):
                due.append(day)
            day += timedelta(days=1)
        return due

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "task": self.task,
            "spec": self.spec,
            "hour": self.hour,
            "minute": self.minute,
            "day_of_week": self.day_of_week,
            "kwargs": dict(self.kwargs),
        }


#: The periodic jobs. Times are KST.
#:
#: * **07:30** — before the market opens: yesterday evening's filings are in, so
#:   the board is current for the day that matters to a 청약 deadline.
#: * **19:30** — after 공시 접수 closes (18:00) plus a margin: the day's filings
#:   and 정정 land the same evening instead of waiting until the next morning.
#: * **Sunday 04:30** — the straggler pass over a 90-day window: corrections
#:   whose original sits outside the daily window, and events whose corp-scoped
#:   pairing query only resolves once more filings exist.
#:
#: ``trigger: "beat"`` is what puts ``beat`` in the run log's 트리거 column: a run
#: fired by hand through the CLI or a manual ``.delay()`` keeps the default
#: ``manual``, so the 최근 실행 표 says which runs the schedule is responsible for.
BEAT_ENTRIES: tuple[BeatEntry, ...] = (
    BeatEntry(
        name="daily-pipeline-morning",
        task="mijual.daily_pipeline",
        hour=7,
        minute=30,
        kwargs={
            "window_days": DEFAULT_WINDOW_DAYS,
            "label": "daily-morning",
            "trigger": "beat",
        },
    ),
    BeatEntry(
        name="daily-pipeline-evening",
        task="mijual.daily_pipeline",
        hour=19,
        minute=30,
        kwargs={
            "window_days": DEFAULT_WINDOW_DAYS,
            "label": "daily-evening",
            "trigger": "beat",
        },
    ),
    BeatEntry(
        name="weekly-resync",
        task="mijual.daily_pipeline",
        hour=4,
        minute=30,
        day_of_week=0,
        kwargs={
            "window_days": RESYNC_WINDOW_DAYS,
            "label": "weekly-resync",
            "trigger": "beat",
            # A quarter of filings costs more discovery + detail calls than two
            # weeks does; still ~10% of one day's 20,000-request quota (O-1).
            "collect_max_requests": 1500,
            "bodydoc_max_requests": 600,
            "collect_max_documents": 400,
        },
    ),
)
