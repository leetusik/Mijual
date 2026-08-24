"""AI 질문 위의 전송 계층 — the agent on the wire, and the turn in the log.

`P6.S3` built the turn as a **generator of typed events** precisely so that this
module could be thin: one SSE frame per event, one row per turn, and no decision
about *what the reader is told* anywhere in here. What the transport genuinely
owns is the four things a generator cannot own for itself.

**1. The connection, and what 중지 means over it.** R6's 중지 is not a request —
there is no stop endpoint and there is nothing to cancel server-side. The reader
aborts the fetch, the consumer stops pulling, and
:func:`~mijual.agent.loop.run_turn` is closed at its yield. Nothing is retracted,
because the stream has no retraction event (`P6.S3`): every sentence already on
the reader's screen was verified before it was sent, and it stays true after the
connection dies.

**2. The transaction.** One session for the whole turn, opened here and owned
here — deliberately **not** :data:`mijual.web.deps.WriteSession`. A dependency
with ``yield`` is torn down when the *handler* returns, which for a streaming
response is **before a single frame is written**; a turn holding that session
would be reading through a committed-and-closed one. So the session is opened
inside the body iterator, used by every tool call, and committed once at the end
by the response's background task — the one hook Starlette runs on **both** exits
(stream finished, and client disconnected).

**3. The row — from the terminal, and from what was actually sent.**
:class:`~mijual.agent.events.TurnEnd` carries :func:`record_turn`'s arguments
verbatim, so a turn that ends normally is stored from the terminal alone (note 20:
the log can never disagree with what the reader saw). A **disconnect produces no
terminal at all**, and the honest default this phase stated is that a broken turn
is exactly the turn 품질 점검 wants. So :class:`_Released` accumulates the released
prose *from the frames this module wrote to the wire* — the same strings, in the
same order, never re-read out of the prose — and it is used **only** when there is
no terminal. The terminal always wins where it exists.

**3b. The structured blocks — verbatim, and only from the frames.** R16 added
blocks the prose cannot carry (a 데이터 블록's rows and their 근거; a 계산 블록's
inputs, expression and result), and its storage contract is that the log keeps
them **as they were sent**, never paraphrased. :class:`_Released` therefore keeps
every *persistent* block keyed by its ``block_id`` — so a block replaced in place
is stored once, in the state the reader ended up looking at — and hands the frames
to :func:`record_turn`. The transient 진행 표시 line is not one of them and is
never stored.

**4. The ledger line.** ``TurnEnd.usage`` is rendered to the **server log** and
nowhere else: recording agent spend is prudent, and adding a row to R7's signed
정확도·비용 panel would be a design change (`P6` Finding 14).

**Rate limiting is here, and it says nothing.** R6-5 removed the quota (질문 수
무제한) and `security` §Rate Limits makes limiting an operations decision with
**zero UI copy**. :class:`TurnLimiter` therefore holds no identity, persists
nothing, and refuses with the ordinary error envelope and no Korean at all — see
its own docstring for what it does and does not protect.

**The boundary this module moves.** ``mijual.web`` now imports ``mijual.agent``,
and the service now makes a model call in a request path — through this one seam
and nowhere else. No OpenDART call happens in a request path, this layer still
speaks HTTP only in :mod:`mijual.web.vocky`, and ``mijual.web`` imports no model
SDK: all three are scanned (``tests/test_web_smoke.py``, ``tests/test_web_vocky.py``,
``tests/test_agent_tools.py``).
"""

from __future__ import annotations

import json
import logging
import re
import threading
import time
from collections import deque
from collections.abc import Iterator, Sequence
from typing import Any

from fastapi import Request
from sqlalchemy.orm import Session

from mijual.agent import HistoryTurn, ToolContext, run_turn
from mijual.agent.client import DEFAULT_MODEL, ModelClient, UsageLedger
from mijual.agent.events import (
    AgentEvent,
    CitationEvent,
    RefusalEvent,
    TextEvent,
    TurnEnd,
)
from mijual.web import clock
from mijual.web.auth import current_account
from mijual.web.conversationstore import (
    KIND_ANSWER,
    KIND_REFUSAL,
    record_turn,
    session_hash_or_new,
)
from mijual.web.deps import session_factory
from mijual.web.errors import ApiError

__all__ = [
    "ASK_PATH",
    "MAX_HISTORY_CHARS",
    "MAX_HISTORY_TURNS",
    "MAX_QUESTION_CHARS",
    "SESSION_EVENT",
    "SSE_HEADERS",
    "AskTurn",
    "TurnLimiter",
    "clean_history",
    "clean_question",
    "clean_scope",
    "sse_frame",
]

log = logging.getLogger(__name__)

#: The one route this module serves. Named so `P6.S5`'s client and the smoke can
#: agree on it without either of them owning the string.
ASK_PATH = "/ask"

#: The first frame's event name: the anonymous handle, handed back so the browser
#: can keep it in ``sessionStorage`` (R6-5/6 — **never** a cookie; the thread is
#: tab-scoped by design, and a cookie is exactly the identifier this schema refuses).
SESSION_EVENT = "session"

#: A question is a question, not a payload. Long enough for a paragraph of context.
MAX_QUESTION_CHARS = 2_000
#: The client holds the thread (sessionStorage), so history arrives on every turn.
#: The cap is defensive: the newest turns are kept and the rest are dropped rather
#: than refused, so a long-lived tab keeps working instead of failing at turn nine.
MAX_HISTORY_TURNS = 8
#: One earlier question or answer. R6's answers are short; this is a ceiling, not a size.
MAX_HISTORY_CHARS = 8_000

#: A 범위 handle is a filing number, and nothing else has that shape.
_RCEPT = re.compile(r"\A\d{14}\Z")

#: Headers that matter once a response is a *stream* rather than a body.
#:
#: ``Cache-Control: no-store`` — an answer is per-reader, per-corpus-moment and
#: never replayable; a cached SSE body would be a second reader's answer.
#: ``no-transform`` — **measured, not defensive** (`P6.S7`): the production
#: ``next start`` proxy gzips whatever it forwards, and a gzip encoder holds the
#: stream until it has a block to emit, so every frame of a turn arrived in one
#: burst at the end and R6's signed 스트리밍 state (도구 행 as the agent reads them,
#: 프로즈 자람, the caret) was never on the screen. ``no-transform`` is the
#: standard's own way to say *do not re-encode this payload* (RFC 9111 §5.2.2.6),
#: and `compression`'s ``shouldTransform`` — the middleware Next's router runs —
#: honours it, as do nginx and the CDNs P4 will meet.
#: ``X-Accel-Buffering: no`` — nginx (and several PaaS routers) buffer a proxied
#: response by default, which turns an incremental stream into one late blob.
#: The header is meaningless where no such proxy exists and free where one does,
#: and P4 owns the deployed topology (Open Question 4).
SSE_HEADERS = {
    "Cache-Control": "no-store, no-transform",
    "X-Accel-Buffering": "no",
}


def sse_frame(name: str, data: Any) -> str:
    """One SSE frame. ``ensure_ascii=False`` because the payload is Korean.

    ``json.dumps`` escapes every newline *inside* a string, so a frame is always
    exactly two lines plus the blank one that terminates it — a quote containing a
    line break cannot split a frame in half.
    """
    return f"event: {name}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


# ---------------------------------------------------------------------------
# request validation — before a single frame is written
# ---------------------------------------------------------------------------
def clean_question(raw: str | None) -> str:
    """The reader's question, or an :class:`ApiError` in the ordinary envelope.

    This runs **before** the response starts, which is the whole reason it is a
    separate step: once the stream is open the only honest way to fail is the
    typed ``error`` terminal, and a half-written frame is not a failure mode this
    contract has. No Korean is invented for either code — the design writes no
    HTTP-error copy (:mod:`mijual.web.errors`).
    """
    question = (raw or "").strip()
    if not question:
        raise ApiError("invalid_question", "a question is required")
    if len(question) > MAX_QUESTION_CHARS:
        raise ApiError(
            "invalid_question", f"a question is at most {MAX_QUESTION_CHARS} characters"
        )
    return question


def clean_scope(raw: str | None) -> str | None:
    """범위: a filing number or nothing. Junk is refused, never ignored.

    Silently dropping a malformed 범위 would answer a *different* question from
    the one the widget asked (전체 공시 instead of this event), and the reader
    would have no way to see that it happened.
    """
    scope = (raw or "").strip()
    if not scope:
        return None
    if not _RCEPT.match(scope):
        raise ApiError("invalid_scope", "scope_rcept_no is a 14-digit filing number")
    return scope


def clean_history(turns: Sequence[HistoryTurn]) -> tuple[HistoryTurn, ...]:
    """The newest :data:`MAX_HISTORY_TURNS` exchanges, each capped.

    History is *prose the client holds* (R6-5/6: the thread lives in
    sessionStorage), so the server treats it as untrusted context rather than as
    state: it is never stored, never cited, and never allowed to grow the prompt
    without bound. Citation numbering is per answer (R6-4), so nothing is lost by
    dropping the oldest turns.
    """
    kept = [turn for turn in turns if turn.question.strip()][-MAX_HISTORY_TURNS:]
    return tuple(
        HistoryTurn(
            question=turn.question[:MAX_HISTORY_CHARS],
            answer=turn.answer[:MAX_HISTORY_CHARS],
        )
        for turn in kept
    )


# ---------------------------------------------------------------------------
# rate limiting — an operations decision with zero UI copy
# ---------------------------------------------------------------------------
class TurnLimiter:
    """The cheapest honest limiter: in-process, identity-free, unpersisted.

    **What it protects, and what it cannot.** Two independent ceilings, because
    they fail differently:

    * ``max_concurrent`` — how many turns this process runs at once. This is the
      one that actually bounds money and latency, it holds **no key at all** (an
      integer), and it cannot be evaded, because minting a new handle does not
      buy a second slot.
    * ``per_session`` in ``window_s`` — how often one thread may ask. It bounds a
      runaway tab, and it is **trivially evaded** by sending a fresh handle every
      turn. That is stated rather than hidden: a handle is a thread grouping, not
      an identity, and pretending otherwise would be the first step toward
      storing one.

    **Why nothing here is keyed on an address.** R7 signs the anonymity promise at
    the *schema* level (계정·이메일·IP·UA 컬럼 없음), and `P6.S1` kept it from the
    other side by minting the handle at random. A per-IP counter would not violate
    the schema — it writes nothing — but it would put the forbidden identifier in
    the process anyway, on the strength of "it's only in memory". The counters
    below hold exactly what the log already holds, and hold it for
    ``window_s`` seconds.

    **Zero UI copy** (R6-5, `security` §Rate Limits): a refused turn is a plain
    ``429`` in the ordinary envelope with no ``message_ko``, and no surface says
    anything about limits — 질문 수 무제한 is the signed promise and a limit that
    is not shown must not be implied.

    **Per process only.** P4 owns cross-process state (it already parks login rate
    limiting there for the same reason); behind two workers each ceiling is
    per-worker, which is why the defaults are set as runaway guards rather than as
    a quota anyone could hit while reading.
    """

    def __init__(
        self,
        *,
        max_concurrent: int = 6,
        per_session: int = 30,
        window_s: float = 300.0,
        slot_ttl_s: float = 600.0,
        max_tracked: int = 4_096,
    ) -> None:
        self.max_concurrent = max_concurrent
        self.per_session = per_session
        self.window_s = window_s
        self.slot_ttl_s = slot_ttl_s
        self.max_tracked = max_tracked
        self._lock = threading.Lock()
        #: When each in-flight turn started. A *list* rather than a counter so a
        #: slot that is never released (a path that skips the response's
        #: background task) expires instead of wedging the endpoint forever — a
        #: guard that can permanently refuse every reader is worse than no guard.
        self._live: list[float] = []
        self._recent: dict[str, deque[float]] = {}

    def acquire(self, session_hash: str, *, now: float | None = None) -> None:
        """Take a slot, or raise the ordinary 429. Pair with :meth:`release`."""
        moment = time.monotonic() if now is None else now
        with self._lock:
            self._sweep(moment)
            if len(self._live) >= self.max_concurrent:
                raise ApiError(
                    "rate_limited", "too many turns are running", status_code=429
                )
            stamps = self._recent.setdefault(session_hash, deque())
            if len(stamps) >= self.per_session:
                raise ApiError(
                    "rate_limited", "this thread is asking too quickly", status_code=429
                )
            stamps.append(moment)
            self._live.append(moment)

    def release(self) -> None:
        """Give the slot back. *Which* timestamp goes is irrelevant — only the
        count is, and dropping the oldest is what makes a lost slot self-heal."""
        with self._lock:
            if self._live:
                self._live.pop(0)

    def _sweep(self, moment: float) -> None:
        """Forget everything older than the window — the memory *is* the retention."""
        self._live = [start for start in self._live if start > moment - self.slot_ttl_s]
        horizon = moment - self.window_s
        for handle, stamps in list(self._recent.items()):
            while stamps and stamps[0] <= horizon:
                stamps.popleft()
            if not stamps:
                del self._recent[handle]
        # A ceiling on the map itself, so a flood of one-shot handles cannot grow
        # it without bound between sweeps. Oldest first: ``dict`` keeps insertion
        # order, and a dropped entry costs its thread nothing but the counter.
        while len(self._recent) > self.max_tracked:
            self._recent.pop(next(iter(self._recent)))


# ---------------------------------------------------------------------------
# what the reader actually received
# ---------------------------------------------------------------------------
class _Released:
    """The turn as it went over the wire — the **fallback** row, never the first choice.

    Assembled from the frames :class:`AskTurn` **finished writing** (see
    :meth:`AskTurn.frames` for why that word is load-bearing), so it cannot
    disagree with what the reader saw:
    :class:`~mijual.agent.events.TextEvent` and
    :class:`~mijual.agent.events.RefusalEvent` are the released sentences in
    order (which is exactly ``CitationGate.released``), and
    :class:`~mijual.agent.events.CitationEvent` is a 근거 chip the moment it is
    defined (exactly ``CitationGate.chips``).

    Every property prefers the terminal when there is one, so a normal turn is
    stored from :class:`~mijual.agent.events.TurnEnd` **alone**, as note 20 fixed.
    The accumulation exists for the one case that has no terminal: the reader's
    중지, where the connection dies mid-turn and the partial answer is still the
    turn 품질 점검 most wants to read.
    """

    def __init__(self) -> None:
        self._parts: list[str] = []
        self._family: str | None = None
        self._evidence: list[str] = []
        self._quotes: list[str] = []
        self._blocks: dict[str, dict[str, Any]] = {}
        self.terminal: TurnEnd | None = None

    def absorb(self, event: object) -> None:
        if isinstance(event, TurnEnd):
            self.terminal = event
        elif isinstance(event, RefusalEvent):
            self._parts.append(event.text)
            self._family = self._family or event.family
        elif isinstance(event, TextEvent):
            self._parts.append(event.text)
        elif isinstance(event, CitationEvent):
            if event.rcept_no not in self._evidence:
                self._evidence.append(event.rcept_no)
            if event.quote is not None and event.quote not in self._quotes:
                self._quotes.append(event.quote)
        elif isinstance(event, AgentEvent) and event.persistent and event.block_id:
            # **Generic on purpose** (R16 §1): any persistent structured block —
            # a 데이터 블록 today, a 계산 블록 when `P9.S5` lands — is kept as the
            # exact frame that went to the reader, keyed by its ``block_id`` so a
            # ``pending`` → ``done`` replacement stores the block **once**, in its
            # final state, the same way the surface drew it. Nothing here knows
            # what kind of block it is, so no second storage change is needed for
            # the next kind.
            self._blocks[event.block_id] = event.frame()

    @property
    def answer(self) -> str:
        return self.terminal.answer if self.terminal else " ".join(self._parts)

    @property
    def refusal_category(self) -> str | None:
        return self.terminal.refusal_category if self.terminal else self._family

    @property
    def kind(self) -> str:
        if self.terminal is not None:
            return self.terminal.kind
        return KIND_REFUSAL if self._family else KIND_ANSWER

    @property
    def evidence(self) -> tuple[str, ...]:
        return self.terminal.evidence if self.terminal else tuple(self._evidence)

    @property
    def quotes(self) -> tuple[str, ...]:
        return self.terminal.quotes if self.terminal else tuple(self._quotes)

    @property
    def blocks(self) -> tuple[dict[str, Any], ...]:
        """구조화 블록 원형 — the frames themselves, in the order they arrived.

        R16 §7 / result.md §3-15: 「프로즈로 환언하지 않는다」. A calculation's audit
        path — its inputs, each input's 근거, the expression — does not exist in
        prose, so paraphrasing the block into the answer string *is* losing it.
        The frame is what the reader received, which makes the stored block and the
        rendered one the same object rather than two readings of one.

        Unlike the prose, this has no terminal to prefer: a block is only ever
        known from the frames that were written, so a 중지 mid-turn keeps the blocks
        the reader had already seen.
        """
        return tuple(self._blocks.values())

    @property
    def storable(self) -> bool:
        """A turn is logged when it ended, or when the reader saw something.

        A 중지 pressed before the first sentence leaves no 답변 to replay and no
        거절 to categorise; a row for it would be noise in a log whose whole
        purpose is 품질 점검. Every terminal is stored, ``aborted`` and ``error``
        included — those are the turns worth reading.
        """
        return self.terminal is not None or bool(self.answer) or bool(self._blocks)

    def end(self, *, status: str, reason: str | None, scope: str | None) -> TurnEnd:
        """A terminal for a failure the *transport* hit, in the stream's own shape."""
        return TurnEnd(
            status=status,
            kind=self.kind,
            answer=self.answer,
            refusal_category=self.refusal_category,
            scope_rcept_no=scope,
            evidence=self.evidence,
            quotes=self.quotes,
            reason=reason,
        )


# ---------------------------------------------------------------------------
# one turn, end to end
# ---------------------------------------------------------------------------
class AskTurn:
    """One question's whole server side: the stream, the transaction, the row.

    Constructed by the router **after** validation, so nothing here fails with a
    body — by the time :meth:`frames` runs, the response has already started.
    :meth:`close` is the response's background task and runs on both exits.
    """

    def __init__(
        self,
        request: Request,
        *,
        question: str,
        session_hash: str,
        scope_rcept_no: str | None = None,
        history: Sequence[HistoryTurn] = (),
    ) -> None:
        self._state = request.app.state
        self._request = request
        self.question = question
        self.session_hash = session_hash
        self.scope_rcept_no = scope_rcept_no
        self.history = tuple(history)
        self._released = _Released()
        self._session: Session | None = None
        self._holds_slot = False

    # -- the wire ---------------------------------------------------------
    def frames(self) -> Iterator[str]:
        """The SSE body. Runs in a worker thread — everything in it is sync.

        **An event is absorbed *after* its frame is yielded, never before**, and
        that ordering is the whole fidelity argument for the disconnect row. Being
        resumed past a ``yield`` is proof the consumer took the previous frame and
        wrote it out; absorbing before the yield would count a sentence the reader
        never received — measured, 2026-08-22: a turn cut mid-answer stored one
        sentence more than ``curl`` had been sent.
        """
        yield sse_frame(SESSION_EVENT, self.session_payload())
        try:
            for event in self._run():
                frame = event.frame()
                yield sse_frame(frame["event"], frame["data"])
                self._released.absorb(event)
        except Exception as exc:  # noqa: BLE001 — type name only, never a message
            # The stream is already open, so this is the one honest ending left:
            # the typed terminal the surface already knows how to render (부분 답변
            # 유지 + 재시도). An exception string is where a URL with a credential
            # tends to surface, so only the class name travels.
            log.exception("the agent turn failed mid-stream")
            end = self._released.end(
                status="error", reason=type(exc).__name__, scope=self.scope_rcept_no
            )
            # Absorbed *before* the yield, and that is the one deliberate exception
            # to the rule above: this terminal reports something that happened on
            # the server, so it is true whether or not the frame lands. It adds no
            # prose — it restates what was already released.
            self._released.absorb(end)
            yield sse_frame(end.event, end.payload())

    def session_payload(self) -> dict[str, Any]:
        """The first frame: the handle the browser keeps for this tab's thread."""
        payload: dict[str, Any] = {"session_hash": self.session_hash}
        if self.scope_rcept_no is not None:
            payload["scope"] = self.scope_rcept_no
        return payload

    def _run(self) -> Iterator[Any]:
        session = self._session = session_factory(self._state)()
        ctx = ToolContext(
            session=session,
            today=clock.now().date(),
            session_hash=self.session_hash,
            # R6: 「계정 로그인 여부와 무관하게 동일 동작」 — the account changes
            # only *whose* portfolio ``get_portfolio`` reads. It is resolved on
            # this turn's own session so the row stays attached for the whole turn.
            account=current_account(session, self._request),
            scope_rcept_no=self.scope_rcept_no,
            settings=self._state.settings,
        )
        return run_turn(ctx, self.question, self.history, client=self._client())

    def _client(self) -> ModelClient | None:
        """The turn's model, or ``None`` for :func:`run_turn`'s own live default.

        ``app.state.agent_client`` is a **factory** (see
        :func:`mijual.web.app.create_app`): the budget and the ledger are per turn,
        so a shared client would ration the second reader with the first reader's
        spend. A test and the SSE smoke pass a scripted one, which is why neither
        needs ``GEMINI_API_KEY`` — and why the suite spends nothing.
        """
        factory = getattr(self._state, "agent_client", None)
        return factory() if factory is not None else None

    # -- the exit both paths take -----------------------------------------
    def hold(self, limiter: TurnLimiter) -> None:
        """Take this turn's limiter slot. Released by :meth:`close`, always."""
        limiter.acquire(self.session_hash)
        self._holds_slot = True

    def close(self) -> None:
        """Log the ▷ line, store the turn, end the transaction, free the slot.

        Starlette runs this after the body iterator is done **and** after a client
        disconnect, which is what makes it the only place per-turn persistence can
        live: the body iterator's own ``finally`` runs on generator finalization,
        and finalization of a stream nobody is pulling is a garbage-collection
        event, not a control-flow one.
        """
        try:
            self._log_ledger()
            self._persist()
        finally:
            session, self._session = self._session, None
            if session is not None:
                session.close()
            if self._holds_slot:
                self._holds_slot = False
                limiter = getattr(self._state, "ask_limiter", None)
                if limiter is not None:
                    limiter.release()

    def _persist(self) -> None:
        """One row per turn — answer *or* refusal, with its 근거 and its 인용.

        The transport owns the transaction: ``record_turn`` and the tools'
        ``save_feedback`` both flush and neither commits, so this single commit is
        what makes either of them real. A failure rolls the **whole** turn back
        rather than half of it — a feedback row whose 원 대화 링크 points at a turn
        that was never written is worse in the 대기열 than no row at all — and it
        never touches the stream, which by now is over.
        """
        session = self._session
        if session is None:
            return
        record = self._released
        try:
            if record.storable:
                record_turn(
                    session,
                    session_hash=self.session_hash,
                    question=self.question,
                    kind=record.kind,
                    answer=record.answer,
                    scope_rcept_no=self.scope_rcept_no,
                    refusal_category=record.refusal_category,
                    evidence=record.evidence,
                    quotes=record.quotes,
                    blocks=record.blocks,
                )
            session.commit()
        except Exception:  # noqa: BLE001 — a log write must not raise at the exit
            log.exception("the turn could not be recorded; nothing from it is kept")
            session.rollback()

    def _log_ledger(self) -> None:
        """The ▷ line, server-side only (`P6` Finding 14: no ops panel gains a row)."""
        end = self._released.terminal
        usage: dict[str, Any] = dict(end.usage) if end is not None else {}

        def count(name: str) -> int:
            return int(usage.get(name) or 0)

        ledger = UsageLedger(
            model=str(usage.get("model") or DEFAULT_MODEL),
            calls=count("calls"),
            failures=count("failures"),
            prompt_tokens=count("prompt_tokens"),
            thoughts_tokens=count("thoughts_tokens"),
            output_tokens=count("output_tokens"),
            total_tokens=count("total_tokens"),
            levels=[str(level) for level in usage.get("thinking_levels") or ()],
        )
        log.info(
            "agent turn %s · %s · rounds %d · tools %d · blocked %d · %s",
            end.status if end is not None else "disconnected",
            end.kind if end is not None else self._released.kind,
            end.rounds if end is not None else 0,
            end.tool_calls if end is not None else 0,
            end.blocked if end is not None else 0,
            ledger.render(),
        )


def start_turn(
    request: Request,
    *,
    question: str | None,
    scope_rcept_no: str | None = None,
    session: str | None = None,
    history: Sequence[HistoryTurn] = (),
) -> AskTurn:
    """Validate, mint the handle, take a slot — everything that may still fail.

    Called by the router before it builds the response, so every refusal here is
    the ordinary error envelope rather than a stream that dies at frame one.
    """
    turn = AskTurn(
        request,
        question=clean_question(question),
        # A missing or malformed client token is **replaced, not trusted**
        # (`P6.S1`): it is what keeps an address out of the column, and it costs
        # the reader nothing but the thread grouping.
        session_hash=session_hash_or_new(session),
        scope_rcept_no=clean_scope(scope_rcept_no),
        history=clean_history(history),
    )
    limiter = getattr(request.app.state, "ask_limiter", None)
    if limiter is not None:
        turn.hold(limiter)
    return turn
