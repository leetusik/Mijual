"""The agent's **own** Gemini client — streaming, function calling, a ceiling, a bill.

Deliberately not :class:`mijual.extract.client.GeminiClient`, and not a shared
base class either. `P6` Finding 1: ``mijual.extract`` is one of the three modules
the request path may not reach, and an agent that imported its wrapper would make
the architecture's loudest sentence false by an import rather than by a decision.
So the two ideas that matter are **copied**, and the two clients stay free to
diverge — which they immediately do, because that one answers with JSON and this
one streams tool calls:

* **a structural budget** (N25): ``max_calls`` refuses the next live call with
  :class:`CallBudgetExceeded` rather than trusting a loop to stop. Here it guards
  a *reader-facing* surface with no quota (R6-5: 질문 수 무제한), so the ceiling
  is per turn and its job is to bound one runaway conversation, never to ration
  the reader;
* **a ledger** — every call's tokens, the thinking level it ran at, and a ▷
  *estimated* cost (D-4: never a billed claim). Agent spend is a server fact and
  **joins no signed ops panel** (`P6` Finding 14): record it, leave 정확도·비용
  alone.

**Key safety** is unchanged from the pattern: the credential is read in-process
from :mod:`mijual.config`, resolved on first *use*, never printed, logged or put
in an error. A failed call is reported by exception **type name only**, because an
exception string is the one place a URL with a query parameter tends to surface.

**The seam that makes this testable.** The loop does not speak SDK: it speaks
:class:`UserMessage` / :class:`ModelMessage` / :class:`ToolMessage` in, and
:class:`TextChunk` / :class:`CallChunk` / :class:`UsageChunk` out. Translation to
``google.genai.types`` happens here, inside one method, behind a **local import**
— so the package still costs no SDK and no credential to import, and `P6.S3`'s
tests drive the **real** loop with a scripted fake that implements
:class:`ModelClient` in twenty lines and calls nothing.

**Automatic function calling is switched off on purpose.** The SDK will happily
run the tool loop itself; the operator's binding addition is that *we* build the
agent, and a loop we do not own is a loop we cannot cite, budget or gate.
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

from mijual.config import Settings, load_settings

__all__ = [
    "AgentGeminiClient",
    "CallBudgetExceeded",
    "CallChunk",
    "DEFAULT_MODEL",
    "DEFAULT_THINKING_LEVEL",
    "GeminiError",
    "INHERIT_PRESET",
    "Message",
    "ModelCall",
    "ModelChunk",
    "ModelClient",
    "ModelMessage",
    "PRICING",
    "Pricing",
    "TASK",
    "TextChunk",
    "ToolMessage",
    "Usage",
    "UsageChunk",
    "UsageLedger",
    "UserMessage",
    "cost_of",
]

#: D-4 / O-2 — the operator's model, present on the credential as
#: ``models/gemini-3.7-flash`` (version ``3.7-flash-08-2026``).
DEFAULT_MODEL = "gemini-3.7-flash"

#: The ledger's task name. One task, because one turn is one kind of work — but
#: it is a *name* rather than a literal so a later task (a summariser, say) lands
#: as a row in the same ledger instead of as an untagged call.
TASK = "agent_turn"

#: Asking for the credential's project-side preset = sending no thinking config
#: at all. Spelled out because ``None`` in a mapping reads as "no thinking".
INHERIT_PRESET = None

#: **The agent turn runs at `LOW`, and that is a decision, not a default drift.**
#: D-4's amendment says an unlisted task runs ``LOW`` and every call records the
#: level it ran at. Three reasons to stay there rather than reach for the preset:
#: the surface is free and unlimited (R6-5), so per-turn cost is the product's
#: cost; SSE's first token is a *reader-visible* latency (답변 준비 중 → 스트리밍)
#: and thinking happens before it; and the properties that must not fail —
#: 인용 강제, never-compute, 거절 가족 — are enforced **structurally** at the
#: generation boundary, so a cheaper level cannot produce an unverified claim, it
#: can only produce a blocked one. Raise it here (or per call) if a measurement
#: says tool choice suffers; the ledger records the level either way, which is
#: what makes two runs comparable.
THINKING_BY_TASK: dict[str, str | None] = {TASK: "LOW"}

#: What an unlisted task gets — D-4's own rule.
DEFAULT_THINKING_LEVEL: str | None = "LOW"


@dataclass(frozen=True)
class Pricing:
    """▷ Published rate card, USD per 1M tokens. Not a billed figure."""

    input_per_m: float
    output_per_m: float
    note: str = ""


#: ▷ Estimate, the same rate card D-4 records: gemini-3.7-flash introductory
#: $0.75 / $3.75 per 1M in/out through 2026-12-31, thinking billed as output.
PRICING: dict[str, Pricing] = {
    "gemini-3.7-flash": Pricing(0.75, 3.75, "introductory rate through 2026-12-31"),
}


class GeminiError(RuntimeError):
    """A model call failed. Never carries key material — see the module docstring."""


class CallBudgetExceeded(GeminiError):
    """``max_calls`` reached: the turn stops before spending more money.

    Raised *instead of* the next call, never after it, which is what makes the
    budget structural rather than a habit (N25). The loop turns it into an honest
    ``aborted`` terminal — a turn is never silently truncated.
    """


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


def cost_of(model: str, usage: Usage) -> float:
    """▷ Estimated USD for ``usage``. An unpriced model costs 0, never a guess."""
    price = PRICING.get(model)
    if price is None:
        return 0.0
    return (
        usage.prompt_tokens * price.input_per_m + usage.billed_output * price.output_per_m
    ) / 1_000_000


@dataclass
class UsageLedger:
    """What one turn (or one client's lifetime) spent, in tokens and ▷ dollars."""

    model: str = DEFAULT_MODEL
    calls: int = 0
    failures: int = 0
    prompt_tokens: int = 0
    thoughts_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    #: Every level this ledger's calls actually ran at, in call order. Plural
    #: because a caller may raise the level mid-turn, and a ▷ cost is only
    #: comparable across runs when the level behind it is known (D-4).
    levels: list[str] = field(default_factory=list)

    def add(self, usage: Usage, *, thinking_level: str | None, ok: bool = True) -> None:
        self.calls += 1
        self.failures += int(not ok)
        self.prompt_tokens += usage.prompt_tokens
        self.thoughts_tokens += usage.thoughts_tokens
        self.output_tokens += usage.output_tokens
        self.total_tokens += usage.total_tokens
        self.levels.append(thinking_level or "preset")

    @property
    def cost_usd(self) -> float:
        """▷ Estimated spend. Never a billed amount (D-4)."""
        return cost_of(
            self.model,
            Usage(
                self.prompt_tokens, self.thoughts_tokens, self.output_tokens, self.total_tokens
            ),
        )

    def payload(self) -> dict[str, Any]:
        """The ledger as JSON, for the terminal event and `P6.S4`'s log line."""
        return {
            "model": self.model,
            "calls": self.calls,
            "failures": self.failures,
            "prompt_tokens": self.prompt_tokens,
            "thoughts_tokens": self.thoughts_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "thinking_levels": list(self.levels),
            "cost_usd_estimate": round(self.cost_usd, 6),
        }

    def render(self) -> str:
        """One human line, with the ▷ mark the phase rule requires."""
        return (
            f"calls {self.calls} ({self.failures} failed) · "
            f"tokens prompt {self.prompt_tokens:,} + thinking {self.thoughts_tokens:,} "
            f"+ output {self.output_tokens:,} = {self.total_tokens:,} · "
            f"thinking {'/'.join(dict.fromkeys(self.levels)) or '-'} · "
            f"▷ ${self.cost_usd:.4f} estimated ({self.model} rate card, not billed)"
        )


# ---------------------------------------------------------------------------
# the neutral conversation — what the loop speaks
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ModelCall:
    """One function call the model decided to make. ``args`` are model input.

    ``thought_signature`` is opaque bytes the 3.x models attach to a function-call
    part and **require back** in the conversation history — a turn that replays a
    call without it is rejected with ``400 INVALID_ARGUMENT`` (measured live,
    2026-08-22). It is the model's own state, so it is carried through this
    neutral shape untouched and never inspected, logged or stored.
    """

    name: str
    args: Mapping[str, Any] = field(default_factory=dict)
    call_id: str | None = None
    thought_signature: bytes | None = None


@dataclass(frozen=True)
class UserMessage:
    text: str


@dataclass(frozen=True)
class ModelMessage:
    """A model turn as it happened: what it said, and what it decided to call."""

    text: str = ""
    calls: tuple[ModelCall, ...] = ()


@dataclass(frozen=True)
class ToolMessage:
    """One tool's answer, going back to the model as a function response."""

    name: str
    response: Mapping[str, Any]
    call_id: str | None = None


Message = UserMessage | ModelMessage | ToolMessage


@dataclass(frozen=True)
class TextChunk:
    """Prose as it streams. Thought summaries are dropped, never released."""

    text: str


@dataclass(frozen=True)
class CallChunk:
    call: ModelCall


@dataclass(frozen=True)
class UsageChunk:
    """The last chunk of every stream: what that one call cost.

    On the same channel as the content rather than on the client, so a fake is a
    generator and the per-turn ledger is assembled by the loop that owns the turn.
    """

    usage: Usage = field(default_factory=Usage)
    thinking_level: str | None = None
    model: str = DEFAULT_MODEL


ModelChunk = TextChunk | CallChunk | UsageChunk


@runtime_checkable
class ModelClient(Protocol):
    """What the loop needs from a model: one streaming call, chunks out.

    Implemented live by :class:`AgentGeminiClient` and, in the tests, by a
    scripted fake — the same loop runs against both, which is the only way a
    control-flow property ("the model chooses") can be *tested* rather than
    asserted in a docstring.
    """

    def stream(
        self, *, messages: Sequence[Message], system_instruction: str
    ) -> Iterator[ModelChunk]:  # pragma: no cover - protocol
        ...


class AgentGeminiClient:
    """Streaming Gemini calls with the tool declarations, a ceiling and a ledger.

    Args:
        settings: process settings (defaults to :func:`mijual.config.load_settings`).
        model: model id — ``gemini-3.7-flash`` (D-4).
        max_calls: hard ceiling on live calls for this client's lifetime. One
            client per turn means one turn's ceiling; the next call past it raises
            :class:`CallBudgetExceeded` **before** spending.
        thinking_level: ``"auto"`` looks :data:`THINKING_BY_TASK` up; ``None`` asks
            for the credential's project preset; a level name overrides both.
    """

    def __init__(
        self,
        *,
        settings: Settings | None = None,
        model: str = DEFAULT_MODEL,
        max_calls: int | None = 8,
        timeout_s: int = 120,
        api_key: str | None = None,
        thinking_level: str | None = "auto",
        temperature: float = 0.2,
    ) -> None:
        self.settings = settings
        self.model = model
        self.max_calls = max_calls
        self.timeout_s = timeout_s
        self.temperature = temperature
        self._thinking_level = thinking_level
        self._api_key_override = api_key
        self._client: Any = None
        self.call_count = 0
        self.ledger = UsageLedger(model=model)

    # -- credential -------------------------------------------------------
    @property
    def api_key(self) -> str:
        """Resolved on first *use*; never logged, stored or reported."""
        if self._api_key_override:
            return self._api_key_override
        if self.settings is None:
            self.settings = load_settings()
        return self.settings.require_gemini_api_key()

    def _sdk(self) -> Any:
        if self._client is None:
            from google import genai  # local import: the SDK is only needed live

            self._client = genai.Client(api_key=self.api_key)
        return self._client

    @property
    def thinking_level(self) -> str | None:
        """The level this client's calls run at. Recorded on every call (D-4)."""
        if self._thinking_level == "auto":
            return THINKING_BY_TASK.get(TASK, DEFAULT_THINKING_LEVEL)
        return self._thinking_level

    # -- one streaming call -----------------------------------------------
    def stream(
        self, *, messages: Sequence[Message], system_instruction: str
    ) -> Iterator[ModelChunk]:
        """One live streaming call. Yields text, function calls, then usage.

        Raises :class:`CallBudgetExceeded` before the call when the ceiling is
        reached, and :class:`GeminiError` when the stream fails — with the
        exception's **type name only**. There is no retry: a stream that died
        halfway has already put prose on the reader's screen, and R6's design for
        that is 부분 답변 유지 + 재시도, a decision the reader makes, not a second
        call the server makes behind them.
        """
        from google.genai import types  # local import (see :meth:`_sdk`)

        from mijual.agent.declarations import declarations

        if self.max_calls is not None and self.call_count >= self.max_calls:
            raise CallBudgetExceeded(f"turn call budget exhausted ({self.max_calls})")
        self.call_count += 1

        level = self.thinking_level
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            tools=[types.Tool(function_declarations=declarations())],
            # Ours is the loop (the operator's binding addition). The SDK's own
            # tool runner would take the control flow — and with it the fact rows,
            # the citation gate and the budget.
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            temperature=self.temperature,
            http_options=types.HttpOptions(timeout=self.timeout_s * 1000),
            # No config at all when the task inherits the preset: sending
            # ``ThinkingConfig()`` would still be an instruction.
            thinking_config=(
                types.ThinkingConfig(thinking_level=level) if level is not None else None
            ),
        )

        usage = Usage()
        try:
            stream = self._sdk().models.generate_content_stream(
                model=self.model, contents=_contents(messages, types), config=config
            )
            for chunk in stream:
                usage = _usage_of(chunk) or usage
                for part in _parts(chunk):
                    if getattr(part, "thought", False):
                        continue  # a thought summary is not the answer
                    call = getattr(part, "function_call", None)
                    if call is not None and getattr(call, "name", None):
                        yield CallChunk(
                            ModelCall(
                                name=call.name,
                                args=dict(getattr(call, "args", None) or {}),
                                call_id=getattr(call, "id", None),
                                thought_signature=getattr(part, "thought_signature", None),
                            )
                        )
                    text = getattr(part, "text", None)
                    if text:
                        yield TextChunk(text)
        except CallBudgetExceeded:
            raise
        except Exception as exc:  # noqa: BLE001 — reported by type name only
            self.ledger.add(usage, thinking_level=level, ok=False)
            raise GeminiError(type(exc).__name__) from None

        self.ledger.add(usage, thinking_level=level)
        yield UsageChunk(usage=usage, thinking_level=level, model=self.model)


def _contents(messages: Sequence[Message], types: Any) -> list[Any]:
    """The neutral conversation as ``types.Content``.

    A function response goes back under role ``user`` — the SDK's own automatic
    loop builds it that way, and the convention is the API's, not a preference.
    """
    contents: list[Any] = []
    for message in messages:
        if isinstance(message, UserMessage):
            contents.append(
                types.Content(role="user", parts=[types.Part.from_text(text=message.text)])
            )
        elif isinstance(message, ModelMessage):
            parts = []
            if message.text:
                parts.append(types.Part.from_text(text=message.text))
            parts += [
                types.Part(
                    function_call=types.FunctionCall(name=call.name, args=dict(call.args)),
                    # Required back verbatim by the 3.x models — see :class:`ModelCall`.
                    thought_signature=call.thought_signature,
                )
                for call in message.calls
            ]
            if parts:
                contents.append(types.Content(role="model", parts=parts))
        elif isinstance(message, ToolMessage):
            contents.append(
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_function_response(
                            name=message.name, response=dict(message.response)
                        )
                    ],
                )
            )
    return contents


def _parts(chunk: Any) -> list[Any]:
    candidates = getattr(chunk, "candidates", None) or []
    if not candidates:
        return []
    content = getattr(candidates[0], "content", None)
    return list(getattr(content, "parts", None) or [])


def _usage_of(chunk: Any) -> Usage | None:
    """The running usage a chunk reports. The last one wins — it is cumulative."""
    meta = getattr(chunk, "usage_metadata", None)
    if meta is None:
        return None

    def get(name: str) -> int:
        return int(getattr(meta, name, None) or 0)

    return Usage(
        prompt_tokens=get("prompt_token_count"),
        thoughts_tokens=get("thoughts_token_count"),
        output_tokens=get("candidates_token_count"),
        total_tokens=get("total_token_count"),
    )
