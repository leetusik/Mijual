"""AI 질문 — one turn, one stream, and the start screen's own small read.

``POST /ask`` → ``text/event-stream``

Request body (every field but ``question`` optional)::

    {"question": "계양전기 증서 언제까지예요?",
     "scope_rcept_no": "20260724000546",      # 범위: the event the widget opened on
     "session": "0f3a…",                      # this tab's anonymous handle
     "history": [{"question": "…", "answer": "…"}]}   # oldest first, client-held

The frames, in order:

``event: session``
    ``{"session_hash": "…", "scope"?: "…"}`` — **always first**, so the browser can
    put the handle in ``sessionStorage`` before a single sentence arrives (R6-5/6:
    sessionStorage, never localStorage, and **never a cookie** — the thread is
    tab-scoped by design and a cookie would be the identifier the schema refuses).
``event: tool_row`` · ``citation`` · ``text`` · ``refusal`` · ``links`` · ``footer``
    :mod:`mijual.agent.events`, serialized by their own ``frame()``. The transport
    invents no field and reorders nothing: a ``citation`` is *defined* immediately
    before the ``text`` that names its number, which is what lets the chip be
    painted with its sentence (R6: 자리표시 칩·후행 부착 금지).
``event: done`` | ``aborted`` | ``error``
    The terminal, exactly once. ``aborted``/``error`` keep the partial answer above
    them — the stream has no retraction event, and 푸터/links arrive only on ``done``.

**중지 has no endpoint.** The reader aborts the fetch; the consumer stops pulling;
the turn's generator is closed. There is nothing to cancel server-side and nothing
to retract client-side, and the partial turn is still stored — see
:mod:`mijual.web.ask`.

**The CSRF header is required**, like every other unsafe method this service serves
(:mod:`mijual.web.csrf`, service-wide). A headerless ``POST`` never reaches this
module.

``GET /ask/start-cards``
    The companies the start screen's two 공시 cards name, resolved from the corpus
    **per request** (`P11.F1`). It is a plain JSON read beside the stream because
    the operator rejected fixed ones at P11's gate: a card whose company has aged
    out is a dead question on the first screen a reader meets. No Korean travels
    in it — the sentences are templates in ``components/ask/copy.ts``.

**The streaming route is where the architecture boundary moved.** It is the only
place a request path reaches a model, and it does so through :mod:`mijual.agent`
alone.
No OpenDART call happens in any request path, and ``mijual.web`` imports no model
SDK — both are still scanned.
"""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Body, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from starlette.background import BackgroundTask

from mijual.agent import HistoryTurn
from mijual.web import clock
from mijual.web.ask import (
    ASK_PATH,
    MAX_HISTORY_CHARS,
    MAX_QUESTION_CHARS,
    SSE_HEADERS,
    start_turn,
)
from mijual.web.deps import DbSession
from mijual.web.reads import load_start_cards

router = APIRouter(tags=["ask"])


class HistoryIn(BaseModel):
    """One earlier exchange, as **prose**. Chip numbering is per answer (R6-4)."""

    question: str = Field(max_length=MAX_HISTORY_CHARS)
    answer: str = Field(default="", max_length=MAX_HISTORY_CHARS)


class AskIn(BaseModel):
    #: Length is checked twice on purpose: here so an absurd body is refused before
    #: it is parsed into a turn, and in ``clean_question`` so the *stripped* text is
    #: what the limit applies to.
    question: str = Field(max_length=MAX_QUESTION_CHARS)
    scope_rcept_no: str | None = Field(default=None, max_length=14)
    #: The handle this tab was given by an earlier turn's ``session`` frame. A
    #: missing or malformed one is replaced rather than trusted (`P6.S1`).
    session: str | None = Field(default=None, max_length=64)
    history: list[HistoryIn] = Field(default_factory=list)


@router.post(ASK_PATH, summary="AI 질문 — 한 번의 대화 턴을 SSE로")
def ask(request: Request, body: Annotated[AskIn, Body()]) -> StreamingResponse:
    """Run one turn and stream it.

    Everything that can be refused is refused *before* the response starts, so a
    caller sees either the ordinary error envelope or a stream that ends in a
    typed terminal — never a half-written frame.

    The background task is not an afterthought: it is the only hook Starlette runs
    on **both** exits (the stream finished, and the client disconnected), so it is
    where this turn's row, its commit and its limiter slot live.
    """
    turn = start_turn(
        request,
        question=body.question,
        scope_rcept_no=body.scope_rcept_no,
        session=body.session,
        history=[HistoryTurn(item.question, item.answer) for item in body.history],
    )
    return StreamingResponse(
        turn.frames(),
        media_type="text/event-stream",
        headers=SSE_HEADERS,
        background=BackgroundTask(turn.close),
    )


#: The start screen's own read. Under ``/ask`` because it belongs to this
#: surface and to nothing else — the board's cards come from ``/board``.
START_CARDS_PATH = f"{ASK_PATH}/start-cards"


@router.get(START_CARDS_PATH, summary="시작 화면 질문 카드가 이름 붙일 회사 — 코퍼스에서, 요청마다")
def start_cards(db: DbSession) -> dict[str, Any]:
    """Which companies the `/ask` start cards name **on this request**.

    P11's acceptance gate rejected fixed ones: a card naming a company whose
    filing has aged out of the corpus is a dead question on the first screen a
    reader meets, and the operator asked for 「real time catch. not fixed.」 So the
    two company-bearing cards are resolved here, per render, from the same board
    reading every other surface uses (:func:`mijual.web.reads.load_start_cards`).

    **No Korean travels in this payload.** The sentences stay templates with a
    company slot in ``components/ask/copy.ts`` — the frontend's one Korean-string
    rule is not bent to make a card served — and a slot with no candidate comes
    back ``null``, which the surface renders from its static fallback rather than
    as a missing card. Read-only and anonymous, like ``/board``.

    Its reference day comes from the same clock the board reports, so a card and
    a D-day drawn on one screen cannot straddle midnight KST.
    """
    return load_start_cards(db, today=clock.now().date())
