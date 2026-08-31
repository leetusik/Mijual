"""사이트 설정 — the deploy values a **reader-facing surface** renders.

``GET /site/contact`` → ``{"contact": …, "email": …, "phone": …}``

One route, and the reason it is not part of another surface's router: the
운영자 연락처 is site-wide config, not ask-specific. The AI 질문 agent already
hands the same string out through ``get_contact``, and the global footer now
publishes it on every page (`P11.F2`, at the operator's instruction at P11's
acceptance gate) — two consumers with nothing in common but the setting, which is
what makes this its own surface rather than a second read bolted onto ``/ask``.

**The frontend cannot see the setting any other way.** ``MIJUAL_OPERATOR_CONTACT``
lives in the gitignored repo-root ``.env`` that this service reads; the Next
process is started with only ``MIJUAL_DEV_ORIGINS`` in its environment and reads
its own ``frontend/.env``, which does not exist. Serving it keeps one source of
truth instead of asking the operator to set the same value twice.

Read-only and anonymous, like ``/board``: the value is published on every page of
the product by design, so there is nothing here a session could protect.
"""

from __future__ import annotations

from fastapi import APIRouter, Request

from mijual.web.site import contact_payload

router = APIRouter(tags=["site"])

CONTACT_PATH = "/site/contact"


@router.get(CONTACT_PATH, summary="운영자 연락처 — 배포 설정값, 그대로와 부분으로")
def contact(request: Request) -> dict[str, str | None]:
    """The operator's contact string, and the two parts the chrome types apart.

    ``contact`` is the operator's own words verbatim (the agent answers with the
    same string); ``email`` and ``phone`` are the parts the footer needs, because
    numerals are mono and prose is not. Splitting happens in
    :mod:`mijual.web.site`, once — the route only serializes it.

    Unset is a state, not an error: all three keys come back ``null`` with a 200,
    and the footer then renders no contact line at all.
    """
    return contact_payload(request.app.state.settings.operator_contact)
