"""What one scheduled run is allowed to do, and over which window.

Every knob here is a **ceiling or a window**, because the two things a scheduled
job must never do are spend without a bound and drift off the dates it was meant
to cover. The defaults are the ones the beat schedule runs with; a task, a CLI
flag or a beat entry may override any of them by keyword, and the run reports the
values it actually used.

Two constraints from the phase are encoded rather than commented:

* **budgets stay structural** — ``collect_max_requests`` / ``bodydoc_max_requests``
  reach :class:`~mijual.dart.DartClient` as ``max_requests`` and
  ``extract_max_calls`` reaches :class:`~mijual.extract.client.GeminiClient` as
  ``max_calls``; both already refuse the next unit past the ceiling (N25, N42),
  so a runaway schedule is impossible by construction rather than by discipline;
* **the window rolls on the ORIGINAL date** — a 정정 filed today can belong to an
  event filed months ago, and pairing re-windows the detail fetch on the
  original's date (N3), so a two-week discovery window is enough to catch both
  new filings and corrections of old ones. The weekly wider pass exists for the
  stragglers whose corp-scoped pairing query needs a second look.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date, timedelta

from mijual.beat import (
    DEFAULT_WINDOW_DAYS,
    NOTIFY_MAX_MAILS,
    RESYNC_WINDOW_DAYS,
)
from mijual.calc import today_kst
from mijual.config import load_settings
from mijual.collect.discovery import DEFAULT_MARKETS
from mijual.collect.targets import DEFAULT_ENDPOINTS
from mijual.db.models import RightsType

__all__ = [
    "DEFAULT_EXTRACT_MAX_CALLS",
    "DEFAULT_STAGES",
    "DEFAULT_WINDOW_DAYS",
    "NOTIFY_MAX_MAILS",
    "RESYNC_WINDOW_DAYS",
    "STAGES",
    "PipelineConfig",
    "window_for",
]

#: Stage order. Each stage consumes what the previous one persisted.
#:
#: ``reparse`` and ``snapshot`` were added by ``P5.S9``. They are the offline
#: re-derivation the phase notes already prescribe after any collection
#: (``bodydoc backfill`` → ``gates run`` → ``estimate reparse`` → ``estimate
#: snapshot``), and until they ran on the schedule the ① extras and the landing
#: headline aged silently while 기준시각 said the corpus was fresh. Both spend
#: **0 requests and 0 model calls**, so putting them on the beat costs nothing
#: and closes the one way this corpus could serve a stale number without saying
#: so. ``reparse`` precedes ``snapshot`` because ``LapseRow`` is built from
#: ``facts``.
STAGES = ("collect", "bodydoc", "extract", "gates", "reparse", "snapshot", "notify")

#: What a run does when nobody says otherwise: the **six corpus stages**, in
#: order. ``notify`` is a known stage (above) but not a default one, and the
#: distinction is the whole reason there are two tuples. ``P4.S2``'s D-day mail
#: is not corpus work: it has a different failure mode (an outward action to a
#: person), a different ceiling (mails, not requests), and — decisively — it must
#: **not share the corpus lock**, because a notify run skipped for lock
#: contention would silently send no mail that day and leave no run row to say
#: so. It therefore runs as its own beat entry on ``lock_name="notify"``
#: (:data:`mijual.beat.NOTIFY_LOCK_NAME`) rather than as a seventh step of the
#: 07:30 pipeline.
DEFAULT_STAGES = ("collect", "bodydoc", "extract", "gates", "reparse", "snapshot")

#: Rights types whose prose fields are read by the scheduled extraction. ② is
#: **deliberately absent**: it is collected by the same ``collect`` stage as
#: ①/③ (``DEFAULT_ENDPOINTS`` carries ``cvbdIsDecsn`` since ``P2.S7``), but its
#: countdown is entirely ``API`` tier (N6), so a scheduled LLM pass over it would
#: buy narrative colour with money. Fields 6–8 are run by hand, capped, over the
#: urgency set only — ``python -m mijual.cb extract``.
DEFAULT_EXTRACT_RIGHTS = (RightsType.SUBSCRIPTION_WARRANT, RightsType.APPRAISAL_RIGHT)

#: How many model calls one run may spend when nobody says otherwise. It stayed a
#: bare literal until ``P4.F4``, when the production corpus outgrew it: the
#: 2026-09-02 evening run ended ``60 of 60 calls, BUDGET EXHAUSTED`` with a 정정
#: backlog still waiting, and the operator asked for a relaxed ceiling. Raising it
#: is now deployment configuration (``MIJUAL_EXTRACT_MAX_CALLS``) rather than a
#: code change — but the **dataclass default stays 60**, so an offline test, a
#: fixture run and this module's own reasoning are unaffected by the environment.
DEFAULT_EXTRACT_MAX_CALLS = 60


def env_extract_max_calls() -> int | None:
    """``MIJUAL_EXTRACT_MAX_CALLS`` if the deployment sets one, else ``None``.

    One reader for the two paths that may take it — :meth:`PipelineConfig.from_kwargs`
    (beat and every Celery task) and ``python -m mijual.scheduler once`` — so the
    key is spelled once and the two can never disagree about which wins. Neither
    path lets it override an explicit ceiling: a beat entry that names
    ``extract_max_calls`` and a CLI ``--max-calls`` both still say the last word.
    An unparseable value raises here, in :func:`mijual.config.load_settings`, and
    the process stops rather than running the schedule at a budget nobody chose.
    """
    return load_settings().extract_max_calls


def window_for(days: int, *, today: date | None = None) -> tuple[str, str]:
    """``days`` back from today (KST) to today, as ``YYYYMMDD`` bounds.

    Inclusive at both ends and anchored on **KST**, not on the host's timezone:
    a worker running in UTC must not poll yesterday's Korean calendar day.
    """
    if days < 0:
        raise ValueError(f"window must not be negative: {days}")
    end = today if today is not None else today_kst()
    start = end - timedelta(days=days)
    return (start.strftime("%Y%m%d"), end.strftime("%Y%m%d"))


@dataclass(frozen=True)
class PipelineConfig:
    """One run's window, ceilings and stage list."""

    # -- window ------------------------------------------------------------
    window_days: int = DEFAULT_WINDOW_DAYS
    #: Explicit window override — an offline evidence run points these at a
    #: window the response cache actually holds. ``None`` means "rolling".
    bgn: str | None = None
    end: str | None = None
    markets: tuple[str, ...] = DEFAULT_MARKETS
    endpoints: tuple[str, ...] = DEFAULT_ENDPOINTS

    # -- ceilings (structural, never optional) ------------------------------
    collect_max_requests: int | None = 500
    collect_max_documents: int | None = 150
    bodydoc_max_requests: int | None = 200
    bodydoc_max_documents: int | None = 100
    extract_max_calls: int | None = DEFAULT_EXTRACT_MAX_CALLS
    extract_rights: tuple[RightsType, ...] = DEFAULT_EXTRACT_RIGHTS
    #: §7 #10 (정정 재추출 + diff) shares ``extract_max_calls`` with the prose pass.
    extract_corrections: bool = True

    # -- the notify stage (P4.S2) -------------------------------------------
    #: The outward-mail ceiling for one run, the same **structural** shape as the
    #: request and call ceilings above: :mod:`mijual.notify` stops at it and
    #: reports ``budget_exhausted``, which is a status, not an exception.
    notify_max_mails: int | None = NOTIFY_MAX_MAILS
    #: ``YYYYMMDD`` — anchor the D-day arithmetic on another day instead of today
    #: (KST). An **inspection knob**: it is how the gate demo and a smoke run
    #: reach a deadline that is not exactly 7/3/1/0 days away right now. Unset in
    #: every beat entry, because a scheduled send must anchor on the real day.
    notify_today: str | None = None

    # -- execution ---------------------------------------------------------
    stages: tuple[str, ...] = DEFAULT_STAGES
    offline: bool = False
    cache_dir: str | None = None
    database_url: str | None = None
    #: Redis URL for the run lock; ``None`` → ``Settings.redis_url``.
    redis_url: str | None = None
    lock_name: str = "pipeline"
    lock_ttl_s: int = 3600
    use_lock: bool = True
    #: Where the file-lock fallback lives when no broker answers (default ``var/locks``).
    lock_dir: str | None = None
    label: str = "daily"
    #: What fired this run — ``beat`` when the schedule did (every entry in
    #: :data:`mijual.beat.BEAT_ENTRIES` carries it in its kwargs), ``manual``
    #: otherwise. It is the 트리거 column of R7's 최근 실행 표, and the default is
    #: ``manual`` on purpose: a run that does not say the schedule fired it did
    #: not, and a panel that guessed would make a missed beat look like a run.
    trigger: str = "manual"
    #: Write one :class:`~mijual.db.models.PipelineRun` row per run. Off only for
    #: a test or an inspection run that must leave the operator's log untouched.
    write_run_log: bool = True
    notes: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        unknown = [s for s in self.stages if s not in STAGES]
        if unknown:
            raise ValueError(f"not a pipeline stage: {unknown} (known: {list(STAGES)})")

    def window(self, *, today: date | None = None) -> tuple[str, str]:
        """The window this run collects, explicit override winning."""
        if self.bgn and self.end:
            return (self.bgn, self.end)
        rolling = window_for(self.window_days, today=today)
        return (self.bgn or rolling[0], self.end or rolling[1])

    def replace(self, **changes) -> "PipelineConfig":
        return replace(self, **changes)

    @classmethod
    def from_kwargs(cls, **kwargs) -> "PipelineConfig":
        """Build from beat/task kwargs — tuples and rights ids come as lists/strings.

        Beat entries and Celery messages are JSON, so ``markets=["Y","K"]`` and
        ``extract_rights=["R1"]`` have to survive the round trip.

        This is also where a **deployment's** extract ceiling arrives (``P4.F4``):
        every scheduled run reaches the pipeline through here, and none of the
        beat entries names ``extract_max_calls``, so kwargs that carry no ceiling
        take :func:`env_extract_max_calls` and kwargs that carry one keep it.
        """
        if "extract_max_calls" not in kwargs:
            ceiling = env_extract_max_calls()
            if ceiling is not None:
                kwargs["extract_max_calls"] = ceiling
        rights = kwargs.pop("extract_rights", None)
        if rights is not None:
            kwargs["extract_rights"] = tuple(
                r if isinstance(r, RightsType) else RIGHTS_BY_ID[r] for r in rights
            )
        for key in ("markets", "endpoints", "stages", "notes"):
            if key in kwargs and kwargs[key] is not None:
                kwargs[key] = tuple(kwargs[key])
        return cls(**kwargs)

    def describe(self) -> str:
        """One line, counts and ceilings only — never a URL that could carry a key."""
        bgn, end = self.window()
        return (
            f"window {bgn}~{end} ({self.window_days}d) "
            f"stages={'+'.join(self.stages)} "
            f"budgets collect<={self.collect_max_requests} req, "
            f"bodydoc<={self.bodydoc_max_requests} req, "
            f"extract<={self.extract_max_calls} calls"
            + (f", notify<={self.notify_max_mails} mail(s)" if "notify" in self.stages else "")
            + (f" notify_today={self.notify_today}" if self.notify_today else "")
            + (" [offline]" if self.offline else "")
        )


#: ``R1``/``R2``/``R3`` as they appear in a beat entry or a CLI flag.
RIGHTS_BY_ID = {
    "R1": RightsType.SUBSCRIPTION_WARRANT,
    "R2": RightsType.CONVERTIBLE_OVERHANG,
    "R3": RightsType.APPRAISAL_RIGHT,
}
