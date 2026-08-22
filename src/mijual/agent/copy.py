"""The agent's Korean strings — **transcribed from R6, never composed freely**.

The convention `frontend/lib/copy.ts` and `frontend/components/chrome/copy.ts`
already use, on the server side: every string below carries the round and section
it came from, so a reader can check it against the record instead of trusting it.
The phase's rule (`P6` note 17): 「Inventing a Korean sentence is a design change」
— P5 shipped an English framework 404 rather than invent one.

**Two provenance tiers, marked per constant.**

*Signed* — the exact words or the exact format R6 fixed
(``docs/reference/design/rounds/06-explain/output/build-prompt.md`` §Agent and
``…/result.md`` §Agent capabilities). These are copied character for character,
placeholders included.

*Composed* — the record signs three fact-row examples and one format, and the
five tools need five rows. The three composed rows below are built **only** from
vocabulary the record already fixed (``읽기`` from 「내 포트폴리오 읽기」, ``재시도``
from R6's SSE strings, ``미정`` from 「연락처 문자열은 배포 설정값 — 미정, 운영자
지정」) in the grammar the signed examples establish (``{도구} → {결과}``). They
are recorded as an open copy point in ``works/phases/active/P6/phase.md`` for
`P6.S7`/`P6.REVIEW` to confirm against the record; nothing here invents a
*sentence*, and no tool ever writes prose.
"""

from __future__ import annotations

__all__ = [
    "BOARD_POINTER_HREF",
    "BOARD_POINTER_KO",
    "CONTACT_ROW",
    "CONTACT_UNSET_ROW",
    "EVENT_MISS_ROW",
    "EVENT_ROW",
    "FEEDBACK_RETRY_ROW",
    "FEEDBACK_ROW",
    "NOT_FOUND_KO",
    "PORTFOLIO_ROW",
    "PORTFOLIO_SAMPLE_LABEL_KO",
    "PORTFOLIO_SAMPLE_ROW",
    "RIGHTS_TOOL_LABEL_KO",
    "SEARCH_ITEM",
    "SEARCH_ROW",
    "search_row",
]

# ---------------------------------------------------------------------------
# signed
# ---------------------------------------------------------------------------
#: The 도구 행 format, verbatim from build-prompt §Agent: 「형식:
#: `이벤트 검색 「{q}」 → {n}건 · {유형} · {rcept_no}`」. The signed example is
#: `이벤트 검색 「대동기어」 → 1건 · ② 전환사채 · 20251016000315` (result.md §Agent
#: capabilities), which is what fixes ``{items}`` as a repetition of
#: :data:`SEARCH_ITEM` — one ``· {유형} · {rcept_no}`` per hit.
SEARCH_ROW = "이벤트 검색 「{q}」 → {n}건{items}"
SEARCH_ITEM = " · {rights_ko} · {rcept_no}"

#: 검색 0건, verbatim: 「"「{q}」에 해당하는 공시를 찾지 못했습니다" + 관제 현황판
#: 링크 — 추측 금지」. The tool returns this **as a fact**, never as prose it wrote.
NOT_FOUND_KO = "「{q}」에 해당하는 공시를 찾지 못했습니다"
#: The pointer that travels with it. 「관제 현황판」 is the board's own name
#: throughout the record; the route is P5's landed one.
BOARD_POINTER_KO = "관제 현황판"
BOARD_POINTER_HREF = "/board"

#: 내 포트폴리오, verbatim from result.md §Agent capabilities:
#: `내 포트폴리오 읽기 → 샘플 포트폴리오 · 4종목 (구성 예시)`. The count is the
#: reading's own, so it is a placeholder here and 4 in the signed example.
PORTFOLIO_SAMPLE_ROW = "내 포트폴리오 읽기 → 샘플 포트폴리오 · {n}종목 (구성 예시)"
#: 「답변에 "구성 예시" 명기」 (R6-3) — the label the sample answer must carry.
PORTFOLIO_SAMPLE_LABEL_KO = "구성 예시"

#: 의견 저장, verbatim from result.md §Agent capabilities:
#: `의견 저장 → 운영자 검토 대기열`.
FEEDBACK_ROW = "의견 저장 → 운영자 검토 대기열"

# ---------------------------------------------------------------------------
# composed (see the module docstring)
# ---------------------------------------------------------------------------
#: ``get_event``'s row. 「읽기」 is 내 포트폴리오 읽기's verb; the tail is the search
#: format's own ``· {유형} · {rcept_no}``, with the 회사 named because a single
#: event's row has no count to state.
EVENT_ROW = "이벤트 읽기 → {corp_name} · {rights_ko} · {rcept_no}"
#: An unknown or non-renderable filing number. The count is 0 the way a 0건 search
#: states it, and the signed :data:`NOT_FOUND_KO` sentence travels in the payload.
EVENT_MISS_ROW = "이벤트 읽기 → 0건"

#: The reader's own portfolio. Same verb and same 종목 counter as the signed
#: sample row, without the 샘플 · 구성 예시 half that does not apply to it.
PORTFOLIO_ROW = "내 포트폴리오 읽기 → {n}종목"

#: 「실패 시에만 재시도 행」 (R6 §의견), in the tool-row grammar. 「재시도」 is R6's
#: own SSE string.
FEEDBACK_RETRY_ROW = "의견 저장 → 재시도"

#: 운영자 연락처. Unset says 미정 — the record's own word for the state — and the
#: tool never invents an address or a 「준비 중」 line (`P6` Finding 9).
CONTACT_ROW = "운영자 연락처 → {contact}"
CONTACT_UNSET_ROW = "운영자 연락처 → 미정"

#: 유형, as the fact row prints it. **② is verbatim** from the signed example
#: (`… · ② 전환사채 · 20251016000315`); ① and ③ are the same shape over the
#: product's existing terms (`copy.ts` ``RIGHTS_LABEL_KO`` / ``WITHDRAWN_NOTICE_KO``:
#: 유상증자 · 주식매수청구권). Note the deliberate difference from the reader-facing
#: chips, which carry **no** ①②③ numbering (R1 revision): this is the mono 도구 행,
#: and R6's own example numbers it.
RIGHTS_TOOL_LABEL_KO: dict[str, str] = {
    "R1": "① 유상증자",
    "R2": "② 전환사채",
    "R3": "③ 주식매수청구권",
}


def search_row(
    query: str, items: list[tuple[str, str | None]], *, count: int | None = None
) -> str:
    """The 이벤트 검색 fact row: the count, then one ``· 유형 · 접수번호`` per hit.

    ``items`` is ``(rights_type, rcept_no)`` in the order the answer will read
    them. Kept here rather than in the tool so `P6.S5` renders one string
    verbatim and never re-assembles the format in TypeScript.

    ``count`` is how many events the search **found**, which is ``len(items)``
    unless the list was capped: a capped row states the true count and prints the
    hits it carries, so the reader can see that it lists fewer than it found
    rather than being told a smaller number.
    """
    tail = "".join(
        SEARCH_ITEM.format(
            rights_ko=RIGHTS_TOOL_LABEL_KO.get(rights_type, rights_type),
            rcept_no=rcept_no,
        )
        for rights_type, rcept_no in items
        if rcept_no
    )
    n = len(items) if count is None else count
    return SEARCH_ROW.format(q=query, n=n, items=tail)
