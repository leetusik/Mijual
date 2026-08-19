"""The 10 extraction targets of field-matrix §7 — and nothing else.

§7 is the LLM's **entire** reading job for the MVP. Everything else in the
service's field list is an ``API`` field or a ``본문-label`` row, i.e.
deterministic, and the phase constraint is blunt about it: *anything
deterministically readable must not be paid for with an LLM call*. So this
registry is a closed list, ``tests/test_extract.py`` asserts it stays disjoint
from :data:`mijual.bodydoc.labels.LABEL_FIELDS`, and a field that turns out to be
label-readable belongs in ``bodydoc``, not here.

Each :class:`FieldSpec` carries four things:

``value_schema``
    the JSON schema of the **normalized** value — ISO dates, decimal ratios,
    enums where §7 says enum-ish. The model is asked for a shape, not for prose.
``instruction``
    the per-field Korean instruction pasted into the prompt, naming the 본문
    location §7 measured (``24-라``, ``24-다`` …) so the model looks in the right
    place instead of pattern-matching the whole document.
``gate``
    §7's gate for the field, carried as documentation for ``P2.S5``. **This slice
    never evaluates it** — layer 1 reads, layer 2 judges, and keeping the two
    apart is what makes the gate testable with the LLM switched off.
``anchor``
    a regex naming where the field lives, used only to slice a *large* document
    into a window (see :mod:`mijual.extract.inputs`). Never used to parse a value.

Every field's model output has the same envelope — ``present`` / ``value`` /
``quote`` / ``note`` — because the quote is the load-bearing part: the span is
resolved from it deterministically (:mod:`mijual.extract.locate`) and never taken
from the model.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

__all__ = [
    "FIELDS",
    "FieldSpec",
    "SCHEMA_VERSION",
    "TASKS",
    "TaskSpec",
    "field_keys_for",
    "response_schema",
]

#: Bumped when a value schema changes shape. Part of ``Extraction``'s identity,
#: so a bump records a new reading beside the old one instead of overwriting it.
SCHEMA_VERSION = "v1"

_DATE = {"type": ["string", "null"], "description": "YYYY-MM-DD"}
_TEXT = {"type": ["string", "null"]}


@dataclass(frozen=True)
class FieldSpec:
    """One §7 extraction target."""

    key: str
    #: §7's row number (1–10) — kept so a report can be read against the doc.
    number: int
    #: Korean name as §7 prints it.
    name: str
    #: ``R1`` ① / ``R2`` ② / ``R3`` ③ / ``ALL``.
    rights: str
    #: 본문 위치 per §7 (``24-라``, ``9-1.`` …).
    location: str
    value_schema: dict[str, Any]
    instruction: str
    #: §7's gate — ``P2.S5``'s specification, documentation here.
    gate: str
    #: Where to look when the document is too large to send whole.
    anchor: str | None = None

    @property
    def schema(self) -> dict[str, Any]:
        """The per-field envelope the model must return."""
        return {
            "type": "object",
            "properties": {
                "present": {
                    "type": "boolean",
                    "description": "이 문서에 해당 항목이 실제로 기재되어 있으면 true",
                },
                "value": self.value_schema,
                "quote": {
                    "type": ["string", "null"],
                    "description": (
                        "값의 근거가 되는 본문 구절을 **입력 텍스트에서 그대로** 복사. "
                        "요약·교정·재작성 금지. 20~200자 권장."
                    ),
                },
                "note": {"type": ["string", "null"], "description": "판단이 애매하면 이유를 한 줄로"},
            },
            "required": ["present", "value", "quote", "note"],
        }


FIELDS: dict[str, FieldSpec] = {}


def _add(spec: FieldSpec) -> FieldSpec:
    FIELDS[spec.key] = spec
    return spec


# --- ① 유상증자 신주인수권 — the five prose fields of §1.1's 🔴 rows -----------
_add(
    FieldSpec(
        key="warrant_trading_period",
        number=1,
        name="신주인수권증서 상장·매매기간",
        rights="R1",
        location="24-라 (기타 투자판단에 참고할 사항 → 신주인수권에 관한 사항)",
        anchor=r"신주인수권증서|상장예정기간|매매기간",
        value_schema={
            "type": ["object", "null"],
            "properties": {
                "start_date": _DATE,
                "end_date": _DATE,
                "trading_days": {"type": ["integer", "null"], "description": "N영업일/거래일 기재값"},
                "listing_date": dict(_DATE, description="증서 상장일이 따로 적혀 있으면"),
            },
            "required": ["start_date", "end_date", "trading_days", "listing_date"],
        },
        instruction=(
            "신주인수권증서의 **상장(예정)기간 / 매매기간**의 시작일과 종료일. "
            "표기 변형이 많다(상장예정기간, 매매기간, 5영업일간, 5거래일간). "
            "한 문서에 날짜 범위가 둘 이상이면 '신주인수권증서'가 명시된 것만 고른다. "
            "청약기간·납입일·배정기준일을 여기에 적지 말 것."
        ),
        gate="date order; must fall between 배정기준일 and 청약일 (§7 #1)",
    )
)

_add(
    FieldSpec(
        key="subscription_agents",
        number=2,
        name="청약 취급처 (대상자별 증권사 + 청약일)",
        rights="R1",
        location="24-다 (청약취급처)",
        anchor=r"청약\s*취급처|청약\s*장소|청약사무\s*취급",
        value_schema={
            "type": ["object", "null"],
            "properties": {
                "entries": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "target": dict(_TEXT, description="청약대상자 (구주주/일반공모/우리사주조합 등)"),
                            "agent": dict(_TEXT, description="청약취급처 (증권사·지점)"),
                            "start_date": _DATE,
                            "end_date": _DATE,
                        },
                        "required": ["target", "agent", "start_date", "end_date"],
                    },
                }
            },
            "required": ["entries"],
        },
        instruction=(
            "청약 대상자별 **청약취급처(증권사)와 청약일**. 표 형태가 보통이나 절 제목과 행 "
            "구성이 발행사마다 다르다. 대상자별로 한 항목씩 만들고, 날짜가 하나면 "
            "start_date와 end_date를 같게 둔다."
        ),
        gate="청약일 must equal 본문 `11. 청약예정일` (§7 #2)",
    )
)

_add(
    FieldSpec(
        key="forfeited_share_method",
        number=3,
        name="실권주 처리 방식",
        rights="R1",
        location="24-나 (신주의 배정방법)",
        anchor=r"실권주|미청약",
        value_schema={
            "type": ["object", "null"],
            "properties": {
                "method": {
                    "type": ["string", "null"],
                    "enum": ["일반공모", "대표주관회사인수", "미발행", "기타", None],
                    "description": "본문이 말하는 실권주 처리 방식",
                },
                "detail": dict(_TEXT, description="방식의 핵심 조건 한두 문장"),
            },
            "required": ["method", "detail"],
        },
        instruction=(
            "구주주 청약 후 남은 **실권주를 어떻게 처리하는지**. "
            "일반공모(잔여주 공모청약) / 대표주관회사인수(잔액인수) / 미발행(발행 철회) 중 "
            "본문이 말하는 것을 고르고, 어느 것도 아니면 기타 + detail에 설명."
        ),
        gate="enum-ish; must name 일반공모 / 대표주관회사 인수 / 미발행 (§7 #3)",
    )
)

_add(
    FieldSpec(
        key="excess_subscription",
        number=4,
        name="초과청약 조건 (비율)",
        rights="R1",
        location="24-나 3) 초과청약",
        anchor=r"초과\s*청약",
        value_schema={
            "type": ["object", "null"],
            "properties": {
                "allowed": {"type": ["boolean", "null"], "description": "초과청약이 허용되면 true"},
                "ratio": {
                    "type": ["number", "null"],
                    "description": "배정 신주 1주당 초과청약 가능 주식수 (0.2 = 20%). 소수로.",
                },
                "detail": _TEXT,
            },
            "required": ["allowed", "ratio", "detail"],
        },
        instruction=(
            "초과청약 허용 여부와 **비율**. '배정 신주 1주당 0.2주', '20%' 모두 ratio=0.2로 "
            "정규화한다. 초과청약이 없다고 적혀 있으면 allowed=false, ratio=null."
        ),
        gate="0 < ratio ≤ 1; 배정주식수 × ratio arithmetic check (§7 #4)",
    )
)

_add(
    FieldSpec(
        key="issue_price_formula",
        number=5,
        name="발행가액 산정방법 (1·2차·확정 산식)",
        rights="R1",
        location="24-가 (신주발행가액 산정방법)",
        anchor=r"발행가액\s*산정|산정방법|기준주가",
        value_schema={
            "type": ["object", "null"],
            "properties": {
                "first_price_method": dict(_TEXT, description="1차 발행가액 산식 요약"),
                "second_price_method": dict(_TEXT, description="2차 발행가액 산식 요약"),
                "final_price_method": dict(_TEXT, description="확정 발행가액 산식 요약"),
                "discount_rate": {
                    "type": ["number", "null"],
                    "description": "할인율 (25% -> 0.25). 여러 개면 확정 발행가액 기준.",
                },
                "final_price_date": dict(_DATE, description="확정 발행가액 산정(공시) 예정일"),
            },
            "required": [
                "first_price_method",
                "second_price_method",
                "final_price_method",
                "discount_rate",
                "final_price_date",
            ],
        },
        instruction=(
            "발행가액 산정 방법을 1차/2차/확정으로 나누어 각각 한 문장으로 요약하고, "
            "할인율은 소수로 정규화한다. 문서에 없는 단계는 null."
        ),
        gate="확정발행가 ≤ MAX(…) consistency vs 본문 `6.` (§7 #5)",
    )
)

# --- ② CB·EB — declared for completeness; P2.S7 owns the corpus --------------
_add(
    FieldSpec(
        key="refixing_terms",
        number=6,
        name="리픽싱 세부 조건",
        rights="R2",
        location="9. 전환가액 조정에 관한 사항",
        anchor=r"전환가액\s*조정|리픽싱",
        value_schema={
            "type": ["object", "null"],
            "properties": {
                "floor_price": {"type": ["number", "null"], "description": "조정 최저가액 (원)"},
                "floor_ratio": {"type": ["number", "null"], "description": "최초 전환가액 대비 비율 (0.7)"},
                "adjustment_period": dict(_TEXT, description="조정 주기 (3개월마다 등)"),
                "detail": _TEXT,
            },
            "required": ["floor_price", "floor_ratio", "adjustment_period", "detail"],
        },
        instruction="전환가액 조정(리픽싱)의 최저 한도와 조정 주기.",
        gate="floor must equal API `act_mktprcfl_cvprc_lwtrsprc` (§7 #6)",
    )
)

_add(
    FieldSpec(
        key="option_schedule",
        number=7,
        name="콜·풋 세부 스케줄",
        rights="R2",
        location="9-1. 옵션에 관한 사항",
        anchor=r"옵션에\s*관한|매도청구권|조기상환청구권|콜옵션|풋옵션",
        value_schema={
            "type": ["object", "null"],
            "properties": {
                "options": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "kind": {"type": ["string", "null"], "enum": ["call", "put", None]},
                            "holder": _TEXT,
                            "start_date": _DATE,
                            "end_date": _DATE,
                            "ratio": {"type": ["number", "null"], "description": "행사 가능 비율 (0.3)"},
                            "detail": _TEXT,
                        },
                        "required": ["kind", "holder", "start_date", "end_date", "ratio", "detail"],
                    },
                }
            },
            "required": ["options"],
        },
        instruction="매도청구권(콜)·조기상환청구권(풋)의 행사 기간과 비율.",
        gate="dates within 사채 발행일 ~ 만기일 (§7 #7)",
    )
)

_add(
    FieldSpec(
        key="lockup_release",
        number=8,
        name="보호예수 / 전매제한 해제일",
        rights="R2",
        location="19. + 기타 투자판단에 참고할 사항",
        anchor=r"보호예수|전매\s*제한|예탁",
        value_schema={
            "type": ["object", "null"],
            "properties": {
                "release_date": _DATE,
                "months": {"type": ["integer", "null"], "description": "예치 기간 (개월)"},
                "detail": _TEXT,
            },
            "required": ["release_date", "months", "detail"],
        },
        instruction="사채·주식의 전매제한(보호예수) 해제일과 기간.",
        gate="≥ 발행일; cross-check `ex_sm_r` (§7 #8)",
    )
)

# --- ③ 매수청구권 -------------------------------------------------------------
_add(
    FieldSpec(
        key="dissent_notice_procedure",
        number=9,
        name="반대의사 통지 방법·절차",
        rights="R3",
        location="13. 주식매수청구권에 관한 사항",
        anchor=r"주식매수청구권|반대의사|매수청구",
        value_schema={
            "type": ["object", "null"],
            "properties": {
                "notice_start_date": dict(_DATE, description="반대의사 통지 접수 시작일"),
                "notice_end_date": dict(_DATE, description="반대의사 통지 접수 종료일"),
                "exercise_start_date": dict(_DATE, description="매수청구권 행사 시작일"),
                "exercise_end_date": dict(_DATE, description="매수청구권 행사 종료일"),
                "method": dict(_TEXT, description="통지 방법 (서면/방문/우편 등)"),
                "recipient": dict(_TEXT, description="접수처 (회사 주소·부서, 명의개서대리인 등)"),
                "detail": _TEXT,
            },
            "required": [
                "notice_start_date",
                "notice_end_date",
                "exercise_start_date",
                "exercise_end_date",
                "method",
                "recipient",
                "detail",
            ],
        },
        instruction=(
            "주주가 **반대의사를 통지하는 방법과 절차**: 접수 기간, 제출 방법, 접수처. "
            "매수청구권 행사기간이 따로 적혀 있으면 exercise_* 에 넣는다 "
            "(반대의사 접수기간과 혼동하지 말 것)."
        ),
        gate="기한 must equal API `mgsc_mgop_rcpd_bgd/_edd` (§7 #9)",
    )
)

# --- 정정 해석 (모든 타입) -----------------------------------------------------
_add(
    FieldSpec(
        key="correction_interpretation",
        number=10,
        name="정정 해석 (무엇이 바뀌어 D-day가 어떻게 이동했나)",
        rights="ALL",
        location="<CORRECTION> 3. 정정사항",
        anchor=r"정정사항|정정\s*전|정정\s*후",
        value_schema={
            "type": ["object", "null"],
            "properties": {
                "changes": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "item": dict(_TEXT, description="정정된 항목명 (본문 표기 그대로)"),
                            "field_hint": dict(_TEXT, description="해당하는 서비스 필드가 있으면 그 이름"),
                            "old": _TEXT,
                            "new": _TEXT,
                            "kind": {
                                "type": ["string", "null"],
                                "enum": ["date_moved", "amount_changed", "text_changed", "other", None],
                            },
                            "direction": {
                                "type": ["string", "null"],
                                "enum": ["연기", "앞당김", "해당없음", None],
                                "description": "날짜가 바뀐 경우에만 연기/앞당김",
                            },
                            "quote": {
                                "type": ["string", "null"],
                                "description": "정정 후 본문에서 그대로 복사한 근거 구절",
                            },
                        },
                        "required": ["item", "field_hint", "old", "new", "kind", "direction", "quote"],
                    },
                },
                "schedule_impact": dict(
                    _TEXT, description="일정(D-day)에 미친 영향 한두 문장. 없으면 '일정 변동 없음'"
                ),
                "summary": dict(_TEXT, description="이 정정을 한 문장으로"),
            },
            "required": ["changes", "schedule_impact", "summary"],
        },
        instruction=(
            "아래 **결정론적으로 파싱된 정정사항 표가 무엇이 바뀌었는지에 대한 사실**이다. "
            "표에 없는 변경을 만들어내지 말고, 표의 값과 다르게 적지 말 것. "
            "당신의 일은 각 변경을 정규화(날짜·금액)하고 일정에 미친 영향을 해석하는 것이다."
        ),
        gate="before/after must both parse; changed dates must move monotonically (§7 #10)",
    )
)


@dataclass(frozen=True)
class TaskSpec:
    """One call: a set of fields read from one document in one request.

    Grouping matters for money. The five ① prose fields all live in the same
    ``24. 기타 투자판단에 참고할 사항`` block of a 2.6k–10k-char document, so
    reading them in **one** call costs one input pass instead of five (28 events
    × 5 fields would otherwise be 140 calls on its own — most of the slice's
    whole ceiling). Per-field records are unaffected: the response envelope is
    still per field, and so is every stored row.
    """

    key: str
    fields: tuple[str, ...]
    #: Korean framing sentence for the prompt.
    header: str
    prompt_version: str = "p1"

    @property
    def specs(self) -> list[FieldSpec]:
        return [FIELDS[k] for k in self.fields]


TASKS: dict[str, TaskSpec] = {
    "r1_prose": TaskSpec(
        key="r1_prose",
        fields=(
            "warrant_trading_period",
            "subscription_agents",
            "forfeited_share_method",
            "excess_subscription",
            "issue_price_formula",
        ),
        header=(
            "다음은 한국 상장사의 **주요사항보고서(유상증자결정)** 본문 전체 텍스트다. "
            "여기서 아래 항목만 정확히 읽어 JSON으로 답하라."
        ),
    ),
    "r3_prose": TaskSpec(
        key="r3_prose",
        fields=("dissent_notice_procedure",),
        header=(
            "다음은 한국 상장사의 **주요사항보고서(합병 등 결정)** 본문 텍스트다. "
            "여기서 아래 항목만 정확히 읽어 JSON으로 답하라."
        ),
    ),
    "r2_prose": TaskSpec(
        key="r2_prose",
        fields=("refixing_terms", "option_schedule", "lockup_release"),
        header=(
            "다음은 한국 상장사의 **주요사항보고서(전환사채/교환사채 발행결정)** 본문 텍스트다. "
            "여기서 아래 항목만 정확히 읽어 JSON으로 답하라."
        ),
    ),
    "correction": TaskSpec(
        key="correction",
        fields=("correction_interpretation",),
        header=(
            "다음은 한국 상장사의 **정정 공시** 본문에서 결정론적으로 파싱한 정정사항 표와, "
            "정정 전/후 버전에서 추출된 값의 차이다. 이를 해석해 JSON으로 답하라."
        ),
    ),
}

#: The rights types this slice actually runs (② is ``P2.S7``'s corpus).
RUN_TASKS = ("r1_prose", "r3_prose", "correction")


def field_keys_for(rights: str) -> tuple[str, ...]:
    return tuple(k for k, s in FIELDS.items() if s.rights == rights)


def response_schema(task: TaskSpec) -> dict[str, Any]:
    """The whole response schema for one task — one envelope per field."""
    return {
        "type": "object",
        "properties": {
            "fields": {
                "type": "object",
                "properties": {spec.key: spec.schema for spec in task.specs},
                "required": [spec.key for spec in task.specs],
            }
        },
        "required": ["fields"],
    }
