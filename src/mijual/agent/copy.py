"""The agent's Korean strings — **transcribed from R6, never composed freely**.

The convention `frontend/lib/copy.ts` and `frontend/components/chrome/copy.ts`
already use, on the server side: every string below carries the round and section
it came from, so a reader can check it against the record instead of trusting it.
The phase's rule (`P6` note 17): 「Inventing a Korean sentence is a design change」
— P5 shipped an English framework 404 rather than invent one.

**Two provenance tiers, marked per constant.**

*Signed* — the exact words or the exact format a round fixed: R6
(``docs/reference/design/rounds/06-explain/output/build-prompt.md`` §Agent and
``…/result.md`` §Agent capabilities) and, where R16 superseded it,
``rounds/16-smart-assistant/output/build-prompt.md`` §0 (`AGENT_INTRO_KO`, the
보안 sentence, `STATUS_KO`). These are copied character for character,
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
    "AGENT_INTRO_KO",
    "BARE_FAMILIES",
    "BOARD_POINTER_KO",
    "CALC_MISS_ROW",
    "CALC_NAMES_KO",
    "CALC_NONE_ROW",
    "CALC_ROW",
    "CALC_UNITS_KO",
    "CONTACT_ROW",
    "CONTACT_UNSET_ROW",
    "EVENT_MISS_ROW",
    "EVENT_ROW",
    "FEEDBACK_RETRY_ROW",
    "FEEDBACK_ROW",
    "FEEDBACK_SAVED_KO",
    "LIVE_REFUSAL_SENTENCES",
    "NOT_FOUND_KO",
    "PORTFOLIO_ROW",
    "PORTFOLIO_SAMPLE_LABEL_KO",
    "PORTFOLIO_SAMPLE_ROW",
    "REFUSAL_SENTENCES",
    "RETIRED_FAMILIES",
    "RIGHTS_TOOL_LABEL_KO",
    "SEARCH_ITEM",
    "SEARCH_ROW",
    "SECURITY_FAMILY",
    "STATUS_KO",
    "family_of",
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
#: throughout the record. **No href travels with it** — the route belongs to
#: `frontend/lib/routes.ts` (the board is `/`, not `/board`), the surface builds
#: it from the `{"kind": "board"}` link the turn serves, and a path string in a
#: tool payload is a string the citation gate would let the model *say*
#: (`citations.py`'s verbatim-string rule). `P6.S3` recorded the dead route as a
#: nit; `P6.S7` removed it rather than correcting it, because the agent should
#: not carry a route at all.
BOARD_POINTER_KO = "관제 현황판"

#: 내 포트폴리오, verbatim from result.md §Agent capabilities:
#: `내 포트폴리오 읽기 → 샘플 포트폴리오 · 4종목 (구성 예시)`. The count is the
#: reading's own, so it is a placeholder here and 4 in the signed example.
PORTFOLIO_SAMPLE_ROW = "내 포트폴리오 읽기 → 샘플 포트폴리오 · {n}종목 (구성 예시)"
#: 「답변에 "구성 예시" 명기」 (R6-3) — the label the sample answer must carry.
PORTFOLIO_SAMPLE_LABEL_KO = "구성 예시"

#: 의견 저장, verbatim from result.md §Agent capabilities:
#: `의견 저장 → 운영자 검토 대기열`.
FEEDBACK_ROW = "의견 저장 → 운영자 검토 대기열"

#: The confirmation line, verbatim from result.md §Proposed copy 의견. Kept here
#: beside the row it follows; the surface renders it (`P6.S5`), the agent never
#: writes it as prose.
FEEDBACK_SAVED_KO = "의견을 저장했습니다 — 운영자가 확인합니다."

#: 에이전트 인트로 — **R16 D1, verbatim** (build-prompt §0), superseding R6's three
#: sentences. Every clause of the old promise had been overtaken by this phase:
#: 「검증을 통과한 공시에 대해서만 답합니다」 was contradicted the moment a greeting
#: stopped being a refusal (`P9.S4`), 「모든 답에는 원문 인용이 붙습니다」 the moment
#: 인용 강제 became a rule about 공시 사실 문장 only, and 「계산은 하지 않습니다」 the
#: moment the calculator landed (`P9.S5`). D1 says what is still true, and says it
#: as a promise about the reader rather than about the machinery.
#:
#: A **surface** string, transcribed here because it is the agent's own promise and
#: this file is where the agent's words live. It is not *served*: nothing in
#: :mod:`mijual.web` reads it, and the two surfaces that print it hold their own
#: copy in ``frontend/components/ask/copy.ts``, which `P9.S8` lands. Until then the
#: two sides differ on purpose — the record's word here, the shipped word there —
#: and nothing breaks, because no code compares them.
AGENT_INTRO_KO = "주주의 권리를 지키기 위해 공시를 근거로 질문에 답합니다."

# ---------------------------------------------------------------------------
# 거절 가족 (R6-7) — signed, and the only sentences a refusal may say
# ---------------------------------------------------------------------------
#: The family name, once, so nothing spells it twice. R16 signs it in
#: :data:`mijual.web.conversationstore.REFUSAL_FAMILIES`' own six-value order.
SECURITY_FAMILY = "보안"

#: The six families and their sentences, **verbatim**: five from R6's result.md
#: §Proposed copy (「거절 가족 (R6-7)」) — 철회 · 확정 전 · 공시에 없음 · 계산 요청 ·
#: 폴백 — and 보안, R16's new one (build-prompt §0, D3), in the record's own order.
#: The keys are
#: :data:`mijual.web.conversationstore.REFUSAL_FAMILIES`, the exact strings R7's
#: 거절 카테고리 filter sends, so a stored row is findable by the panel that was
#: built for it.
#:
#: Three rules ride on this mapping and none of them is a style choice:
#:
#: * **the family is the most specific thing said** — R6 forbids per-reason-code
#:   wording, and the reader payload carries no gate reason code at all, so there
#:   is nothing more specific that could honestly be said;
#: * **a refusal is not an error** — these are ordinary prose sentences on the
#:   ordinary prose path, and the surface gives them body ink, no alert colour and
#:   no icon;
#: * **the loop selects a family by recognising its sentence**, so a paraphrase is
#:   not a softer refusal — under strip-don't-drop it is simply prose, and it
#:   reaches the reader as prose (uncited, and stored as an answer rather than as
#:   a refusal). Recognition runs over :data:`LIVE_REFUSAL_SENTENCES`, not over
#:   this mapping: two of these six are retired and may not be newly recorded.
#:
#: 보안 is the one family the **loop** states rather than the model: it is what the
#: hard reject says (:func:`mijual.agent.loop.run_turn`, `P9.S6`). It is still
#: recognised here like the others, deliberately — see :data:`LIVE_REFUSAL_SENTENCES`.
REFUSAL_SENTENCES: dict[str, str] = {
    "철회": "철회된 공시는 해설하지 않습니다.",
    "확정 전": "확정 전 금액은 해설하지 않습니다.",
    "공시에 없음": "공시에 없는 내용은 해설하지 않습니다.",
    # R16 D3, verbatim from build-prompt §0. Two sentences: the refusal and the
    # standing invitation back to 공시 — which is also why it carries **no 갈 곳
    # 링크** (:data:`BARE_FAMILIES`): the second sentence is the 갈 곳.
    SECURITY_FAMILY: "그 요청에는 답변하지 않습니다. 공시에 대한 질문은 언제든 받습니다.",
    "계산 요청": "해설은 계산하지 않습니다 — 계산은 검증된 수치로 내 종목 조회가 합니다.",
    "검증 미통과 폴백": (
        "이 데이터는 검증을 통과하지 못했습니다. 검증되지 않은 내용은 해설하지 않습니다."
    ),
}

#: The two families that stay in the **stored** vocabulary for past rows and are
#: never newly written (R16 §0: 「은퇴: … 새로 기록하지 않음」). The whitelist a row
#: is validated against is :data:`mijual.web.conversationstore.REFUSAL_FAMILIES`
#: and it keeps all six — this is the producer side of the same decision, and the
#: two are different by design: a turn recorded in 2026-08 must still be findable
#: by a family the product no longer states.
#:
#: * **검증 미통과 폴백** — retired with the sentence-dropping gate that made it
#:   true (`P9.S4`). It was the literal source of the operator's
#:   「이 데이터는 검증을 통과하지 못했습니다」 on a greeting. Its ``REFUSAL_FALLBACK``
#:   constant is **deleted** here (build-prompt §0: 「REFUSAL_FALLBACK 삭제」); the
#:   name survives only as the dictionary key past rows are found by.
#: * **계산 요청** — retired with the calculator (`P9.S5`): 「해설은 계산하지
#:   않습니다」 describes a product that no longer exists, and the auditable
#:   calculation block is what answers 「1,000주면 얼마?」 now.
#:
#: Retiring one is a **code** change, not a copy edit: :func:`family_of`,
#: :func:`mijual.agent.citations._family_at_head` and
#: :func:`mijual.agent.citations._is_family_prefix` all read
#: :data:`LIVE_REFUSAL_SENTENCES`, so from here a model that types either sentence
#: is writing prose — and under strip-don't-drop prose ships.
RETIRED_FAMILIES: frozenset[str] = frozenset({"계산 요청", "검증 미통과 폴백"})

#: The families a turn may still **state** — the mapping every recogniser reads.
#: A retired sentence arriving from the model is therefore not a refusal at all:
#: it is ordinary prose, and under strip-don't-drop ordinary prose ships (which is
#: the honest outcome — the alternative would be writing a retired family to the
#: 대화 로그 the moment the model happens to type its words).
#:
#: **보안 is live here on purpose** (`P9.S6`). The loop's hard reject is what
#: normally states it, but a model that types the signed sentence itself has done
#: the same thing the other three live families do — refused in the record's own
#: words — and the honest record of that turn is a 보안 row the operator can find
#: in 대화 로그, not prose that hides one. Recognising it also keeps the two paths
#: from disagreeing: one sentence, one family, whoever emitted it.
LIVE_REFUSAL_SENTENCES: dict[str, str] = {
    family: sentence
    for family, sentence in REFUSAL_SENTENCES.items()
    if family not in RETIRED_FAMILIES
}

#: Families whose sentence is followed by **nothing** — no 갈 곳 링크, no 답변 푸터.
#:
#: R6's refusal is three moves (사실 · 가족 문장 · 갈 곳 링크) because it declines
#: *a question about 공시* and the reader still has somewhere to go. R16 §4 check 11
#: writes the 보안 turn differently and exactly: 「보안」 가족 문장만 — 도구 실행 0 ·
#: 인용 0 · **링크 0** · 점검 언급 0 · 같은 턴에 추가 프로즈 0. Its sentence already
#: carries its own invitation (「공시에 대한 질문은 언제든 받습니다」), and a
#: 내 종목 조회 link under it would be the surface offering a destination to a
#: request the product just declined to serve.
#:
#: Read by :func:`mijual.agent.loop._finish`, so the rule is a property of the
#: family and not a branch on a Korean string in the loop.
BARE_FAMILIES: frozenset[str] = frozenset({SECURITY_FAMILY})


# ---------------------------------------------------------------------------
# 진행 표시 (R16 D5) — signed, and the only sentences a status line may say
# ---------------------------------------------------------------------------
#: The five phases and their sentences, **verbatim** from R16 build-prompt §0
#: (`docs/reference/design/rounds/16-smart-assistant/output/build-prompt.md`,
#: ``STATUS_KO``). The keys are :data:`mijual.agent.events.STATUS_PHASES`.
#:
#: They live here, server-side, for the same reason the 도구 행 strings do: the
#: agent's Korean is composed once and the surface renders it **verbatim**
#: (:class:`~mijual.agent.events.StatusEvent` carries the sentence beside its
#: phase), so there is no second copy of a signed string in TypeScript to drift
#: from this one.
#:
#: R16 §2.1: the line is 진행 중인 상태 — 항상 하나, phase가 바뀌면 텍스트만 교체,
#: 첫 문장에 소멸, **애니메이션 없음**. It is never stored (transient).
STATUS_KO: dict[str, str] = {
    "read": "질문을 읽고 있습니다",
    "search": "공시를 찾고 있습니다",
    "open": "공시 원문을 읽고 있습니다",
    "calc": "계산하고 있습니다",
    "write": "답변을 정리하고 있습니다",
}


def family_of(sentence: str) -> str | None:
    """Which signed family this sentence **is**, or ``None``.

    Exact match only: a family is selected by the record's own words arriving
    verbatim, never by a keyword in something that resembles them — and only a
    **live** family is selectable (:data:`RETIRED_FAMILIES`), because recognising
    a retired sentence would newly record a family R16 retired.
    """
    text = sentence.strip()
    return next(
        (
            family
            for family, signed in LIVE_REFUSAL_SENTENCES.items()
            if signed == text
        ),
        None,
    )

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


#: 계산, in the same ``{도구} → {결과}`` grammar as every other row — transcribed
#: from the round's own reference implementation
#: (``rounds/16-smart-assistant/output/r16-parts.babel.js``:
#: ``계산 → 초과청약 한도 · 1,000주 × 0.2주 = 200주`` and
#: ``계산 → 확정 발행가액 미공시 · 0건``). 「계산」 is R16 D6's own word (진행 줄
#: 「계산 중」, 결과 마커 「계산」, 머리말 「검증된 계산」/「식 계산」) and 「0건」 is the
#: count idiom :data:`EVENT_MISS_ROW` already writes, so neither row coins a word.
#:
#: Three rows, because a calculation fails in two different places: ``CALC_ROW``
#: when it computed, ``CALC_MISS_ROW`` when a **drawn** calculation could not (the
#: reason names the input that stopped it, in its own label and value — no sentence
#: is invented for it), and ``CALC_NONE_ROW`` when the call was never a drawable
#: calculation at all, which is the model's mistake and carries no reason the
#: reader could act on.
CALC_ROW = "계산 → {name} · {expr}"
CALC_MISS_ROW = "계산 → {why} · 0건"
CALC_NONE_ROW = "계산 → 0건"

#: The 계산 블록 머리말's name for each **named** operation — 「검증된 계산 · {이름}」.
#: Every one of them is the product's own existing word, not a coined one, and the
#: server (never the model) supplies it: the heading of a verified calculation must
#: name the operation that actually ran.
#:
#: * 배정 신주 — R4's own caption label (``frontend/components/lookup/copy.ts``:
#:   「배정 {k}주 = {n}주 × 배정비율 {ratio}」);
#: * 초과청약 한도 — :func:`mijual.calc.excess_subscription_cap`'s own docstring
#:   (「§7 #4's arithmetic: 초과청약 한도 = 배정주식수 × 초과청약비율」);
#: * 소멸 증서 — :mod:`mijual.present.summary`'s own words (「소멸 증서 and 발행 증서
#:   are cited counts」), R4 writes the count 「발행 − 청약 = 소멸 {k}주」;
#: * D-day — the board's own vocabulary (:attr:`mijual.calc.DDay.label`), not Korean
#:   at all;
#: * 전매제한 해제일 — :func:`mijual.calc.lockup_release_date`'s own docstring, and
#:   :data:`mijual.present.FIELD_NAMES_KO`'s 「보호예수 / 전매제한 해제일」.
CALC_NAMES_KO: dict[str, str] = {
    "allotted_shares": "배정 신주",
    "excess_subscription_cap": "초과청약 한도",
    "lapsed_warrants": "소멸 증서",
    "d_day": "D-day",
    "lockup_release_date": "전매제한 해제일",
}

#: The unit each named operation's **result** is read in. 「주」 is the product's own
#: share unit wherever it counts one (R4: 「+{k}주」, 「발행 − 청약 = 소멸 {k}주」; R16's
#: own calculation fixture reads 「200주」), and a date or a D-day label carries none.
#: The escape hatch has no entry here at all: 식 계산 returns arithmetic, and a unit
#: on it would be the server asserting what the arithmetic *meant*.
CALC_UNITS_KO: dict[str, str] = {
    "allotted_shares": "주",
    "excess_subscription_cap": "주",
    "lapsed_warrants": "주",
    "d_day": "",
    "lockup_release_date": "",
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
