"""The things scheduling must not get wrong (P2.S6, extended by P5.S9).

No broker, no worker, and no database except an in-memory SQLite one: a test that
needed live Celery would be testing Celery. What is tested is what a wrong
schedule would actually cost — polling the wrong days, a beat entry naming a task
that does not exist, two runs double-fetching the same 본문, one stage's failure
taking the run down with it, and (P5.S9) a run that leaves no record of itself or
skips the offline re-derivation that keeps the served numbers from ageing.
"""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from mijual.beat import BEAT_ENTRIES, lock_key
from mijual.db.models import Base, PipelineRun, RightsType
from mijual.scheduler import FileLock, PipelineConfig, run_pipeline, window_for
from mijual.scheduler.locks import KEY_PREFIX, RedisLock
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
    # P5.S9 wired the offline re-derivation onto the schedule. Until it did, the
    # ① extras and the landing headline aged silently while 기준시각 said the
    # corpus was fresh (P5.S3's deviation note). Order is a data dependency:
    # reparse rewrites `facts`, snapshot builds `LapseRow` from them.
    assert config.stages == (
        "collect", "bodydoc", "extract", "gates", "reparse", "snapshot",
    )
    assert config.stages.index("reparse") < config.stages.index("snapshot")
    assert config.stages.index("gates") < config.stages.index("reparse")
    # Neither of the two spends anything, which is why scheduling them is free.
    assert config.trigger == "manual" and config.write_run_log is True


def test_a_deployment_may_raise_the_extract_ceiling_but_never_lower_an_explicit_one(monkeypatch):
    """P4.F4: the ceiling is the one knob a corpus can outgrow, and it is money.

    Production ended its 2026-09-02 evening run at ``60 of 60 calls, BUDGET
    EXHAUSTED`` with a 정정 backlog still waiting, so ``MIJUAL_EXTRACT_MAX_CALLS``
    makes the ceiling deployment configuration. Every scheduled run reaches the
    pipeline through ``from_kwargs``, and no beat entry names the ceiling — so a
    wrong answer here is either a silent under-run or an unbounded spend.
    """
    monkeypatch.setenv("MIJUAL_EXTRACT_MAX_CALLS", "300")
    assert PipelineConfig.from_kwargs(window_days=14).extract_max_calls == 300
    # An explicit ceiling still says the last word.
    assert PipelineConfig.from_kwargs(extract_max_calls=5).extract_max_calls == 5


def test_the_beat_declaration_is_the_only_one_and_the_ops_panel_reads_it():
    """The schedule Celery fires and the schedule the panel renders are one object.

    R7: "beat 스케줄 표는 Celery beat 설정에서 렌더 (하드코딩 금지 — 설정이 곧
    진실)". The panel cannot import ``mijual.scheduler`` (it pulls the collector
    and the extractor), so the declaration lives in ``mijual.beat`` and both ends
    read it.
    """
    from mijual.scheduler.app import BEAT_SCHEDULE

    assert set(BEAT_SCHEDULE) == {e.name for e in BEAT_ENTRIES}
    # A beat-fired run says so, so the run log's 트리거 column is a fact.
    assert all(e.kwargs.get("trigger") == "beat" for e in BEAT_ENTRIES)
    assert lock_key("pipeline") == f"{KEY_PREFIX}pipeline" == "mijual:lock:pipeline"

    weekly = next(e for e in BEAT_ENTRIES if e.day_of_week == 0)
    # Celery numbers Sunday 0; Python numbers Monday 0. Getting that backwards
    # would make the panel say the weekly pass was due on the wrong day.
    due = weekly.due_between(
        datetime(2026, 8, 16, 0, 0), datetime(2026, 8, 23, 23, 59)  # Sun → Sun
    )
    assert [d.isoformat() for d in due] == ["2026-08-16T04:30:00", "2026-08-23T04:30:00"]
    morning = next(e for e in BEAT_ENTRIES if e.name == "daily-pipeline-morning")
    assert morning.spec == "07:30 daily"
    assert len(morning.due_between(datetime(2026, 8, 20), datetime(2026, 8, 22, 23, 59))) == 3


def test_a_run_writes_itself_down_and_the_row_carries_the_run_s_own_spend_line():
    """R7's 최근 실행 표, round-tripped: the row is the run's own report.

    Opened before the first stage and closed after the last, so a crashed run
    leaves an unfinished row rather than none — and the ▷ line is stored
    **verbatim** as the pipeline prints it (경계 = 출처: in the ops panel ▷ is
    quoted pipeline output and must never become 「추정」).
    """
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)

    result = run_pipeline(
        PipelineConfig(
            stages=(), use_lock=False, label="test-run", trigger="beat", bgn="20260101",
            end="20260131",
        ),
        factory=factory,
    )
    with factory() as session:
        rows = session.scalars(select(PipelineRun)).all()
        assert len(rows) == 1
        row = rows[0]
        assert row.label == "test-run" and row.trigger == "beat"
        assert (row.window_bgn, row.window_end) == ("20260101", "20260131")
        assert row.finished_at is not None and row.ok is True
        assert row.spend_line == result.spend_line
        assert "▷" in row.spend_line and "추정" not in row.spend_line
        assert row.requests == 0 and row.calls == 0 and row.stages == []

    # A skipped run did nothing, so it is not a run: the lock chip is where
    # contention shows up, and a row here would count non-runs as runs.
    held = FileLock("var/locks/test-p5s9.lock")
    assert held.acquire() is True
    try:
        skipped = run_pipeline(
            PipelineConfig(
                redis_url="", lock_dir="var/locks", lock_name="test-p5s9", stages=(),
                label="skipped",
            ),
            factory=factory,
        )
    finally:
        held.release()
    assert skipped.skipped is True
    with factory() as session:
        assert session.scalar(select(PipelineRun).where(PipelineRun.label == "skipped")) is None
    engine.dispose()
