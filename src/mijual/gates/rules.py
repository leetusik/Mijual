"""One named gate per field-matrix §7 row — the whole of §3.6 layer 2.

§7's *gate* column is the specification and each function below implements
exactly its row, in the order §7 prints them:

===  ====================================  =========================================
 #   field                                 gate (§7)
===  ====================================  =========================================
 1   신주인수권증서 상장·매매기간            date order; between 배정기준일 and 청약일
 2   청약 취급처                            청약일 must equal 본문 ``11. 청약예정일``
 3   실권주 처리 방식                        enum: 일반공모 / 대표주관회사 인수 / 미발행
 4   초과청약 조건                          0 < ratio ≤ 1; 배정주식수 × ratio 산술 검증
 5   발행가액 산정방법                       확정발행가 consistency vs 본문 ``6.``
 6   리픽싱 세부 조건                        floor == API ``act_mktprcfl_cvprc_lwtrsprc``
 7   콜·풋 세부 스케줄                       dates within 발행일 ~ 만기일
 8   보호예수 / 전매제한 해제일               ≥ 발행일
 9   반대의사 통지 방법·절차                  기한 == API ``mgsc_mgop_rcpd_bgd/_edd``
10   정정 해석                              정정사항 rows parse; changes subset-consistent
===  ====================================  =========================================

Three rules bind every one of them.

**The citation gate runs first, on every field.** A value whose quote could not
be located in the stored snapshot is not a citation, so it is blocked
(``span_unresolved``) before any arithmetic is attempted. There is exactly one
such value in today's corpus (LB세미콘 ``20260730000278`` ``issue_price_formula``,
N37) and it must stay blocked.

**A gate compares against evidence the model never saw** — 본문 labels and the
stored API detail row (see :mod:`mijual.gates.context`), never against another
model output.

**Conservative on absence.** A check whose reference value does not exist is
*skipped*, not passed; a gate all of whose checks were skipped is
``not_evaluable`` and the field is not shown.

**Gates 6–8 were exercised for the first time by ``P2.S7``** (62 rows each, over
the ② urgency set) and two of the three needed the corpus, exactly as §7's ①
rows did (N45):

* **#6 리픽싱** held as written — the 본문's 최저 조정가액 equals the API's
  ``act_mktprcfl_cvprc_lwtrsprc`` in **29 of 29** comparable rows, 0 mismatches;
  the other 13 skip because the API field itself is blank (180/267 filled).
* **#7 콜·풋** held, and its one failure is a real catch (see #8's).
* **#8 보호예수 moved**: a CB states the 전매제한 as a *duration*, not a date
  (``사모발행에 의한 1년간 …``) in 31 of 62 rows, and the rows that did carry a date
  carried one the **model** computed. So the date is now derived deterministically
  from the API 납입일 (:func:`mijual.calc.lockup_release_date`) and any stated date
  is checked against it. Its 3 failures — and #7's one — all land on the same
  finding: a 정정 whose 본문 ``최초제출일`` names an event this workspace never
  collected got attached to a *different* CB of the same corp, and the
  API-derived cross-check is the only layer that noticed.

**One gate is not a §7 row.** ``P5.S6`` added ③'s 매수예정가격 (D-15) as a
``본문-label`` field — read for free by :mod:`mijual.extract.labelfields`, judged
here by :func:`gate_appraisal_price` against the ③ API row's ``aprskh_plnprc``.
The registry below is therefore "every field the product may show", which is
what :func:`evaluate_field` needs it to be, rather than "§7's ten".
"""

from __future__ import annotations

import re
from typing import Callable

from mijual.calc import lockup_release_date
from mijual.db.models import Extraction
from mijual.gates.context import VersionContext, iso_date, korean_date, squash
from mijual.gates.outcome import (
    Check,
    Outcome,
    check_failed,
    check_passed,
    check_skipped,
    not_evaluable,
    tbd,
    verdict,
)

__all__ = ["GATES", "citation_check", "evaluate_field", "gate_for"]

#: §7 #3's enum, normalized to the model's own value set.
FORFEIT_METHODS = {"일반공모", "대표주관회사인수", "미발행"}
#: Targets whose 청약일 is *not* in 본문 ``11.`` — the 실권주 일반공모 that follows it.
_PUBLIC_OFFER = ("일반공모", "일반투자자", "잔여주", "실권주", "고위험고수익")
_RATIO_PER_SHARE = re.compile(r"1\s*주\s*당\s*([\d.]+)\s*주")
_RATIO_PERCENT = re.compile(r"(\d{1,3}(?:\.\d+)?)\s*%")
#: The 원 amount inside a 매수예정가격 citation — the last number it prints.
_PRICE_IN_QUOTE = re.compile(r"([\d][\d,]*(?:\.\d+)?)\s*원?\s*$")
#: How far a filing's own 전매제한 해제일 may sit from ``납입일 + N개월`` before the
#: gate calls it a different claim. A CB states 발행일 and 납입일 within a day or
#: two of each other and the prose picks either; 3 days covers that and nothing
#: like a mis-derived year.
LOCKUP_DERIVATION_TOLERANCE_DAYS = 3


# ---------------------------------------------------------------------------
# the citation gate — every field, before anything else
# ---------------------------------------------------------------------------
def citation_check(row: Extraction, ctx: VersionContext) -> Check:
    """*원문 인용 스팬 존재* — the gate S3 built the whole span machinery for (N33).

    ``resolved`` is the requirement; ``span_verified`` (byte-faithful) is
    preferred and recorded, because the 2 ``trimmed`` cases in this corpus differ
    from the document only by a list marker the model re-rendered (``①`` → ``1)``)
    and blocking them would be pedantry, not diligence.
    """
    if row.span_status == "resolved":
        detail = "verified" if row.span_verified else f"located:{row.locate_method}"
        return check_passed("citation", detail)
    if row.span_status == "unresolved":
        return check_failed("citation", "span_unresolved", row.locate_method or "no match")
    return check_failed("citation", "span_missing", str(row.span_status))


# ---------------------------------------------------------------------------
# ① 1 — 신주인수권증서 상장·매매기간
# ---------------------------------------------------------------------------
def gate_warrant_trading_period(row: Extraction, ctx: VersionContext) -> Outcome:
    """Date order, and the window between 배정기준일 and 청약일 (§7 #1).

    This is the countdown's own field, so ``추후결정`` is handled here first: a
    verified citation with null dates and a document that says 추후결정 is
    ``tbd``, **not** a pass and never a fallback to the superseded schedule (N40).
    """
    checks = [citation_check(row, ctx)]
    if not checks[0].ok:
        return verdict(checks)

    value = row.value if isinstance(row.value, dict) else {}
    start, end = iso_date(value.get("start_date")), iso_date(value.get("end_date"))
    if start is None or end is None:
        if ctx.says_tbd(row):
            checks.append(check_passed("schedule_stated", "추후결정"))
            return tbd("schedule_tbd", checks, "본문이 일정을 추후결정으로 유보")
        checks.append(check_failed("dates_present", "dates_missing"))
        return verdict(checks)

    checks.append(
        check_passed("date_order", f"{start}~{end}")
        if start <= end
        else check_failed("date_order", "date_order", f"{start} > {end}")
    )

    record = ctx.record_date
    if record is None:
        checks.append(check_skipped("after_record_date", "본문 8. 없음"))
    else:
        checks.append(
            check_passed("after_record_date", f"> {record}")
            if start > record
            else check_failed("after_record_date", "not_after_record_date", f"{start} <= {record}")
        )

    first = ctx.first_subscription_date
    if first is None:
        checks.append(check_skipped("before_subscription", "본문 11. 없음"))
    else:
        checks.append(
            check_passed("before_subscription", f"< {first}")
            if end < first
            else check_failed("before_subscription", "not_before_subscription", f"{end} >= {first}")
        )
    return verdict(checks)


# ---------------------------------------------------------------------------
# ① 2 — 청약 취급처
# ---------------------------------------------------------------------------
def gate_subscription_agents(row: Extraction, ctx: VersionContext) -> Outcome:
    """Per-대상자 청약일 equality against 본문 ``11. 청약예정일`` (§7 #2).

    Two 대상자 families need different treatment, and measuring the corpus is what
    settled it: 55 우리사주조합/구주주 entries match 본문 ``11.`` **exactly**, while
    23 일반공모 entries have no ``11.`` row at all — the 실권주 일반공모 청약 is a
    later, separate window (계양전기: 구주주 09-03~09-04, 일반공모 09-08~09-09).
    So the 일반공모 entries are gated on *ordering* (they must follow the 구주주
    청약) rather than on an equality that has no reference.
    """
    checks = [citation_check(row, ctx)]
    if not checks[0].ok:
        return verdict(checks)

    entries = (row.value or {}).get("entries") if isinstance(row.value, dict) else None
    if not entries:
        checks.append(check_failed("entries_present", "no_entries"))
        return verdict(checks)

    labels = ctx.subscription_dates
    shareholder = ctx.shareholder_subscription
    dated = [e for e in entries if iso_date(e.get("start_date")) or iso_date(e.get("end_date"))]
    if not dated and ctx.says_tbd(row):
        checks.append(check_passed("schedule_stated", f"{len(entries)}건 추후결정"))
        return tbd("schedule_tbd", checks, "청약일이 추후결정")

    matched = mismatched = ordered = skipped_entries = 0
    detail_bad: list[str] = []
    for entry in entries:
        target = str(entry.get("target") or "")
        start, end = iso_date(entry.get("start_date")), iso_date(entry.get("end_date"))
        if any(k in target for k in _PUBLIC_OFFER) and "구주주" not in target:
            close = shareholder.get("end")
            if start is None or close is None:
                skipped_entries += 1
            elif start > close:
                ordered += 1
            else:
                mismatched += 1
                detail_bad.append(f"일반공모 {start} <= 구주주 종료 {close}")
            continue
        group = "우리사주" if "우리사주" in target else "구주주"
        reference = labels.get(group)
        if reference is None or start is None or end is None:
            skipped_entries += 1
            continue
        if (start, end) == (reference.get("start"), reference.get("end")):
            matched += 1
        else:
            mismatched += 1
            detail_bad.append(
                f"{group} {start}~{end} != 본문 11. "
                f"{reference.get('start')}~{reference.get('end')}"
            )

    if mismatched:
        reason = (
            "public_offer_not_after"
            if all("일반공모" in d for d in detail_bad)
            else "subscription_date_mismatch"
        )
        checks.append(check_failed("subscription_dates", reason, "; ".join(detail_bad[:3])))
    elif matched or ordered:
        checks.append(
            check_passed(
                "subscription_dates",
                f"본문 11. 일치 {matched}건, 일반공모 순서 {ordered}건, 미대조 {skipped_entries}건",
            )
        )
    else:
        checks.append(check_skipped("subscription_dates", f"대조 가능한 항목 없음 ({len(entries)}건)"))
    return verdict(checks)


# ---------------------------------------------------------------------------
# ① 3 — 실권주 처리 방식
# ---------------------------------------------------------------------------
def gate_forfeited_share_method(row: Extraction, ctx: VersionContext) -> Outcome:
    """Enum membership: 일반공모 / 대표주관회사 인수 / 미발행 (§7 #3).

    ``기타`` is a **failure**, not a shrug: §7 says the field must name one of the
    three, and a 실권주 plan the reader could not classify is precisely the thing
    the product must not print next to a countdown. Two events sit here today
    (이렘's two event keys) and are recorded, not dropped.
    """
    checks = [citation_check(row, ctx)]
    if not checks[0].ok:
        return verdict(checks)
    method = squash((row.value or {}).get("method") if isinstance(row.value, dict) else None)
    if not method:
        checks.append(check_failed("method_enum", "no_value"))
    elif method in FORFEIT_METHODS:
        checks.append(check_passed("method_enum", method))
    else:
        checks.append(check_failed("method_enum", "method_not_enumerated", method))
    return verdict(checks)


# ---------------------------------------------------------------------------
# ① 4 — 초과청약 조건
# ---------------------------------------------------------------------------
def gate_excess_subscription(row: Extraction, ctx: VersionContext) -> Outcome:
    """``0 < ratio ≤ 1`` plus the arithmetic §7 asks for, where a document can carry it.

    §7's *배정주식수 × ratio* is a **per-shareholder** quantity — the document
    states the ratio, not any holder's 주수 — so the multiplication itself lives in
    :func:`mijual.calc.excess_subscription_cap` (deterministic, unit-tested, used
    by P3) and what the gate can check on paper is that the normalized ratio
    equals the ratio the cited text states (``배정 신주 1주당 0.2주`` / ``20%``).
    That catches the real failure mode of a normalized number: a unit slip.
    """
    checks = [citation_check(row, ctx)]
    if not checks[0].ok:
        return verdict(checks)

    value = row.value if isinstance(row.value, dict) else {}
    ratio = value.get("ratio")
    if value.get("allowed") is False and ratio in (None, 0):
        checks.append(check_passed("ratio_range", "초과청약 없음"))
        return verdict(checks)
    if not isinstance(ratio, (int, float)) or not 0 < float(ratio) <= 1:
        checks.append(check_failed("ratio_range", "ratio_out_of_range", str(ratio)))
        return verdict(checks)
    checks.append(check_passed("ratio_range", str(ratio)))

    stated = _stated_ratio(f"{row.quote or ''} {value.get('detail') or ''}")
    if stated is None:
        checks.append(check_skipped("ratio_vs_quote", "인용에 비율 표기 없음"))
    elif abs(stated - float(ratio)) < 1e-9:
        checks.append(check_passed("ratio_vs_quote", f"{stated}"))
    else:
        checks.append(
            check_failed("ratio_vs_quote", "ratio_quote_mismatch", f"{ratio} != 인용 {stated}")
        )
    return verdict(checks)


def _stated_ratio(text: str) -> float | None:
    """The 초과청약 비율 as the cited text writes it (``1주당 0.2주`` / ``20%``)."""
    per_share = _RATIO_PER_SHARE.search(text)
    if per_share:
        try:
            return float(per_share.group(1))
        except ValueError:  # pragma: no cover - regex guarantees a number
            return None
    percent = _RATIO_PERCENT.search(text)
    if percent:
        try:
            return float(percent.group(1)) / 100
        except ValueError:  # pragma: no cover
            return None
    return None


# ---------------------------------------------------------------------------
# ① 5 — 발행가액 산정방법
# ---------------------------------------------------------------------------
def gate_issue_price_formula(row: Extraction, ctx: VersionContext) -> Outcome:
    """Consistency against 본문 ``6. 신주 발행가액`` (§7 #5).

    §7 writes the gate as *확정발행가 ≤ MAX(…) consistency vs 본문 6.* The MAX's
    operands are 가중산술평균주가 — market data this repository does not hold — so
    what is deterministically checkable is the **shape** of the 산식 and its
    schedule: a 확정 발행가액 산식 must exist, its 할인율 must be a fraction, and
    the day the 확정가 is announced must fall between 본문 6.'s 확정예정일 and the
    첫 청약일. A 확정발행가 announced after 청약 opens would be a broken schedule.

    Measured before it was written (the reason it is a window and not an
    equality): 16 filings state the same date in both places, **3 state exactly
    one day later in the prose** — 본문 6. names the day the price is *determined*
    (구주주청약 초일 전 제3거래일), the prose the day it is *공시*.
    """
    checks = [citation_check(row, ctx)]
    if not checks[0].ok:
        return verdict(checks)

    value = row.value if isinstance(row.value, dict) else {}
    final_method = value.get("final_price_method") or value.get("first_price_method")
    if final_method:
        checks.append(check_passed("formula_present", "확정 산식"))
    else:
        checks.append(check_failed("formula_present", "formula_missing"))

    discount = value.get("discount_rate")
    if discount is None:
        checks.append(check_skipped("discount_rate", "할인율 미기재"))
    elif isinstance(discount, (int, float)) and 0 < float(discount) < 1:
        checks.append(check_passed("discount_rate", str(discount)))
    else:
        checks.append(
            check_failed("discount_rate", "discount_rate_out_of_range", str(discount))
        )

    announced = iso_date(value.get("final_price_date"))
    lower, upper = ctx.price_confirm_date, ctx.first_subscription_date
    if announced is None or (lower is None and upper is None):
        checks.append(check_skipped("final_price_date", "본문 6. 확정예정일 또는 산정일 없음"))
    elif (lower is None or announced >= lower) and (upper is None or announced <= upper):
        checks.append(
            check_passed("final_price_date", f"{lower} <= {announced} <= {upper}")
        )
    else:
        checks.append(
            check_failed(
                "final_price_date",
                "final_price_date_out_of_window",
                f"{announced} not in [{lower}, {upper}]",
            )
        )
    return verdict(checks)


# ---------------------------------------------------------------------------
# ② 6·7·8 — written from §7, unexercised until P2.S7's corpus exists
# ---------------------------------------------------------------------------
def gate_refixing_terms(row: Extraction, ctx: VersionContext) -> Outcome:
    """Floor must equal API ``act_mktprcfl_cvprc_lwtrsprc`` (§7 #6).

    Exercised by ``P2.S7``: **29 of 29** comparable rows agree with the API floor
    and none disagree, so §7's row needed no adjustment. The 13 skips are the API
    field's own gaps, not the reading's — and a skip is never a pass.
    """
    checks = [citation_check(row, ctx)]
    if not checks[0].ok:
        return verdict(checks)
    value = row.value if isinstance(row.value, dict) else {}
    floor = value.get("floor_price")
    api_floor = _api_number(ctx.api_value("act_mktprcfl_cvprc_lwtrsprc"))
    if floor is None or api_floor is None:
        checks.append(check_skipped("floor_vs_api", f"본문 {floor} / API {api_floor}"))
    elif abs(float(floor) - api_floor) < 0.5:
        checks.append(check_passed("floor_vs_api", str(api_floor)))
    else:
        checks.append(
            check_failed("floor_vs_api", "floor_price_mismatch", f"{floor} != API {api_floor}")
        )
    ratio = value.get("floor_ratio")
    if ratio is None:
        checks.append(check_skipped("floor_ratio", "미기재"))
    elif isinstance(ratio, (int, float)) and 0 < float(ratio) <= 1:
        checks.append(check_passed("floor_ratio", str(ratio)))
    else:
        checks.append(check_failed("floor_ratio", "floor_ratio_out_of_range", str(ratio)))
    return verdict(checks)


def gate_option_schedule(row: Extraction, ctx: VersionContext) -> Outcome:
    """Call/put dates within 사채 발행일 ~ 만기일 (§7 #7).

    Exercised by ``P2.S7``: 37 rows checked and 1 failed — 엑시큐어하이트론
    ``20260630000509``, whose 조기상환 schedule runs past the 만기일 of the CB it is
    attached to **because the 정정 belongs to a different CB** (see the module
    docstring). §7's rule held; what it caught was an identity error.
    """
    checks = [citation_check(row, ctx)]
    if not checks[0].ok:
        return verdict(checks)
    options = (row.value or {}).get("options") if isinstance(row.value, dict) else None
    if not options:
        checks.append(check_failed("options_present", "no_options"))
        return verdict(checks)
    issued = korean_date(ctx.api_value("bd_isu_dt", "pymd"))
    matures = korean_date(ctx.api_value("bd_mtd", "bd_mtrt_dt"))
    inside = 0
    for option in options:
        start, end = iso_date(option.get("start_date")), iso_date(option.get("end_date"))
        if start and end and start > end:
            checks.append(
                check_failed("option_order", "option_date_order", f"{start} > {end}")
            )
            return verdict(checks)
        for edge in (start, end):
            if edge is None or (issued is None and matures is None):
                continue
            if (issued and edge < issued) or (matures and edge > matures):
                checks.append(
                    check_failed(
                        "option_term",
                        "option_date_out_of_term",
                        f"{edge} not in [{issued}, {matures}]",
                    )
                )
                return verdict(checks)
            inside += 1
    checks.append(
        check_passed("option_term", f"{inside}개 일자 확인")
        if inside
        else check_skipped("option_term", "사채 발행일/만기일 없음")
    )
    return verdict(checks)


def gate_lockup_release(row: Extraction, ctx: VersionContext) -> Outcome:
    """전매제한 해제일 ≥ 발행일, and the date is **derived, not trusted** (§7 #8).

    ``P2.S7`` measured what a CB filing actually says here, and §7's gate had to
    move: **31 of 62 extracted rows state a duration and no date at all**
    (``사모발행에 의한 1년간 행사 및 분할금지``), and every row that *does* carry a
    date carries one the model computed by adding 12 months to the 발행일. Failing
    the first group and passing the second would have rewarded the model for doing
    arithmetic §3.6 assigns to the code.

    So the gate derives the 해제일 itself — :func:`mijual.calc.lockup_release_date`
    over the **API** 납입일 (``pymd``, evidence the model never saw) and the stated
    개월수 — and then:

    * a model-stated date is checked **against** that derivation (±3 days for the
      발행일/납입일 wobble a filing shows), which is a real independent check where
      the old rule had none;
    * a duration with no date passes on the derivation, with the derived date in
      the note so the board can count down to it;
    * neither date nor duration is ``not_evaluable`` — a 전매제한 the filing does
      not quantify is nothing to judge, not a failure.
    """
    checks = [citation_check(row, ctx)]
    if not checks[0].ok:
        return verdict(checks)
    value = row.value if isinstance(row.value, dict) else {}
    stated = iso_date(value.get("release_date"))
    months = value.get("months")
    issued = korean_date(ctx.api_value("pymd", "bd_isu_dt"))
    derived = lockup_release_date(issued, months if isinstance(months, int) else None)

    if stated is None and derived is None:
        return not_evaluable(
            "lockup_not_quantified", checks, "해제일도 예치기간도 기재되지 않음"
        )
    if stated is not None and derived is not None:
        if abs((stated - derived).days) <= LOCKUP_DERIVATION_TOLERANCE_DAYS:
            checks.append(check_passed("release_vs_derived", f"{stated} ≈ {derived} (API 납입일 {issued} + {months}M)"))
        else:
            checks.append(
                check_failed(
                    "release_vs_derived",
                    "release_date_not_derived",
                    f"본문 {stated} != API 납입일 기준 {derived}",
                )
            )
            return verdict(checks)
    elif stated is None:
        checks.append(
            check_passed("release_derived", f"{derived} = API 납입일 {issued} + {months}개월")
        )

    release = stated or derived
    if issued is None:
        checks.append(check_skipped("release_after_issue", "API 납입일 없음"))
    elif release >= issued:
        checks.append(check_passed("release_after_issue", f"{release} >= {issued}"))
    else:
        checks.append(
            check_failed("release_after_issue", "release_before_issue", f"{release} < {issued}")
        )
    return verdict(checks)


# ---------------------------------------------------------------------------
# ③ 9 — 반대의사 통지 방법·절차
# ---------------------------------------------------------------------------
def gate_dissent_notice_procedure(row: Extraction, ctx: VersionContext) -> Outcome:
    """기한 must equal API ``mgsc_mgop_rcpd_bgd`` / ``_edd`` (§7 #9).

    The strictest gate in the set, and it can afford to be: both sides are
    machine values (a 본문 prose reading against the stored detail row), and the
    corpus agrees 10/10. When the API row carries ``-`` there is nothing to
    compare against, and the conservative default applies — ``not_evaluable``,
    not a free pass (휴온스 ``20260804000344`` is the one such event).
    """
    checks = [citation_check(row, ctx)]
    if not checks[0].ok:
        return verdict(checks)

    value = row.value if isinstance(row.value, dict) else {}
    start, end = iso_date(value.get("notice_start_date")), iso_date(value.get("notice_end_date"))
    api_start = korean_date(ctx.api_value("mgsc_mgop_rcpd_bgd"))
    api_end = korean_date(ctx.api_value("mgsc_mgop_rcpd_edd"))
    if api_start is None and api_end is None:
        if not ctx.api_is_current:
            return not_evaluable(
                "superseded_api_reference", checks, f"{ctx.version.rcept_no}은 이전 버전"
            )
        return not_evaluable("api_deadline_absent", checks, "API 반대의사 접수기간이 '-'")
    if start is None and end is None:
        if ctx.says_tbd(row):
            return tbd("schedule_tbd", checks, "접수기간이 추후결정")
        checks.append(check_failed("dissent_period", "dates_missing", f"API {api_start}~{api_end}"))
        return verdict(checks)
    if (start, end) == (api_start, api_end):
        checks.append(check_passed("dissent_period", f"{api_start}~{api_end}"))
    else:
        checks.append(
            check_failed(
                "dissent_period",
                "dissent_period_mismatch",
                f"본문 {start}~{end} != API {api_start}~{api_end}",
            )
        )
    return verdict(checks)


# ---------------------------------------------------------------------------
# ③ 매수예정가격 — a 본문-label field, not a §7 row (P5.S6 / D-15)
# ---------------------------------------------------------------------------
def gate_appraisal_price(row: Extraction, ctx: VersionContext) -> Outcome:
    """본문 ``13. 매수예정가격`` == API ``aprskh_plnprc`` (D-15).

    The same two-witness shape as gate #6 and #9, with one difference worth
    stating: **both witnesses are machine-read here**, because the value is a
    form cell rather than prose (:mod:`mijual.extract.labelfields`). So the gate
    is not defending against a hallucination — it is defending against the two
    things that can actually go wrong with a cell: reading the *wrong* cell, and
    a filing whose own two statements of the price disagree. Measured before it
    was written: **17 of 17** comparable current versions agree, 0 mismatches.

    Absence is conservative in the established way. An empty cell never reaches
    this gate at all (the reader records ``absent`` → ``field_absent``), and an
    API row with ``-`` — or a superseded version, whose reference row belongs to
    a newer filing (N2) — leaves the cross-check *skipped*, not passed. The
    remaining checks are still substantive: the value is the document's own
    number and the citation shows it.
    """
    checks = [citation_check(row, ctx)]
    if not checks[0].ok:
        return verdict(checks)

    value = row.value if isinstance(row.value, dict) else {}
    price = value.get("price")
    if not isinstance(price, (int, float)) or isinstance(price, bool) or float(price) <= 0:
        checks.append(check_failed("price_positive", "appraisal_price_out_of_range", str(price)))
        return verdict(checks)
    checks.append(check_passed("price_positive", f"{int(price):,}원"))

    stated = _stated_price(row.quote)
    if stated is None:
        checks.append(check_skipped("price_vs_quote", "인용에 금액 표기 없음"))
    elif abs(stated - float(price)) < 0.5:
        checks.append(check_passed("price_vs_quote", f"{stated:,.0f}"))
    else:
        checks.append(
            check_failed(
                "price_vs_quote", "appraisal_price_quote_mismatch", f"{price} != 인용 {stated}"
            )
        )
        return verdict(checks)

    api_price = _api_number(ctx.api_value("aprskh_plnprc"))
    if api_price is None:
        checks.append(
            check_skipped(
                "price_vs_api",
                f"{ctx.version.rcept_no}은 이전 버전" if not ctx.api_is_current
                else "API 매수예정가격이 '-'",
            )
        )
    elif abs(api_price - float(price)) < 0.5:
        checks.append(check_passed("price_vs_api", f"{api_price:,.0f}"))
    else:
        checks.append(
            check_failed(
                "price_vs_api", "appraisal_price_mismatch", f"본문 {price} != API {api_price}"
            )
        )
    return verdict(checks)


def _stated_price(text: str | None) -> float | None:
    """The 원 amount the citation itself prints (``매수예정가격 5,649`` → 5649)."""
    match = _PRICE_IN_QUOTE.search(text or "")
    if match is None:
        return None
    try:
        return float(match.group(1).replace(",", ""))
    except ValueError:  # pragma: no cover - the regex guarantees a number
        return None


# ---------------------------------------------------------------------------
# 10 — 정정 해석
# ---------------------------------------------------------------------------
def gate_correction_interpretation(row: Extraction, ctx: VersionContext) -> Outcome:
    """정정사항 rows all parse, and the interpretation stays inside them (§7 #10).

    The deterministic rows are ground truth and the model only normalises (N41),
    so this gate re-parses the ``<CORRECTION>`` block **from the snapshot** and
    requires (a) that the stored record holds every changed row the document
    still yields — a row that stopped parsing is a silent loss of evidence — and
    (b) that no interpreted change is unsupported by those rows. Rows the model
    did not mention are *recorded*, never a failure: that count is ``P2.S9``'s
    recall measurement, not a correctness claim.
    """
    checks = [citation_check(row, ctx)]
    if not checks[0].ok:
        return verdict(checks)

    value = row.value if isinstance(row.value, dict) else {}
    stored_rows = value.get("deterministic_items") or []
    document_rows = ctx.correction.changed_items
    if not document_rows and not stored_rows:
        return not_evaluable("no_correction_rows", checks, "정정사항 표 없음")
    if len(stored_rows) < len(document_rows):
        checks.append(
            check_failed(
                "rows_parsed",
                "correction_rows_unparsed",
                f"기록 {len(stored_rows)}행 < 본문 {len(document_rows)}행",
            )
        )
        return verdict(checks)
    checks.append(check_passed("rows_parsed", f"{len(stored_rows)}행"))

    checked = value.get("deterministic_check") or {}
    unsupported = int(checked.get("unsupported") or 0)
    if unsupported:
        checks.append(
            check_failed("changes_supported", "unsupported_change", f"{unsupported}건")
        )
    else:
        checks.append(
            check_passed(
                "changes_supported",
                f"{checked.get('changes', 0)}건 전부 근거 있음, 미언급 {checked.get('uncovered', 0)}행",
            )
        )
    return verdict(checks)


#: ``field_key`` → its §7 gate. A field with no entry is ``not_evaluable``:
#: a field the product would show without a named gate does not exist.
GATES: dict[str, Callable[[Extraction, VersionContext], Outcome]] = {
    "warrant_trading_period": gate_warrant_trading_period,
    "subscription_agents": gate_subscription_agents,
    "forfeited_share_method": gate_forfeited_share_method,
    "excess_subscription": gate_excess_subscription,
    "issue_price_formula": gate_issue_price_formula,
    "refixing_terms": gate_refixing_terms,
    "option_schedule": gate_option_schedule,
    "lockup_release": gate_lockup_release,
    "dissent_notice_procedure": gate_dissent_notice_procedure,
    "correction_interpretation": gate_correction_interpretation,
    # Not a §7 row: the 본문-label field ``P5.S6`` added for D-15.
    "appraisal_price": gate_appraisal_price,
}


def gate_for(field_key: str) -> Callable[[Extraction, VersionContext], Outcome] | None:
    return GATES.get(field_key)


def evaluate_field(row: Extraction, ctx: VersionContext) -> Outcome:
    """The one entry point: judge one stored extraction row. Pure, no I/O.

    ``absent`` and ``error`` rows never reach a gate — there is no value to
    judge — and they are recorded ``not_evaluable`` so the report can tell "the
    filing does not state this" apart from "the filing states it and we blocked
    it".
    """
    if row.status == "absent":
        return not_evaluable("field_absent")
    if row.status != "extracted":
        return not_evaluable("extraction_error", detail=row.status)
    if row.value is None:
        return not_evaluable("no_value")
    gate = GATES.get(row.field_key)
    if gate is None:  # pragma: no cover - the registry is closed (test asserts it)
        return not_evaluable("no_gate", detail=row.field_key)
    return gate(row, ctx)


def _api_number(value: object) -> float | None:
    text = str(value or "").replace(",", "").strip()
    if not text or text in {"-", "–"}:
        return None
    try:
        return float(text)
    except ValueError:
        return None
