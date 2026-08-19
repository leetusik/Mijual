"""``mijual.scheduler`` — the pipeline on a schedule (P2.S6).

The four stages built by ``P2.S1``–``P2.S5`` are idempotent CLIs; this package
makes them a **job**: Celery beat + a worker on the Redis ``compose.yaml``
already reserves (host 6380, ``scheduling`` profile), one lock so runs cannot
overlap, and an explicit ceiling on every stage that spends.

Three things it is, and one it is not.

* **A job topology, not a service.** ``collect → bodydoc → extract → gates``, in
  that order, because each stage consumes what the previous one persisted.
* **Bounded by construction.** ``DartClient(max_requests=…)`` and
  ``GeminiClient(max_calls=…)`` refuse the next unit past the ceiling, so a
  scheduled run cannot spend without a bound even if a window suddenly widens.
* **Runnable without a broker.** ``python -m mijual.scheduler once`` runs the
  identical code path synchronously — the testable path, the ops fallback, and
  what ``P2.S7``/``P2.S8`` reuse.
* **Not in any request path.** Nothing here is imported by P3's HTTP layer; the
  board reads persisted rows. A worker that never runs leaves the board stale,
  never dark — the 결격 rule read from the scheduling side.

    .venv/bin/python -m mijual.scheduler once --window 14      # one live run
    .venv/bin/python -m mijual.scheduler once --offline        # 0 req / 0 calls
    .venv/bin/python -m mijual.scheduler schedule              # what beat will do

:mod:`mijual.scheduler.app` (the Celery app) is imported **only** by the worker,
by beat and by the ``schedule`` command, so everything else here works whether or
not Celery is installed.
"""

from __future__ import annotations

from mijual.scheduler.config import (
    DEFAULT_WINDOW_DAYS,
    RESYNC_WINDOW_DAYS,
    STAGES,
    PipelineConfig,
    window_for,
)
from mijual.scheduler.locks import FileLock, NullLock, RedisLock, make_lock
from mijual.scheduler.pipeline import (
    PipelineResult,
    StageResult,
    run_pipeline,
    session_factory_for,
    stage_bodydoc,
    stage_collect,
    stage_extract,
    stage_gates,
)

__all__ = [
    "DEFAULT_WINDOW_DAYS",
    "FileLock",
    "NullLock",
    "PipelineConfig",
    "PipelineResult",
    "RESYNC_WINDOW_DAYS",
    "RedisLock",
    "STAGES",
    "StageResult",
    "make_lock",
    "run_pipeline",
    "session_factory_for",
    "stage_bodydoc",
    "stage_collect",
    "stage_extract",
    "stage_gates",
    "window_for",
]
