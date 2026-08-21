"""내 포트폴리오 — 보유 종목, D-day 목록, 챙긴 돈, 알림 설정, 샘플.

The transport half of :mod:`mijual.web.portfolio`, which holds the decisions.
The route map, so ``P5.S16`` and ``P5.S10``'s client can hard-code it:

=====================================  =========================================
``GET    /portfolio``                  the home: holdings + 다가오는/지나간 마감
``POST   /portfolio/holdings``         담기 — ``{corp_code, shares}`` (201)
``PATCH  /portfolio/holdings/{id}``    보유량 수정 (inline row edit)
``DELETE /portfolio/holdings/{id}``    삭제, 즉시 (the 되돌리기 is the client's)
``PUT    /portfolio/claims/{rcept_no}``    챙긴 돈 체크   (R5-8)
``DELETE /portfolio/claims/{rcept_no}``    챙긴 돈 해제
``GET    /portfolio/notifications``    수신 주소 + 시점 칩
``PUT    /portfolio/notifications``    시점 칩 저장
``GET    /portfolio/sample``           the R5-4 sample — **anonymous**
=====================================  =========================================

**Everything but the sample needs the owner**, and the sample needs nobody: it is
the product's front door for a reader with no account (로그인 페이지 하단 + 랜딩
푸터, 원클릭, 가입 없음), so it takes no cookie, writes nothing and carries no
account fact at all — no address, no 알림 설정, no 챙긴 돈 state. R5: "가짜
이메일·알림 이력 렌더 금지; 샘플에서 알림 설정 숨김".

**No holding count leaves this service as a product.** Like ``P5.S4``, every ①
row carries the *factors* (배정비율 · 증서 1주 이론가치 + 하한 · 초과청약 비율) and
the browser multiplies — the row states its ``shares`` because the server stored
that count, never because it multiplied by it.

**Every mutation carries the CSRF header** (:mod:`mijual.web.csrf`, service-wide)
and takes the committing session, which a safe method cannot acquire. Failures
travel as structural codes with no Korean: R5's signed copy is the client's.
"""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Body, Path
from pydantic import BaseModel, Field

from mijual.web import clock, portfolio
from mijual.web.auth import ReadAccount, WriteAccount
from mijual.web.deps import DbSession, WriteSession
from mijual.web.reads import load_portfolio, stock_by_code

router = APIRouter(tags=["portfolio"])


class HoldingIn(BaseModel):
    """담기. The issuer is a ``corp_code`` — ``GET /stocks?q=`` resolves the text."""

    corp_code: str = Field(max_length=8)
    #: Range-checked in the service layer so an out-of-range count comes back as
    #: ``invalid_shares`` in the ordinary envelope rather than as a 422 with
    #: English field detail — it is a normal product state, not a client bug.
    shares: int


class SharesIn(BaseModel):
    shares: int


class LeadDaysIn(BaseModel):
    """시점 칩. ``[]`` is a valid selection and means no mail (R5's off switch)."""

    lead_days: list[int]


@router.get("/portfolio", summary="내 포트폴리오 홈 — 보유 종목 + D-day 목록")
def home(db: DbSession, account: ReadAccount) -> dict[str, Any]:
    """The owner's whole home surface in one read.

    The 챙긴 돈 marks are loaded with it so a past ① row arrives already labelled;
    a second request for them would let the two render out of step.
    """
    return load_portfolio(
        db,
        portfolio.entries_of(db, account),
        today=clock.now().date(),
        claims=portfolio.claimed_reports(db, account),
    )


@router.get("/portfolio/sample", summary="샘플 포트폴리오 (익명, 읽기 전용)")
def sample(db: DbSession) -> dict[str, Any]:
    """The fixed R5-4 composition, resolved live through the same composition.

    Four real filings, four real states, and the 보유량 stated on the card as an
    example — so every number here is the corpus's, and only the portfolio itself
    is illustrative. ``sample: true`` is the flag the banner, the nav 「샘플」 chip
    and the 샘플 종료 control key on; ``claims`` is ``None``, so no row carries a
    ``claimed`` key and no account fact appears anywhere in the payload.
    """
    payload = load_portfolio(
        db, portfolio.sample_entries(), today=clock.now().date(), claims=None
    )
    payload["sample"] = True
    return payload


@router.post("/portfolio/holdings", status_code=201, summary="종목 담기")
def add(
    db: WriteSession, account: WriteAccount, body: Annotated[HoldingIn, Body()]
) -> dict[str, Any]:
    row = portfolio.add_holding(
        db, account, corp_code=body.corp_code, shares=body.shares
    )
    return {"holding": portfolio.holding_payload(row, stock_by_code(db, row.corp_code))}


@router.patch("/portfolio/holdings/{holding_id}", summary="보유량 수정")
def update(
    db: WriteSession,
    account: WriteAccount,
    holding_id: int,
    body: Annotated[SharesIn, Body()],
) -> dict[str, Any]:
    row = portfolio.update_holding(db, account, holding_id, shares=body.shares)
    return {"holding": portfolio.holding_payload(row, stock_by_code(db, row.corp_code))}


@router.delete("/portfolio/holdings/{holding_id}", summary="삭제 (즉시)")
def remove(db: WriteSession, account: WriteAccount, holding_id: int) -> dict[str, Any]:
    portfolio.delete_holding(db, account, holding_id)
    return {"deleted": True}


#: A 실적보고서 filing number: 14 digits, and the key a 챙긴 돈 mark is stored under.
_RCEPT = Path(min_length=14, max_length=14, pattern=r"^\d{14}$")


@router.put("/portfolio/claims/{rcept_no}", summary="챙긴 돈 체크 (본인 표시)")
def claim(
    db: WriteSession, account: WriteAccount, rcept_no: Annotated[str, _RCEPT]
) -> dict[str, Any]:
    """"청약·매도로 챙겼습니다" — the reader's own claim, on their own row.

    It re-labels one row and changes no figure: the amount stays the same
    「추정」 number the 소멸 계산 produced, and this mark reaches no total, no
    statistic and no other reader (R5-8: 공시 데이터와 혼동 금지).
    """
    portfolio.set_claim(db, account, rcept_no, claimed=True)
    return {"rcept_no": rcept_no, "claimed": True}


@router.delete("/portfolio/claims/{rcept_no}", summary="챙긴 돈 해제")
def unclaim(
    db: WriteSession, account: WriteAccount, rcept_no: Annotated[str, _RCEPT]
) -> dict[str, Any]:
    portfolio.set_claim(db, account, rcept_no, claimed=False)
    return {"rcept_no": rcept_no, "claimed": False}


@router.get("/portfolio/notifications", summary="알림 설정 — 수신 주소 + 시점 칩")
def notifications(db: DbSession, account: ReadAccount) -> dict[str, Any]:
    """The settings a reader has, defaults included — and **no sending happens
    anywhere in P5**: the D-day mail channel (provider, schedule, body) is P4's.
    """
    return portfolio.notifications_payload(account, portfolio.lead_days_of(db, account))


@router.put("/portfolio/notifications", summary="시점 칩 저장")
def save_notifications(
    db: WriteSession, account: WriteAccount, body: Annotated[LeadDaysIn, Body()]
) -> dict[str, Any]:
    days = portfolio.set_lead_days(db, account, body.lead_days)
    return portfolio.notifications_payload(account, days)
