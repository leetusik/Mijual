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

from mijual.calc import today_kst
from mijual.collect.discovery import DEFAULT_MARKETS
from mijual.collect.targets import DEFAULT_ENDPOINTS
from mijual.db.models import RightsType

__all__ = [
    "DEFAULT_WINDOW_DAYS",
    "RESYNC_WINDOW_DAYS",
    "STAGES",
    "PipelineConfig",
    "window_for",
]

#: Rolling discovery window of the daily run, in days back from today (KST).
DEFAULT_WINDOW_DAYS = 14
#: The weekly straggler pass. Wide enough to re-reach a quarter of filings.
RESYNC_WINDOW_DAYS = 90
#: Stage order. Each stage consumes what the previous one persisted.
STAGES = ("collect", "bodydoc", "extract", "gates")

#: Rights types whose prose fields are read by the scheduled extraction. ② is
#: structured-only (N6) and needs no LLM, so it is not listed here — ``P2.S7``
#: registers its own collection task instead.
DEFAULT_EXTRACT_RIGHTS = (RightsType.SUBSCRIPTION_WARRANT, RightsType.APPRAISAL_RIGHT)


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
    extract_max_calls: int | None = 60
    extract_rights: tuple[RightsType, ...] = DEFAULT_EXTRACT_RIGHTS
    #: §7 #10 (정정 재추출 + diff) shares ``extract_max_calls`` with the prose pass.
    extract_corrections: bool = True

    # -- execution ---------------------------------------------------------
    stages: tuple[str, ...] = STAGES
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
        """
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
            + (" [offline]" if self.offline else "")
        )


#: ``R1``/``R2``/``R3`` as they appear in a beat entry or a CLI flag.
RIGHTS_BY_ID = {
    "R1": RightsType.SUBSCRIPTION_WARRANT,
    "R2": RightsType.CONVERTIBLE_OVERHANG,
    "R3": RightsType.APPRAISAL_RIGHT,
}
