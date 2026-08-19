"""The four things scheduling must not get wrong (P2.S6).

No broker, no worker, no database: a test that needed live Celery would be
testing Celery. What is tested is what a wrong schedule would actually cost —
polling the wrong days, a beat entry naming a task that does not exist, two runs
double-fetching the same 본문, and one stage's failure taking the run down with
it.
"""

from __future__ import annotations

from datetime import date

from mijual.db.models import RightsType
from mijual.scheduler import FileLock, PipelineConfig, run_pipeline, window_for
from mijual.scheduler.locks import RedisLock
from mijual.scheduler.pipeline import stage_gates


def test_the_window_is_kst_anchored_inclusive_and_overridable():
    """A worker in UTC must still poll the Korean calendar day (N3's window)."""
    assert window_for(14, today=date(2026, 8, 20)) == ("20260806", "20260820")
    assert window_for(0, today=date(2026, 8, 20)) == ("20260820", "20260820")
    rolling = PipelineConfig(window_days=3).window(today=date(2026, 8, 20))
    assert rolling == ("20260817", "20260820")
    # An explicit window (offline evidence runs) wins over the rolling one.
    pinned = PipelineConfig(bgn="20260101", end="20260331")
    assert pinned.window(today=date(2026, 8, 20)) == ("20260101", "20260331")


def test_every_beat_entry_names_a_registered_task_and_carries_usable_kwargs():
    """A beat entry is a string until beat fires it — resolve it now, not at 07:30."""
    from mijual.scheduler.app import BEAT_SCHEDULE, TIMEZONE, app

    assert app.conf.timezone == TIMEZONE == "Asia/Seoul"
    assert app.conf.enable_utc is False
    assert BEAT_SCHEDULE, "beat schedule must not be empty"
    for name, entry in BEAT_SCHEDULE.items():
        assert entry["task"] in app.tasks, f"{name} names an unregistered task"
        # Beat sends JSON; the kwargs have to survive the trip into a config.
        config = PipelineConfig.from_kwargs(**(entry.get("kwargs") or {}))
        assert config.collect_max_requests and config.extract_max_calls, (
            f"{name} would run without a ceiling"
        )
        assert config.window_days > 0


def test_a_second_run_cannot_take_the_lock_and_a_late_release_spares_the_successor(tmp_path):
    """Overlap is the one thing idempotent upserts cannot repair (spent quota)."""
    first = FileLock(tmp_path / "pipeline.lock")
    second = FileLock(tmp_path / "pipeline.lock")
    assert first.acquire() is True
    assert second.acquire() is False
    assert first.release() is True
    assert second.acquire() is True
    second.release()

    # Same contract on Redis, including the case that matters: a run whose TTL
    # expired must not delete the lock its successor now holds.
    class FakeRedis:
        def __init__(self):
            self.store: dict[str, str] = {}

        def set(self, key, value, nx=False, px=None):
            if nx and key in self.store:
                return None
            self.store[key] = value
            return True

        def get(self, key):
            return self.store.get(key)

        def delete(self, key):
            self.store.pop(key, None)

    client = FakeRedis()
    a, b = RedisLock(client, ttl_s=1), RedisLock(client, ttl_s=1)
    assert a.acquire() is True
    assert b.acquire() is False
    client.store[a.key] = b.token  # a's TTL lapsed; b took over
    assert a.release() is False
    assert client.store[a.key] == b.token


def test_a_run_that_cannot_take_the_lock_does_nothing_and_says_so(tmp_path):
    held = FileLock(tmp_path / "pipeline.lock")
    assert held.acquire() is True
    result = run_pipeline(
        PipelineConfig(redis_url="", lock_dir=str(tmp_path), stages=(), label="test"),
        factory=object(),
    )
    assert result.skipped is True and result.stages == []
    assert result.ok is False and "another run holds" in " ".join(result.notes)
    held.release()


def test_one_failing_stage_is_a_reported_status_not_a_dead_run():
    """A 07:30 job must report what broke, keep the others, and leak nothing."""

    class Exploding:
        def __call__(self, *a, **k):
            raise RuntimeError("postgres is not listening")

    outcome = stage_gates(PipelineConfig(), Exploding())
    assert outcome.status == "error"
    assert outcome.summary.startswith("RuntimeError:")
    assert outcome.requests == 0 and outcome.calls == 0


def test_the_defaults_are_ceilings_and_r2_is_not_scheduled_for_the_llm():
    """② is structured-only (N6) — a scheduled LLM read of it would be waste."""
    config = PipelineConfig()
    assert config.collect_max_requests and config.bodydoc_max_requests
    assert config.extract_max_calls
    assert RightsType.CONVERTIBLE_OVERHANG not in config.extract_rights
    assert config.stages == ("collect", "bodydoc", "extract", "gates")
