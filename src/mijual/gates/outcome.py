"""The verdict vocabulary of §3.6 layer 2 — four states and a reason code.

A gate is a **list of named checks** over one extracted field, and its verdict is
derived from them rather than written by hand:

``passed``
    at least one substantive check ran and none failed. The field may be shown.
``failed``
    a check failed. The field is **recorded with its reason code and never
    shown** — the phase's blunt invariant, and the product's trust claim.
``tbd``
    the document says the schedule is suspended (``추후결정``): a *verified*
    citation with null dates (N40). Shown as ``추후결정`` — never as the
    superseded date it replaced.
``not_evaluable``
    nothing could be checked (the field is absent, the call errored, or the
    gate's reference value does not exist). Conservative default: **not shown**.
    ``not_evaluable`` is honest about *why* nothing was shown, which a bare
    ``failed`` would not be.

A skipped check is not a failure and not a pass — it is recorded as skipped and
kept in the note, so "the gate ran but could not compare against 본문 6" and "the
gate compared and agreed" never look the same afterwards.
"""

from __future__ import annotations

from dataclasses import dataclass, field

__all__ = [
    "Check",
    "FAILED",
    "NOT_EVALUABLE",
    "Outcome",
    "PASSED",
    "REASON_LABELS_KO",
    "TBD",
    "check_failed",
    "check_passed",
    "check_skipped",
    "not_evaluable",
    "tbd",
    "verdict",
]

PASSED = "passed"
FAILED = "failed"
TBD = "tbd"
NOT_EVALUABLE = "not_evaluable"

#: Statuses whose field the product may render. ``tbd`` renders as ``추후결정``.
EXPOSABLE_STATUSES = frozenset({PASSED, TBD})

#: Korean rendering for every reason code this layer can emit. P3 shows these;
#: the code itself is the stable identifier. Keeping the map here means a new
#: reason code cannot reach the product without a human-readable sentence.
REASON_LABELS_KO: dict[str, str] = {
    # --- citation (every field) ---------------------------------------
    "span_unresolved": "인용 구절을 원문에서 찾지 못했습니다",
    "span_missing": "인용 구절이 없습니다",
    "field_absent": "해당 항목이 공시 본문에 없습니다",
    "extraction_error": "추출이 실패한 항목입니다",
    "no_value": "값이 비어 있습니다",
    # --- ① 1 신주인수권증서 매매기간 ------------------------------------
    "schedule_tbd": "일정이 추후결정 상태입니다",
    "dates_missing": "기간이 기재되어 있지 않습니다",
    "date_order": "시작일이 종료일보다 늦습니다",
    "not_after_record_date": "매매기간이 신주배정기준일보다 앞섭니다",
    "not_before_subscription": "매매기간이 청약일보다 늦게 끝납니다",
    # --- ① 2 청약 취급처 -----------------------------------------------
    "no_entries": "청약 취급처 항목이 비어 있습니다",
    "subscription_date_mismatch": "청약일이 본문 11. 청약예정일과 다릅니다",
    "public_offer_not_after": "일반공모 청약일이 구주주 청약일보다 앞섭니다",
    # --- ① 3 실권주 처리 ------------------------------------------------
    "method_not_enumerated": "실권주 처리 방식이 정해진 유형에 없습니다",
    # --- ① 4 초과청약 ---------------------------------------------------
    "ratio_out_of_range": "초과청약 비율이 0 초과 1 이하가 아닙니다",
    "ratio_quote_mismatch": "초과청약 비율이 인용 구절의 값과 다릅니다",
    # --- ① 5 발행가액 산정방법 -------------------------------------------
    "formula_missing": "확정 발행가액 산식이 없습니다",
    "discount_rate_out_of_range": "할인율이 0 초과 1 미만이 아닙니다",
    "final_price_date_out_of_window": "확정 발행가액 공시일이 본문 6.과 청약일 사이에 있지 않습니다",
    # --- ② 6·7·8 (P2.S7의 코퍼스) ----------------------------------------
    "floor_price_mismatch": "조정 최저가액이 API 값과 다릅니다",
    "floor_ratio_out_of_range": "최저 조정 비율이 0 초과 1 이하가 아닙니다",
    "option_date_order": "옵션 행사 시작일이 종료일보다 늦습니다",
    "option_date_out_of_term": "옵션 행사기간이 사채 발행일~만기일을 벗어납니다",
    "no_options": "옵션 항목이 비어 있습니다",
    "release_before_issue": "전매제한 해제일이 발행일보다 앞섭니다",
    "release_date_missing": "전매제한 해제일이 없습니다",
    # --- ③ 9 반대의사 ----------------------------------------------------
    "dissent_period_mismatch": "반대의사 접수기간이 API 값과 다릅니다",
    "api_deadline_absent": "API에 반대의사 접수기간이 없어 대조할 수 없습니다",
    "superseded_api_reference": "이전 버전이라 최신 API 값과 대조할 수 없습니다",
    # --- 10 정정 해석 -----------------------------------------------------
    "correction_rows_unparsed": "정정사항 표의 일부가 기록에 없습니다",
    "unsupported_change": "정정사항 표가 뒷받침하지 않는 변경이 있습니다",
    "no_correction_rows": "정정사항 표를 읽지 못했습니다",
    # --- event level ------------------------------------------------------
    "withdrawn": "철회된 공시입니다",
    "no_gate": "이 필드에 정의된 게이트가 없습니다",
}


@dataclass(frozen=True)
class Check:
    """One named deterministic test. ``ok is None`` means it could not run."""

    name: str
    ok: bool | None
    reason: str | None = None
    detail: str | None = None

    @property
    def skipped(self) -> bool:
        return self.ok is None

    def render(self) -> str:
        mark = "ok" if self.ok else ("skip" if self.ok is None else "FAIL")
        tail = f"({self.detail})" if self.detail else ""
        return f"{self.name}={mark}{tail}"


def check_passed(name: str, detail: str | None = None) -> Check:
    return Check(name, True, None, detail)


def check_failed(name: str, reason: str, detail: str | None = None) -> Check:
    return Check(name, False, reason, detail)


def check_skipped(name: str, detail: str | None = None) -> Check:
    """A check whose reference value does not exist — recorded, never a pass."""
    return Check(name, None, None, detail)


@dataclass
class Outcome:
    """A gate's verdict on one field, with the checks that produced it."""

    status: str
    reason_code: str | None = None
    checks: list[Check] = field(default_factory=list)
    #: Set only for ``tbd`` / ``not_evaluable``, where the reason is not a failure.
    detail: str | None = None

    @property
    def exposable(self) -> bool:
        return self.status in EXPOSABLE_STATUSES

    @property
    def note(self) -> str:
        """One audit line: every check, in the order it ran."""
        rendered = " ".join(c.render() for c in self.checks)
        head = f"{self.status}"
        if self.reason_code:
            head += f":{self.reason_code}"
        if self.detail:
            head += f" — {self.detail}"
        return f"{head} | {rendered}" if rendered else head

    @property
    def reason_ko(self) -> str | None:
        return REASON_LABELS_KO.get(self.reason_code or "")


def verdict(checks: list[Check], *, empty_reason: str = "no_gate") -> Outcome:
    """Derive the verdict from the checks that ran. The only way to build a pass.

    First failure wins the reason code (checks are ordered cheapest/most
    fundamental first, so the first failure is the most explanatory one), and a
    gate where **every** check was skipped is ``not_evaluable`` rather than a
    pass — a gate that compared nothing has not vouched for anything.
    """
    for check in checks:
        if check.ok is False:
            return Outcome(FAILED, check.reason, checks)
    if any(check.ok for check in checks):
        return Outcome(PASSED, None, checks)
    return Outcome(NOT_EVALUABLE, empty_reason, checks)


def tbd(reason: str, checks: list[Check], detail: str | None = None) -> Outcome:
    return Outcome(TBD, reason, checks, detail)


def not_evaluable(reason: str, checks: list[Check] | None = None, detail: str | None = None) -> Outcome:
    return Outcome(NOT_EVALUABLE, reason, checks or [], detail)
