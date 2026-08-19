"""Gemini wrapper — structured output, a hard call ceiling, and an honest bill.

Three things this has that a bare ``genai.Client`` does not, all of them lessons
this repo already paid for:

**A budget that is structural, not a habit** (N25). ``max_calls`` refuses the
next live call with :class:`CallBudgetExceeded` instead of trusting a loop to
stop, exactly as ``DartClient(max_requests=…)`` does for OpenDART quota. Here it
guards money rather than quota, so it is on by default in the CLI.

**A ledger.** Every call's prompt / thinking / output tokens are accumulated and
priced, because "the LLM slice" is the only part of P2 that spends real money and
the phase rule is that facts carry evidence and estimates carry ``▷``. The rate
card below is an estimate; the token counts are measurements.

**Key safety.** The credential is read in-process from :mod:`mijual.config`,
resolved on first *use*, and never printed, logged, or written to a report — the
same structural rule the DART client follows (N18).

**The thinking level is per task, and routine reading is explicitly cheap**
(operator directive, 2026-08-20 — an amendment to D-4). The credential's project
preset applies **HIGH** thinking to every call, which is right for reasoning and
wasteful for the schema extraction that makes up most of this package's spend:
the model is copying a value and a verbatim quote out of a 7,000-character
document, not deciding anything. So :data:`THINKING_BY_TASK` sets an explicit
level per task — ``LOW`` for the three prose tasks — while a task left at ``None``
**inherits the operator's preset**, which is how the harder 정정 interpretation
still gets the reasoning it is measured against (N41).

Two properties keep that honest: the level actually used is recorded on every
:class:`CallResult` (and stored per call), and it is a *keyword* on
:meth:`GeminiClient.generate_json`, so a caller that needs more thinking asks for
it explicitly rather than by editing a default.
"""

from __future__ import annotations

import json
import random
import time
from dataclasses import dataclass, field
from typing import Any

from mijual.config import Settings, load_settings

__all__ = [
    "CallBudgetExceeded",
    "CallResult",
    "DEFAULT_MODEL",
    "DEFAULT_THINKING_LEVEL",
    "GeminiClient",
    "GeminiError",
    "INHERIT_PRESET",
    "PRICING",
    "Pricing",
    "THINKING_BY_TASK",
    "Usage",
    "UsageLedger",
]

#: Confirmed by the operator (O-2) and present in the credential's model list as
#: ``models/gemini-3.7-flash`` (version ``3.7-flash-08-2026``).
DEFAULT_MODEL = "gemini-3.7-flash"

#: What a task asks for when it wants the credential's project-side preset —
#: i.e. *do not send a thinking config at all*. Spelled out because ``None`` in a
#: mapping is ambiguous between "no opinion" and "no thinking".
INHERIT_PRESET = None

#: Per-task thinking level (``google.genai.types.ThinkingLevel``: ``MINIMAL`` /
#: ``LOW`` / ``MEDIUM`` / ``HIGH``), operator directive 2026-08-20.
#:
#: * the three **prose** tasks are routine schema extraction — find a value, copy
#:   the sentence it came from — and the deterministic layer re-checks every one
#:   of them afterwards, so they run at ``LOW``;
#: * **correction** is the one task that *reasons*: it diffs two versions, works
#:   out which changes moved a D-day, and is scored against the deterministic
#:   정정사항 rows (N41: 121 changes, 0 unsupported). It keeps the operator's
#:   preset, because that measurement was taken at the preset level;
#: * **probe** keeps the preset too — its whole job is to observe what the preset
#:   does.
#:
#: gemini-3.7-flash is a 3.x model, so the knob is ``thinking_level``; the older
#: ``thinking_budget`` (token count) is not used here.
THINKING_BY_TASK: dict[str, str | None] = {
    "r1_prose": "LOW",
    "r2_prose": "LOW",
    "r3_prose": "LOW",
    "correction": INHERIT_PRESET,
    "probe": INHERIT_PRESET,
}

#: What a task not named above gets. Cheap by default is the point of the
#: directive: a new routine reader should not silently inherit HIGH.
DEFAULT_THINKING_LEVEL: str | None = "LOW"


@dataclass(frozen=True)
class Pricing:
    """▷ Published rate card, USD per 1M tokens. Not a billed figure."""

    input_per_m: float
    output_per_m: float
    #: Thinking tokens are billed as output tokens.
    note: str = ""


#: ▷ Estimate. gemini-3.7-flash introductory pricing (through 2026-12-31) as
#: published on the 2026-08 rate card: $0.75 / $3.75 per 1M input / output
#: tokens, standard $1.50 / $7.50 from 2027-01-01. Every cost this package
#: reports is therefore an estimate, tagged ``▷``, never a billed amount.
PRICING: dict[str, Pricing] = {
    "gemini-3.7-flash": Pricing(0.75, 3.75, "introductory rate through 2026-12-31"),
}


class GeminiError(RuntimeError):
    """A call failed after retries. Never carries key material."""


class CallBudgetExceeded(GeminiError):
    """``max_calls`` reached — the run stops before spending more money."""


@dataclass(frozen=True)
class Usage:
    prompt_tokens: int = 0
    thoughts_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0

    @property
    def billed_output(self) -> int:
        """Thinking tokens bill as output tokens."""
        return self.output_tokens + self.thoughts_tokens


@dataclass
class UsageLedger:
    """Per-run accounting: what was spent, in tokens and in ▷ dollars."""

    model: str = DEFAULT_MODEL
    attempts: int = 0
    calls_ok: int = 0
    calls_failed: int = 0
    prompt_tokens: int = 0
    thoughts_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    by_task: dict[str, int] = field(default_factory=dict)

    def add(self, task: str, usage: Usage, *, ok: bool) -> None:
        self.calls_ok += int(ok)
        self.calls_failed += int(not ok)
        self.prompt_tokens += usage.prompt_tokens
        self.thoughts_tokens += usage.thoughts_tokens
        self.output_tokens += usage.output_tokens
        self.total_tokens += usage.total_tokens
        self.by_task[task] = self.by_task.get(task, 0) + 1

    @property
    def cost_usd(self) -> float:
        """▷ Estimated spend for this run."""
        return cost_of(
            self.model,
            Usage(self.prompt_tokens, self.thoughts_tokens, self.output_tokens, self.total_tokens),
        )

    def render(self) -> str:
        return (
            f"calls      : {self.calls_ok} ok, {self.calls_failed} failed, "
            f"{self.attempts} HTTP attempt(s) — {dict(sorted(self.by_task.items()))}\n"
            f"tokens     : prompt {self.prompt_tokens:,} + thinking {self.thoughts_tokens:,} "
            f"+ output {self.output_tokens:,} = {self.total_tokens:,}\n"
            f"cost       : ▷ ${self.cost_usd:.4f} estimated ({self.model} rate card, not billed)"
        )


def cost_of(model: str, usage: Usage) -> float:
    price = PRICING.get(model)
    if price is None:
        return 0.0
    return (
        usage.prompt_tokens * price.input_per_m + usage.billed_output * price.output_per_m
    ) / 1_000_000


@dataclass
class CallResult:
    """One call's outcome — payload plus everything the ledger and DB need."""

    task: str
    status: str  # ok | invalid_json | error
    payload: dict[str, Any] | None = None
    text: str | None = None
    usage: Usage = field(default_factory=Usage)
    model: str = DEFAULT_MODEL
    model_version: str | None = None
    latency_ms: int = 0
    attempts: int = 0
    error: str | None = None
    #: The thinking level this call asked for; ``None`` = the project preset.
    #: Recorded rather than assumed, because the same prompt costs different
    #: money at different levels and the ledger has to be able to say why.
    thinking_level: str | None = None

    @property
    def ok(self) -> bool:
        return self.status == "ok" and self.payload is not None

    @property
    def cost_usd(self) -> float:
        return cost_of(self.model, self.usage)


#: Transient conditions worth another try (rate limit, backend hiccup, socket).
_RETRY_CODES = {408, 429, 500, 502, 503, 504}
_RETRY_NAMES = ("ServerError", "ClientError", "TimeoutError", "ConnectionError", "APIError")


class GeminiClient:
    """Schema-constrained Gemini calls with a ceiling and a ledger.

    Args:
        settings: process settings (defaults to :func:`mijual.config.load_settings`).
        model: model id — the operator's ``gemini-3.7-flash`` by default (D-4/O-2).
        max_calls: hard ceiling on live calls for this client's lifetime; the
            next call past it raises :class:`CallBudgetExceeded`.
        tries: attempts per call on transient failures (exponential backoff).
        dry_run: build prompts and count them, never call the API — how a run's
            size and cost are checked before spending anything.
    """

    def __init__(
        self,
        *,
        settings: Settings | None = None,
        model: str = DEFAULT_MODEL,
        max_calls: int | None = None,
        tries: int = 3,
        timeout_s: int = 180,
        api_key: str | None = None,
        dry_run: bool = False,
        thinking_by_task: dict[str, str | None] | None = None,
        log=None,
    ) -> None:
        self.settings = settings if settings is not None else load_settings()
        self.model = model
        self.max_calls = max_calls
        self.tries = tries
        self.timeout_s = timeout_s
        self.dry_run = dry_run
        self.thinking_by_task = (
            THINKING_BY_TASK if thinking_by_task is None else thinking_by_task
        )
        self.log = log
        self._api_key_override = api_key
        self._client = None
        #: Live calls started (attempts included) — what ``max_calls`` counts.
        self.call_count = 0
        self.ledger = UsageLedger(model=model)

    # -- credential -------------------------------------------------------
    @property
    def api_key(self) -> str:
        """Resolved on first *use*; never logged, stored or reported."""
        if self._api_key_override:
            return self._api_key_override
        return self.settings.require_gemini_api_key()

    def _sdk(self):
        if self._client is None:
            from google import genai  # local import: the SDK is only needed live

            self._client = genai.Client(api_key=self.api_key)
        return self._client

    # -- calls ------------------------------------------------------------
    def thinking_for(self, task: str) -> str | None:
        """The level this task runs at — ``None`` means "inherit the preset"."""
        return self.thinking_by_task.get(task, DEFAULT_THINKING_LEVEL)

    def generate_json(
        self,
        *,
        prompt: str,
        schema: dict[str, Any],
        task: str,
        temperature: float = 0.0,
        thinking_level: str | None = "auto",
    ) -> CallResult:
        """One schema-constrained call. Never raises on a model/API failure.

        Returns a :class:`CallResult` whose ``status`` says what happened, so a
        corpus run records the failure against the filing and keeps going. The
        one exception that *is* raised is :class:`CallBudgetExceeded` — spending
        past the ceiling must stop the run, not be logged and continued.

        ``thinking_level`` defaults to the sentinel ``"auto"``, meaning *look the
        task up in* :data:`THINKING_BY_TASK`. Passing ``None`` explicitly asks for
        the credential's project preset; passing a level name overrides both.
        """
        from google.genai import types  # local import (see :meth:`_sdk`)

        level = self.thinking_for(task) if thinking_level == "auto" else thinking_level
        if self.dry_run:
            return CallResult(
                task=task, status="dry_run", model=self.model, thinking_level=level
            )

        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_json_schema=schema,
            temperature=temperature,
            http_options=types.HttpOptions(timeout=self.timeout_s * 1000),
            # No config at all when the task inherits the preset: sending
            # ``ThinkingConfig()`` would still be an instruction, and the point of
            # inheriting is to leave an operator-side decision untouched.
            thinking_config=(
                types.ThinkingConfig(thinking_level=level) if level is not None else None
            ),
        )
        started = time.monotonic()
        attempts = 0
        last_error: str | None = None

        for attempt in range(self.tries):
            if self.max_calls is not None and self.call_count >= self.max_calls:
                raise CallBudgetExceeded(f"LLM call budget exhausted ({self.max_calls})")
            self.call_count += 1
            self.ledger.attempts += 1
            attempts += 1
            try:
                response = self._sdk().models.generate_content(
                    model=self.model, contents=prompt, config=config
                )
            except Exception as exc:  # noqa: BLE001 - classified below
                last_error = f"{type(exc).__name__}: {str(exc)[:200]}"
                if not _retryable(exc) or attempt == self.tries - 1:
                    break
                time.sleep(min(30.0, 2.0 * (2**attempt)) + random.uniform(0, 0.5))
                continue

            usage = _usage_of(response)
            latency = int((time.monotonic() - started) * 1000)
            text = response.text
            try:
                payload = json.loads(text) if text else None
            except json.JSONDecodeError as exc:
                self.ledger.add(task, usage, ok=False)
                return CallResult(
                    task=task,
                    status="invalid_json",
                    text=(text or "")[:4000],
                    usage=usage,
                    model=self.model,
                    model_version=getattr(response, "model_version", None),
                    latency_ms=latency,
                    attempts=attempts,
                    error=f"JSONDecodeError: {exc.msg}",
                    thinking_level=level,
                )
            self.ledger.add(task, usage, ok=True)
            return CallResult(
                task=task,
                status="ok",
                payload=payload,
                text=text,
                usage=usage,
                model=self.model,
                model_version=getattr(response, "model_version", None),
                latency_ms=latency,
                attempts=attempts,
                thinking_level=level,
            )

        self.ledger.add(task, Usage(), ok=False)
        return CallResult(
            task=task,
            status="error",
            model=self.model,
            latency_ms=int((time.monotonic() - started) * 1000),
            attempts=attempts,
            error=last_error,
            thinking_level=level,
        )

    def probe(self) -> CallResult:
        """The one-call sanity probe: does the model answer, and does the
        credential's **preset** thinking level show up in the usage metadata?

        Deliberately tiny, deliberately not configuring thinking — the point is
        to observe what the preset does, not to impose one (plan §Operator inputs).
        """
        schema = {
            "type": "object",
            "properties": {"answer": {"type": "string"}, "quote": {"type": "string"}},
            "required": ["answer", "quote"],
        }
        return self.generate_json(
            prompt=(
                "다음 문장에서 청약 시작일을 찾아 JSON으로 답하라: "
                "'청약기간은 2026년 09월 03일부터 09월 04일까지이다.' "
                "answer에는 YYYY-MM-DD, quote에는 근거 구절을 그대로 넣어라."
            ),
            schema=schema,
            task="probe",
        )


def _retryable(exc: Exception) -> bool:
    code = getattr(exc, "code", None) or getattr(exc, "status_code", None)
    if isinstance(code, int) and code in _RETRY_CODES:
        return True
    name = type(exc).__name__
    if name == "ClientError":  # 4xx: only 408/429 are worth retrying
        return isinstance(code, int) and code in _RETRY_CODES
    return any(name.endswith(suffix) for suffix in _RETRY_NAMES)


def _usage_of(response: Any) -> Usage:
    meta = getattr(response, "usage_metadata", None)
    if meta is None:
        return Usage()

    def get(name: str) -> int:
        return int(getattr(meta, name, None) or 0)

    return Usage(
        prompt_tokens=get("prompt_token_count"),
        thoughts_tokens=get("thoughts_token_count"),
        output_tokens=get("candidates_token_count"),
        total_tokens=get("total_token_count"),
    )
