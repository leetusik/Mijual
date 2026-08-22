"""내 종목 조회 — one stock's live rights and its 2026 놓친 돈.

``GET /stocks?q=<종목명|종목코드>``
    The search box. Resolves the query server-side against the corpus's issuers
    and, on a hit, returns that stock's whole page in the same response — the
    surface has nothing to draw before it knows which company it is about, so a
    second round trip would only delay it.

``GET /stocks/suggest?q=<text>``
    Candidates for a **half-typed** query — what the reader may mean, each with
    its ``corp_code`` and 종목코드, at most eight, ``200`` with an empty list when
    nothing matches. Read-only and free of the resolver: it never opens a page,
    it only offers ones to open.

``GET /stocks/{corp_code}``
    The same page by stable handle, for R3's "내 보유량으로 환산 →" link-out,
    which travels from an event that already knows its ``corp_code`` — and, since
    `P7.S4`, for a candidate a reader **chose** out of the suggestion list.

**A miss is a result, not an error.** An unresolvable query comes back ``200``
with ``{"query": …, "found": false}`` and nothing else: R4 renders its own locked
검색 불일치 sentence on the same page, and a 404 envelope would carry an English
``code`` the surface would have to translate anyway. It says only that nothing
matched — never *why* and never how close a near-miss was, because a guess that
opened a different company's 놓친 돈 is the one defect class this product cannot
ship. **The resolver still never guesses; suggestions are the reader's own
choice.** `P7.S4` (operator item 2) reads that rule as being about the *system*
silently picking, so a candidate list exists — on its own route, before the
submit, never in this response — and a chosen candidate travels as the exact
handle ``/stocks/{corp_code}``, never back through ``?q=``. Submitting without
choosing behaves exactly as it always did, ambiguous prefixes included. An unknown
``corp_code`` on the handle route **is** a 404: that is a link to a resource that
does not exist, not a search that found nothing.

**No holding count is ever received here.** These endpoints serve **factors, not
products** — 배정비율 to its ten decimals, 증서 1주 이론가치 and its floor, the
초과청약 비율 — and the browser multiplies. R4 keeps the 보유 주식 수 in
``sessionStorage`` and states so on the page ("브라우저 세션에만 저장 · 서버 전송
없음"); an endpoint that accepted an ``n`` would make that sentence false, so
there is no parameter for one and no per-holding number in any payload. The
suggestion route keeps that promise the short way: its only parameter is ``q``.

No route here touches OpenDART or a model, none writes, and none re-derives a
figure: every number comes from :mod:`mijual.present` over persisted rows.
"""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Query

from mijual.web import clock
from mijual.web.deps import DbSession
from mijual.web.errors import NotFound
from mijual.web.reads import load_stock, resolve_corp, stock_by_code, suggest_corps

router = APIRouter(tags=["stocks"])


@router.get("/stocks", summary="Resolve a 종목명/종목코드 and serve that stock's page")
def stocks(
    db: DbSession,
    q: Annotated[str, Query(min_length=1, description="종목명 또는 종목코드")],
) -> dict[str, Any]:
    corp = resolve_corp(db, q)
    if corp is None:
        return {"query": q, "found": False}
    return {"query": q, "found": True, **load_stock(db, corp, today=clock.now().date())}


@router.get("/stocks/suggest", summary="입력 중인 종목명/종목코드의 후보 목록")
def stocks_suggest(
    db: DbSession,
    q: Annotated[str, Query(min_length=1, description="입력 중인 종목명 또는 종목코드")],
) -> dict[str, Any]:
    """Candidates for a query still being typed — a **choice**, not a resolution.

    **Declared before ``/stocks/{corp_code}`` on purpose.** FastAPI matches routes
    in declaration order, so the handle route would otherwise swallow ``suggest``
    as a ``corp_code`` and answer 404.

    Nothing matching is a ``200`` with an empty list, never a 404 and never an
    error: "no candidates yet" is the normal state of a box someone is still
    typing into. The payload carries only what the listbox renders and what the
    click needs — 회사명, 종목코드 and the ``corp_code`` the surface navigates by.
    """
    return {
        "query": q,
        "candidates": [
            {
                "corp_code": corp.corp_code,
                "corp_name": corp.corp_name,
                "stock_code": corp.stock_code,
            }
            for corp in suggest_corps(db, q)
        ],
    }


@router.get("/stocks/{corp_code}", summary="One stock's live rights and its 2026 놓친 돈")
def stock(db: DbSession, corp_code: str) -> dict[str, Any]:
    corp = stock_by_code(db, corp_code)
    if corp is None:
        raise NotFound("stock")
    return load_stock(db, corp, today=clock.now().date())
