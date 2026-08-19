"""Prompt construction — small, Korean, and deliberately context-free.

Two rules shape every prompt here.

**Only the document.** The model is given the 본문 text and nothing else: no
API values, no 본문-label values, no "expected" schedule. That is not minimalism,
it is what keeps ``P2.S5``'s gates meaningful — §7's gate for 청약 취급처 is
*"청약일 must equal 본문 11. 청약예정일"*, so feeding 본문 11's value into the
prompt would let the model copy the answer and the gate would then be checking
the prompt against itself. The deterministic layer stays the independent witness.

**Quote, do not describe.** Every field asks for a verbatim quote because the
span is resolved from it deterministically (:mod:`mijual.extract.locate`). The
instruction is explicit that summarising or "fixing" the quote breaks it — a
paraphrase simply fails to locate and the value is recorded span-unresolved.

The 정정 prompt is the one place context *is* supplied, and it is supplied as
**fact**: the deterministic ``3. 정정사항`` rows (bodydoc) and the value diff this
package computed itself. The model normalises and interprets them; it is told in
so many words not to invent a change or to restate one differently.
"""

from __future__ import annotations

from typing import Any

from mijual.extract.fields import TaskSpec
from mijual.extract.inputs import DocumentInput

__all__ = ["build_correction_prompt", "build_field_prompt"]

_RULES = """규칙:
1. 아래 <본문>에 실제로 적혀 있는 내용만 사용한다. 추정·보완·외부지식·계산 금지.
   해당 항목이 문서에 없으면 present=false, value=null 로 답한다 (빈 값을 지어내지 말 것).
2. quote 는 <본문> 텍스트에서 **문자 그대로 복사**한다. 요약·교정·줄임·재배열 금지.
   길이는 20~200자 정도로, 값이 실제로 적힌 부분을 고른다.
3. 날짜는 YYYY-MM-DD, 비율은 소수(20% -> 0.2), 금액은 숫자만(원 단위)으로 정규화한다.
4. 확신이 없으면 present=false 로 두고 note 에 이유를 한 줄 적는다. 추측은 오답보다 나쁘다."""

#: How much of one 정정사항 cell is pasted into the prompt (the cell can be a
#: whole nested table — S3's ``CELL_TEXT_LIMIT`` is 4,000 chars).
CELL_PROMPT_LIMIT = 600


def build_field_prompt(task: TaskSpec, document: DocumentInput) -> str:
    """Prompt for one document + one task's fields."""
    lines = [task.header, "", _RULES, "", "항목:"]
    for spec in task.specs:
        lines.append(f"- `{spec.key}` — {spec.name} (본문 위치: {spec.location})")
        lines.append(f"  {spec.instruction}")
    lines += [
        "",
        f"<본문 rcept_no={document.doc.rcept_no or '?'} scope={document.scope} "
        f"chars={document.chars}>",
        document.text,
        "</본문>",
    ]
    return "\n".join(lines)


def build_correction_prompt(
    task: TaskSpec,
    document: DocumentInput,
    *,
    items: list[dict[str, Any]],
    field_moves: list[dict[str, Any]],
    old_rcept_no: str | None,
    new_rcept_no: str | None,
) -> str:
    """Prompt for 정정 해석 (§7 #10).

    ``items`` are the deterministic ``3. 정정사항`` rows and ``field_moves`` the
    prose-value differences this package computed between the two versions.
    Both are **ground truth**; the model's job is normalisation + interpretation.
    """
    lines = [
        task.header,
        "",
        "규칙:",
        "1. 아래 [결정론적 정정사항]은 공시 원문에서 기계적으로 파싱한 **사실**이다.",
        "   여기에 없는 변경을 만들어내지 말고, 값을 다르게 적지 말 것.",
        "2. 실제로 값이 달라진 항목만 changes 에 넣는다 (문구만 다듬어진 항목은 제외).",
        "3. 각 change 의 quote 는 아래 <정정 후 본문>에서 **그대로 복사**한다.",
        "4. 날짜는 YYYY-MM-DD 로 정규화하고, 날짜가 뒤로 밀리면 direction='연기',",
        "   앞당겨지면 '앞당김', 날짜 변경이 아니면 '해당없음'.",
        "5. schedule_impact 에는 투자자 일정(D-day)에 미친 영향만 한두 문장으로 적는다.",
        "",
        f"[결정론적 정정사항] (정정 공시 {new_rcept_no or '?'} 의 <CORRECTION> 3. 정정사항 표)",
    ]
    if items:
        for index, item in enumerate(items, 1):
            lines.append(
                f"{index}. 항목: {item.get('item', '')}"
                + (f" | 사유: {item['reason']}" if item.get("reason") else "")
            )
            lines.append(f"   정정 전: {_clip(item.get('before'))}")
            lines.append(f"   정정 후: {_clip(item.get('after'))}")
    else:
        lines.append("(표를 파싱하지 못함 — 본문에서 직접 읽을 것)")

    lines += ["", f"[추출 값 차이] ({old_rcept_no or '?'} -> {new_rcept_no or '?'})"]
    if field_moves:
        for move in field_moves:
            lines.append(
                f"- {move['field_key']}: {_clip(move.get('old'), 200)} "
                f"-> {_clip(move.get('new'), 200)}"
            )
    else:
        lines.append("(추출된 산문 필드 값에는 차이가 없음)")

    lines += [
        "",
        f"<정정 후 본문 rcept_no={new_rcept_no or '?'} scope={document.scope}>",
        document.text,
        "</정정 후 본문>",
    ]
    return "\n".join(lines)


def _clip(value: Any, limit: int = CELL_PROMPT_LIMIT) -> str:
    text = "" if value is None else str(value)
    text = " ".join(text.split())
    return text if len(text) <= limit else text[:limit] + " …(생략)"
