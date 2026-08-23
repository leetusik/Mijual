"""의견 보내기 — one write-only route that forwards a reader's message to vocky.

``POST /feedback`` → ``202 {"request_id": …, "accepted_at": …}``

R8 designed the 의견 screen as **미주알's own** ("vocky는 임베드 위젯을 제공하지
않으므로 화면은 우리 것이다"), so the browser talks only to this service and the
``vk_`` credential never leaves the server. The forward itself lives in
:mod:`mijual.web.vocky`, which is the one module in ``mijual.web`` allowed to
speak HTTP (scanned by ``tests/test_web_vocky.py``).

**This route stores nothing.** It writes no row, and specifically not the AI 질문
agent's ``save_feedback`` queue (``/ops/feedback``): R8's handoff left the two
paths separate — one is a human writing to the operator's feedback service, the
other is the agent recording what a conversation produced — and merging them would
put an unreviewed human message into an agent-recorded log. A later phase may
decide the ops panel should *see* vocky's captures; that is what the observation
tab already does, from the other side.

**The four outcomes are the surface's four outcomes** (build-prompt §6):

============================  ============================================
``202``                       접수됨 — the body carries vocky's own
                              ``request_id``, which the screen shows as
                              「접수 번호」. Nothing is minted here.
``400 feedback_empty``        an empty message. The screen already refuses
                              to send one (보내기 disabled), so this is the
                              server saying the same thing rather than
                              trusting the client.
``502 feedback_rejected``     vocky refused it — the credential or the body.
                              ``retryable: false``: 「키 문제는 독자가 해결
                              못 한다」, so the screen shows 실패 **without**
                              「다시 시도」.
``503 feedback_unavailable``  vocky did not answer (timeout, network, 5xx).
                              ``retryable: true`` — 실패 + 다시 시도.
============================  ============================================

An unconfigured deployment (no base URL / no key) answers ``503
feedback_unconfigured`` with ``retryable: false``, because retrying cannot
configure it — it is an operator's job, and one warning line says so in the log.

**Nothing logs the message or the key.** A failure logs its state, the upstream
status and the exception's *name*; the reader's own words exist only in vocky.
"""

from __future__ import annotations

import logging
from typing import Annotated, Literal

from fastapi import APIRouter, Body, Request
from pydantic import BaseModel, Field

from mijual.web import vocky
from mijual.web.errors import ApiError

router = APIRouter(tags=["feedback"])

log = logging.getLogger(__name__)

#: A ceiling on the body, not a rule the reader is told about: the signed surface
#: writes no length copy, so the textarea simply stops accepting characters at the
#: same number. Generous enough that no real 의견 meets it.
MAX_MESSAGE_CHARS = 4000

#: vocky's own enumeration for this field, narrowed to the two the surface can
#: produce: the footer entry is ``web``, the mobile sheet row is ``mobile``.
Channel = Literal["web", "mobile"]


class FeedbackIn(BaseModel):
    message: str = Field(max_length=MAX_MESSAGE_CHARS)
    #: Which entry point opened the surface (build-prompt §6: "`channel`은 시트에서
    #: 열렸으면 `"mobile"`, 푸터에서 열렸으면 `"web"`").
    channel: Channel = "web"
    #: The anonymous AI 질문 tab handle, **if the browser already had one**. No
    #: identifier is minted for a 의견 and none is stored here.
    session_id: str | None = Field(default=None, max_length=64)


@router.post("/feedback", status_code=202, summary="의견 보내기 — vocky로 전달")
def send_feedback(request: Request, body: Annotated[FeedbackIn, Body()]) -> dict[str, str]:
    message = body.message.strip()
    if not message:
        raise ApiError("feedback_empty", "message must not be blank", status_code=400)

    receipt = vocky.submit(
        request.app.state.settings,
        message=message,
        channel=body.channel,
        session_id=(body.session_id or None),
    )
    if receipt.accepted:
        answer = {"request_id": receipt.request_id or ""}
        if receipt.accepted_at:
            answer["accepted_at"] = receipt.accepted_at
        return answer

    # One line, no key and no message text — the state, the upstream status and
    # the exception's name are what an operator needs to fix it.
    log.warning(
        "의견 forward not accepted: state=%s status=%s reason=%s",
        receipt.state,
        receipt.status,
        receipt.reason,
    )
    if receipt.state == "unconfigured":
        raise ApiError(
            "feedback_unconfigured",
            "MIJUAL_VOCKY_API_BASE / MIJUAL_VOCKY_API_KEY are not both set",
            status_code=503,
            retryable=False,
        )
    if receipt.state == "rejected":
        raise ApiError(
            "feedback_rejected",
            "the feedback service refused this request",
            status_code=502,
            retryable=False,
        )
    raise ApiError(
        "feedback_unavailable",
        "the feedback service did not answer",
        status_code=503,
        retryable=True,
    )
