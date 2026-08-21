"""The 대화 로그 / 익명 세션 / 피드백 port — framed in P5, filled by P6.

R7 signs **six** ops tabs and forbids component fragments ("모든 섹션은 ops 크롬을
갖춘 완전한 페이지"), but three of its surfaces read data that belongs to the AI
질문 agent, which is **P6**: the conversation log, the anonymous-session
aggregates and the ``save_feedback`` queue. Dropping them would break the signed
chrome; inventing a 「준비 중」 string would invent Korean copy; and creating the
tables here would put P6's schema in P5.

So this is the seam. P5 defines the interface and ships
:class:`EmptyConversations`, which returns empty results, and **creates no
conversation table at all**. The endpoints serve an honest ``0건`` — which is
true: this build stores no conversations. P6 implements the same interface over
its own storage and passes it to
:func:`mijual.web.app.create_app`, exactly the way ``P5.S7``'s
:class:`mijual.mail.Mailer` leaves the real transport to P4. No route changes.

**Three rules the port carries, so P6 inherits them rather than re-deciding:**

1. **No account, email, IP or user-agent field exists in any shape here.**
   `security`'s anonymity promise (「대화는 익명으로 저장됩니다 (품질 점검용)」) is
   kept at the schema level, and a port that offered an ``account_id`` filter
   would be an invitation to break it in the implementation. The 사용자 tab's two
   tables are two independent reads for the same reason: 계정↔대화 연결
   컴럼·조인·추정 매칭 금지.
2. **Read-only.** There is no delete, no edit, no tagging and no processed-state
   bit (R7: 읽기 전용 — 삭제·편집·태깅 없음; 처리 상태 비트 없음). The whole panel
   has no mutation endpoint (§6.5) and this port must not become the exception.
3. **Cursor pagination, newest first.** R7 asks for 시간 역순 커서 페이지네이션 on
   the log; the cursor is an opaque string this layer never interprets.

The dataclasses below are the *shape of the answer*, not of the storage: P6 owns
the columns. A row is a plain mapping so P6 can serve the fields R7 lists
(세션 해시 · 시각 KST · 범위 · 질문 · 답변/거절 · 거절 카테고리 · 근거 rcept_no ·
인용 칩 원문) without this module having to know them before they exist.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol, Sequence, runtime_checkable

__all__ = [
    "Conversations",
    "EmptyConversations",
    "Page",
]


@dataclass(frozen=True)
class Page:
    """One page of rows, newest first, plus the cursor for the next one.

    ``total`` is the count the tab renders (R7's 「대기 0건」 empty state needs a
    number, not an absence). ``next_cursor`` is ``None`` at the end of the list —
    and is **omitted** from the payload rather than serialized as ``null``, the
    contract-wide rule for an absent value.
    """

    rows: Sequence[Mapping[str, Any]] = field(default_factory=tuple)
    total: int = 0
    next_cursor: str | None = None

    def payload(self) -> dict[str, Any]:
        body: dict[str, Any] = {"count": self.total, "rows": [dict(r) for r in self.rows]}
        if self.next_cursor is not None:
            body["next_cursor"] = self.next_cursor
        return body


@runtime_checkable
class Conversations(Protocol):
    """What the 대화 로그 · 익명 세션 · 피드백 tabs read. Implemented by P6.

    Every method is a read and every one of them returns a :class:`Page`. The
    filters are exactly the ones R7 signs — 유형 (답변/거절), 거절 카테고리, and a
    session hash for the two-way cross-link between the log and the 사용자 tab —
    and there is deliberately nothing else: a filter this panel does not render is
    a query surface nobody asked for.
    """

    def conversations(
        self,
        *,
        kind: str | None = None,
        refusal_category: str | None = None,
        session_hash: str | None = None,
        cursor: str | None = None,
        limit: int = 50,
    ) -> Page:
        """The log, newest first. ``kind`` is ``answer`` | ``refusal``."""

    def sessions(self, *, cursor: str | None = None, limit: int = 50) -> Page:
        """익명 세션 aggregates: 세션 해시 · 최근 활동 · 질문 수 · 거절 수 · 마지막 범위."""

    def feedback(self, *, cursor: str | None = None, limit: int = 50) -> Page:
        """The ``save_feedback`` queue: 시각 · 의견 · 답장 이메일(선택) · 세션 해시."""


class EmptyConversations:
    """P5's implementation: there is no conversation storage, so there are none.

    Not a stub and not a placeholder — a truthful source. P5 creates no
    conversation table (DECOMP note 5), so ``0건`` is what this build actually
    holds, and the tabs render that rather than a Korean string nobody signed.
    """

    def conversations(
        self,
        *,
        kind: str | None = None,
        refusal_category: str | None = None,
        session_hash: str | None = None,
        cursor: str | None = None,
        limit: int = 50,
    ) -> Page:
        return Page()

    def sessions(self, *, cursor: str | None = None, limit: int = 50) -> Page:
        return Page()

    def feedback(self, *, cursor: str | None = None, limit: int = 50) -> Page:
        return Page()
