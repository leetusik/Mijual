"""익명 대화 저장소 — the storage behind the AI 질문 log, and its read port.

This is P6's half of the seam :mod:`mijual.web.conversations` framed in P5: the
protocol and :class:`~mijual.web.conversations.EmptyConversations` stay exactly
as they are, and :class:`DbConversations` here implements the same three reads
over the two tables R7 signs (:class:`~mijual.db.models.ConversationTurn` and
:class:`~mijual.db.models.ConversationFeedback`). ``create_app`` wires this
implementation the way it wires the mailer, so **no ``/ops`` route changed** and
no frontend changed: the 대화 로그 · 익명 세션 · 피드백 tabs simply stop being
empty.

**Anonymity is what this module is for.** R7: 「계정·이메일·IP·UA 컬럼은 저장하지
않음 — 표시 정책이 아니라 스키마」. The tables carry no such column and no foreign
key (see :class:`~mijual.db.models.ConversationTurn`), and this module keeps the
promise from the other side too:

* the session handle is **minted here, at random** (:func:`new_session_hash`) and
  is never derived from an address, an agent string, an account or an email —
  hashing an identifier would turn the forbidden join into a lookup;
* a handle that arrives from a client is accepted only if it *looks* like one
  (:func:`is_session_hash`), so the column cannot be used to smuggle a mail
  address or a user id into the log;
* the read side offers exactly R7's filters and nothing else — no filter this
  panel does not render, which is the port's own rule.

**Three reads and two writes, deliberately on different sides.** The port is
read-only (R7 §6.5: the whole panel has no mutation endpoint), so the writes
`P6.S2` (``save_feedback``) and `P6.S4` (per-turn persistence) need are
module-level functions taking the caller's own session — :func:`record_turn` and
:func:`record_feedback`. They are not on :class:`DbConversations` and they are
reachable from no HTTP route in this slice.

**Pagination is a keyset cursor, newest first** (R7: 시간 역순 커서
페이지네이션). The cursor encodes the last row's instant and its tiebreaker,
base64url'd so the layers above treat it as the opaque string the port promises;
``next_cursor`` is **omitted** at the end of the list rather than served as
``null``.
"""

from __future__ import annotations

import base64
import binascii
import re
import secrets
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Iterator, Mapping, Sequence

from sqlalchemy import Select, and_, case, func, or_, select
from sqlalchemy.orm import Session

from mijual.db.models import ConversationFeedback, ConversationTurn
from mijual.web import clock
from mijual.web.conversations import Page
from mijual.web.errors import ApiError

__all__ = [
    "KIND_ANSWER",
    "KIND_REFUSAL",
    "KINDS",
    "REFUSAL_FAMILIES",
    "SCOPE_ALL_KO",
    "DbConversations",
    "is_session_hash",
    "new_session_hash",
    "record_feedback",
    "record_turn",
    "session_hash_or_new",
]

#: 유형 — the port's own vocabulary ("``kind`` is ``answer`` | ``refusal``"),
#: and the values `P5.S9`'s filter already sends.
KIND_ANSWER = "answer"
KIND_REFUSAL = "refusal"
KINDS = (KIND_ANSWER, KIND_REFUSAL)

#: The refusal families this column may hold: **six values**, four live and two
#: read-only. R16 re-signed R6's five (build-prompt §0, result.md §7 계약 확장 2/2):
#:
#: * live — 철회 · 확정 전 · 공시에 없음 (R6, verbatim) and **보안**, the sixth
#:   family the prompt-injection guard states (`P9.S6` is what emits it; a
#:   whitelist is a contract, not a producer, so it is declared here first);
#: * retired — 계산 요청 (superseded by the auditable calculator) and 검증 미통과
#:   폴백 (superseded by strip-don't-drop). They stay in the vocabulary **for past
#:   rows only**: thousands of stored turns carry them, R7's filter must still find
#:   those, and nothing new is ever written with either.
#:
#: They are the stored vocabulary because they are what the panel's filter sends
#: (`frontend/components/ops/copy.ts` ``REFUSAL_CATEGORIES_KO``, the same six in the
#: same order) — inventing an English token for a signed Korean family would be a
#: design change.
REFUSAL_FAMILIES = (
    "철회",
    "확정 전",
    "공시에 없음",
    "보안",
    "계산 요청",
    "검증 미통과 폴백",
)

#: 범위 for a turn asked outside any single event. R6 §범위 모델 signs the words
#: (「그 외 = `범위: 전체 공시`」); the column stores NULL and the row says this.
SCOPE_ALL_KO = "전체 공시"

#: What a session handle may look like: lowercase hex, 16–64 chars. The shape is
#: a guard, not an identity — see the module docstring.
_SESSION_HASH = re.compile(r"\A[0-9a-f]{16,64}\Z")

_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)
_SEP = "\x1f"
#: The panel's ceiling (`P5.S9`'s ``Query(ge=1, le=200)``), restated so a direct
#: caller of this module cannot ask for the whole log in one page either.
_MAX_LIMIT = 200


# ---------------------------------------------------------------------------
# the anonymous session handle
# ---------------------------------------------------------------------------
def new_session_hash() -> str:
    """A fresh anonymous thread handle: 32 hex chars of ``secrets`` randomness.

    **Random, not derived.** R7's 익명 세션 is 「대화 로그의 집계면」 — the handle
    exists to group a reader's own turns into one thread and to let the operator
    see 거절 비중 as a 프리셋·게이트 점검 signal. Deriving it from an IP, a user
    agent, an account id or an email would make it a pseudonymous identifier of a
    *person*, which is the exact thing the schema refuses to hold.

    The client (`P6.S4`/`P6.S5`) keeps it in ``sessionStorage`` beside the thread
    (R6-5/6: sessionStorage, never localStorage) and sends it back; storage only
    ever sees this string.
    """
    return secrets.token_hex(16)


def is_session_hash(value: str | None) -> bool:
    """Does ``value`` have the shape :func:`new_session_hash` mints?"""
    return bool(value) and _SESSION_HASH.match(value or "") is not None


def session_hash_or_new(value: str | None) -> str:
    """The client's handle if it is one, otherwise a fresh handle.

    The transport slice's entry point: a missing, malformed or over-long token is
    replaced rather than trusted, so nothing a client controls reaches the column
    unchecked. A rejected token costs the reader the thread grouping and nothing
    else — there is no account behind it to lose.
    """
    return value if is_session_hash(value) else new_session_hash()


# ---------------------------------------------------------------------------
# the write API — `P6.S2` (save_feedback) and `P6.S4` (per-turn persistence)
# ---------------------------------------------------------------------------
def record_turn(
    session: Session,
    *,
    session_hash: str,
    question: str,
    kind: str,
    answer: str,
    scope_rcept_no: str | None = None,
    refusal_category: str | None = None,
    evidence: Sequence[str] = (),
    quotes: Sequence[str] = (),
    blocks: Sequence[Mapping[str, Any]] = (),
) -> ConversationTurn:
    """Persist one turn — the answer **or** the refusal, with its citations.

    R7: 「거절도 저장 시 인용 동반」, so a refusal is stored exactly like an answer
    (its 3-part prose in ``answer``, its family in ``refusal_category``) rather
    than as an error record. ``evidence`` is the 근거 rcept_no 목록 and ``quotes``
    the 인용 칩 원문, **verbatim** — R6 forbids a reconstructed quote, and a
    summarised one would make the log's 대화 재생 a paraphrase.

    ``blocks`` is R16's contract extension: the turn's **structured blocks, as
    frames**, stored exactly as they were sent (result.md §3-15: 「구조화 블록은
    프로즈로 환언되지 않는다」). A calculation's audit path — its inputs, each
    input's 근거, its expression — has no existence in prose, so paraphrasing it
    into ``answer`` would be losing it. Absent for a turn that produced none: the
    column is NULL rather than an empty list, so a row from before R16 and a row
    with no blocks read the same.

    Four things are refused here rather than written, because each one would
    corrupt something the panel promises:

    * an unknown ``kind`` (the filter has two values);
    * a ``refusal_category`` outside the six stored families, and a refusal with
      none — R6 allows no per-reason-code wording, so the family *is* the
      category, and an invented one would appear in a filter that cannot find it;
    * a category on an answer;
    * a ``session_hash`` that is not a minted handle (see the module docstring).

    Raises :class:`ValueError` for all four: a caller passing one has a bug, and
    an ``INSERT`` that quietly normalises it would hide the bug in the log.
    The row is flushed but **not committed** — the caller's transaction owns that.
    """
    if kind not in KINDS:
        raise ValueError(f"kind must be one of {KINDS}, not {kind!r}")
    if kind == KIND_REFUSAL:
        if refusal_category not in REFUSAL_FAMILIES:
            raise ValueError(
                f"refusal_category must be one of the six stored families "
                f"{REFUSAL_FAMILIES}, not {refusal_category!r}"
            )
    elif refusal_category is not None:
        raise ValueError("an answer carries no refusal_category")
    if not is_session_hash(session_hash):
        raise ValueError("session_hash is not a minted anonymous handle")

    turn = ConversationTurn(
        session_hash=session_hash,
        scope_rcept_no=scope_rcept_no,
        question=question,
        kind=kind,
        answer=answer,
        refusal_category=refusal_category,
        evidence=[str(item) for item in evidence],
        quotes=[str(item) for item in quotes],
        blocks=[dict(block) for block in blocks] or None,
    )
    session.add(turn)
    session.flush()
    return turn


def record_feedback(
    session: Session,
    *,
    text: str,
    email: str | None = None,
    session_hash: str | None = None,
) -> ConversationFeedback:
    """Persist one ``save_feedback`` call — 의견, 답장 이메일(선택), 원 대화.

    ``email`` is stored **only when the reader volunteered it** (R6 §의견: 선택
    이메일 입력 (답장용)); ``None`` and a blank string are the same absence.
    ``session_hash`` is R7's 원 대화 링크 and is optional for the reason the column
    is nullable.

    An empty comment is a :class:`ValueError`: there is nothing to save, and a
    blank row in the 대기열 would be a call the operator cannot act on. Flushed,
    not committed — the caller's transaction owns that.
    """
    comment = (text or "").strip()
    if not comment:
        raise ValueError("save_feedback stores a comment, not an empty string")
    address = (email or "").strip() or None
    if address is not None and len(address) > 254:
        raise ValueError("email exceeds the RFC 5321 address limit")
    if session_hash is not None and not is_session_hash(session_hash):
        raise ValueError("session_hash is not a minted anonymous handle")

    row = ConversationFeedback(text=comment, email=address, session_hash=session_hash)
    session.add(row)
    session.flush()
    return row


# ---------------------------------------------------------------------------
# the opaque cursor
# ---------------------------------------------------------------------------
def _utc(moment: datetime) -> datetime:
    """Naive values come from SQLite and are UTC (:func:`mijual.web.clock.to_kst`)."""
    if moment.tzinfo is None:
        return moment.replace(tzinfo=timezone.utc)
    return moment.astimezone(timezone.utc)


def _micros(moment: datetime) -> int:
    delta = _utc(moment) - _EPOCH
    return delta.days * 86_400_000_000 + delta.seconds * 1_000_000 + delta.microseconds


def _moment(micros: int) -> datetime:
    return _EPOCH + timedelta(microseconds=micros)


def _encode_cursor(moment: datetime, tiebreaker: object) -> str:
    raw = f"{_micros(moment)}{_SEP}{tiebreaker}".encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _decode_cursor(cursor: str) -> tuple[datetime, str]:
    """``cursor`` → (instant, tiebreaker). An unreadable one is a 400, not a page 1.

    Silently restarting from the top would answer a question nobody asked, and the
    operator would page through the log without noticing.
    """
    try:
        padded = cursor + "=" * (-len(cursor) % 4)
        raw = base64.urlsafe_b64decode(padded.encode("ascii")).decode("utf-8")
        micros, tiebreaker = raw.split(_SEP, 1)
        return _moment(int(micros)), tiebreaker
    except (ValueError, binascii.Error, UnicodeDecodeError, OverflowError) as exc:
        raise ApiError("invalid_cursor", "cursor is not readable") from exc


def _decode_row_cursor(cursor: str) -> tuple[datetime, int]:
    """The same, for the two tables whose tiebreaker is a row id."""
    moment, tiebreaker = _decode_cursor(cursor)
    try:
        return moment, int(tiebreaker)
    except ValueError as exc:
        raise ApiError("invalid_cursor", "cursor is not readable") from exc


def _limit(limit: int) -> int:
    return max(1, min(int(limit), _MAX_LIMIT))


# ---------------------------------------------------------------------------
# the row shapes the panel reads
# ---------------------------------------------------------------------------
def _turn_row(turn: ConversationTurn) -> dict[str, Any]:
    """One 대화 로그 row, in the keys `frontend/components/ops/log.ts` reads."""
    row: dict[str, Any] = {
        "session_hash": turn.session_hash,
        "at": clock.iso(turn.created_at),
        "scope": turn.scope_rcept_no or SCOPE_ALL_KO,
        "question": turn.question,
        "kind": turn.kind,
        # The expanded row — 대화 재생: 저장분 그대로.
        "answer": turn.answer,
        "evidence": list(turn.evidence or ()),
        "quotes": list(turn.quotes or ()),
    }
    if turn.refusal_category is not None:
        row["refusal_category"] = turn.refusal_category
    return row


def _feedback_row(row: ConversationFeedback) -> dict[str, Any]:
    body: dict[str, Any] = {"at": clock.iso(row.created_at), "text": row.text}
    # 답장 이메일 (선택) and 원 대화 are absent when they are absent — the
    # contract's rule for an optional value, and the panel renders an empty cell.
    if row.email is not None:
        body["email"] = row.email
    if row.session_hash is not None:
        body["session_hash"] = row.session_hash
    return body


class DbConversations:
    """The port, over the two tables. Reads only — there is no other method here.

    Built with a **session factory** rather than a session: the port is called
    from a route that already has its own request-scoped session, but the port's
    methods take none (P5 framed them that way so an implementation could store
    its rows anywhere). So each read opens a session, rolls it back and closes it,
    which is :func:`mijual.web.deps.get_session`'s rule — a read that reaches the
    end holding pending changes is a bug, and rolling back makes it "nothing
    happened" instead of "a GET wrote something".

    ``create_app`` passes a factory that builds on the app's own lazy engine, so
    constructing this costs no connection.
    """

    def __init__(self, session_factory: Callable[[], Session]) -> None:
        self._session_factory = session_factory

    @contextmanager
    def _read(self) -> Iterator[Session]:
        session = self._session_factory()
        try:
            yield session
        finally:
            session.rollback()
            session.close()

    # -- 대화 로그 ---------------------------------------------------------
    def conversations(
        self,
        *,
        kind: str | None = None,
        refusal_category: str | None = None,
        session_hash: str | None = None,
        cursor: str | None = None,
        limit: int = 50,
    ) -> Page:
        """The log, newest first, with R7's three filters and nothing else."""
        size = _limit(limit)

        def filtered(statement: Select) -> Select:
            if kind:
                statement = statement.where(ConversationTurn.kind == kind)
            if refusal_category:
                statement = statement.where(
                    ConversationTurn.refusal_category == refusal_category
                )
            if session_hash:
                statement = statement.where(ConversationTurn.session_hash == session_hash)
            return statement

        page = filtered(select(ConversationTurn)).order_by(
            ConversationTurn.created_at.desc(), ConversationTurn.id.desc()
        )
        if cursor:
            moment, last_id = _decode_row_cursor(cursor)
            page = page.where(
                or_(
                    ConversationTurn.created_at < moment,
                    and_(ConversationTurn.created_at == moment, ConversationTurn.id < last_id),
                )
            )

        with self._read() as session:
            found = list(session.scalars(page.limit(size + 1)).all())
            total = session.scalar(
                filtered(select(func.count()).select_from(ConversationTurn))
            ) or 0
            rows = found[:size]
            next_cursor = (
                _encode_cursor(rows[-1].created_at, rows[-1].id)
                if len(found) > size and rows
                else None
            )
            return Page(
                rows=[_turn_row(turn) for turn in rows], total=total, next_cursor=next_cursor
            )

    # -- 익명 세션 ---------------------------------------------------------
    def sessions(self, *, cursor: str | None = None, limit: int = 50) -> Page:
        """익명 세션 — 「대화 로그의 집계면」, so it is an aggregate, not a table.

        R7 calls the 사용자 tab's second table exactly that, and deriving it keeps
        the promise cheap to check: there is one place a session can be written
        (a turn) and no row that could ever hold something a turn does not.
        마지막 범위 is the newest turn's own 범위, read back for this page's
        handles in one further query.
        """
        size = _limit(limit)
        last_activity = func.max(ConversationTurn.created_at)
        page = (
            select(
                ConversationTurn.session_hash,
                last_activity.label("last_activity"),
                func.count(ConversationTurn.id).label("questions"),
                func.count(case((ConversationTurn.kind == KIND_REFUSAL, 1))).label("refusals"),
            )
            .group_by(ConversationTurn.session_hash)
            .order_by(last_activity.desc(), ConversationTurn.session_hash.desc())
        )
        if cursor:
            moment, handle = _decode_cursor(cursor)
            page = page.having(
                or_(
                    last_activity < moment,
                    and_(
                        last_activity == moment,
                        ConversationTurn.session_hash < handle,
                    ),
                )
            )

        with self._read() as session:
            found = list(session.execute(page.limit(size + 1)).all())
            total = session.scalar(
                select(func.count(func.distinct(ConversationTurn.session_hash)))
            ) or 0
            aggregates = found[:size]
            handles = [row.session_hash for row in aggregates]
            scopes: dict[str, str | None] = {}
            if handles:
                for handle, scope in session.execute(
                    select(ConversationTurn.session_hash, ConversationTurn.scope_rcept_no)
                    .where(ConversationTurn.session_hash.in_(handles))
                    .order_by(ConversationTurn.created_at.desc(), ConversationTurn.id.desc())
                ).all():
                    scopes.setdefault(handle, scope)
            rows = [
                {
                    "session_hash": row.session_hash,
                    "last_activity": clock.iso(row.last_activity),
                    "questions": row.questions,
                    "refusals": row.refusals,
                    "last_scope": scopes.get(row.session_hash) or SCOPE_ALL_KO,
                }
                for row in aggregates
            ]
            next_cursor = (
                _encode_cursor(aggregates[-1].last_activity, aggregates[-1].session_hash)
                if len(found) > size and aggregates
                else None
            )
            return Page(rows=rows, total=total, next_cursor=next_cursor)

    # -- save_feedback 대기열 ----------------------------------------------
    def feedback(self, *, cursor: str | None = None, limit: int = 50) -> Page:
        """The queue, newest first. No filter — R7's 대기열 has none."""
        size = _limit(limit)
        page = select(ConversationFeedback).order_by(
            ConversationFeedback.created_at.desc(), ConversationFeedback.id.desc()
        )
        if cursor:
            moment, last_id = _decode_row_cursor(cursor)
            page = page.where(
                or_(
                    ConversationFeedback.created_at < moment,
                    and_(
                        ConversationFeedback.created_at == moment,
                        ConversationFeedback.id < last_id,
                    ),
                )
            )

        with self._read() as session:
            found = list(session.scalars(page.limit(size + 1)).all())
            total = session.scalar(select(func.count()).select_from(ConversationFeedback)) or 0
            rows = found[:size]
            next_cursor = (
                _encode_cursor(rows[-1].created_at, rows[-1].id)
                if len(found) > size and rows
                else None
            )
            return Page(
                rows=[_feedback_row(row) for row in rows], total=total, next_cursor=next_cursor
            )
