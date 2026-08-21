"""철회 detection — deterministic, from one ``3. 정정사항`` row.

The finding this module exists for (N39): **two currently-exposable ① events have
already been withdrawn and every deterministic layer above says they are
healthy.** 썸에이지 ``20260805000454`` and 제이알글로벌리츠 ``20260205000605`` each
file a ~1.9k-char ``[기재정정]`` whose label table still parses 10/10 and whose
정정사항 table holds a single row:

    항목 ``유상증자 결정`` · 정정 전 ``유상증자 결정`` · 정정 후 ``유상증자 철회``

Publishing 썸에이지 today would advertise a 매매기간 that has been cancelled.

**A keyword test does not work and must not be attempted.** S4 measured
``"철회" in 본문``: it also fires on 증권신고서 and 매수청구 boilerplate. Re-measured
here over **every 정정사항 row this workspace holds — 1,282 rows in 328 distinct
본문 documents**: the word appears in the 정정 후 cell of **14 rows and only 4 of
them are withdrawals** (a 71 % false-positive rate). The other 10 are the ③
반대의사 procedure text (``매수청구를 철회할 수 있습니다``), a 정정신고서 notice and a
주주명부폐쇄 paragraph. So the detector keys on the row's *shape*, not on the word:

1. the 정정 후 cell is **short** (≤ 30 squashed chars) — boilerplate never is. On
   this corpus that bound alone is already exact: 4 short cells, 4 withdrawals;
2. the cell **is** the withdrawal — it *ends* with ``철회`` (+ an optional verb),
   rather than mentioning one mid-sentence;
3. the 항목 carries **no form number** — ``유상증자 결정`` is the filing's subject,
   whereas ``13. 주식매수청구권에 관한 사항`` is one field inside it;
4. its subject either restates 정정 전 (``유상증자 결정`` → ``유상증자 철회``) or is a
   filing-level decision by name — which is what catches 코퍼스코리아
   ``20260130000680``, whose 항목 is the bare ``전 항목`` and whose 정정 후 reads
   ``유상증자 발행 결정 철회``. Rule 4 was widened *because* that row existed: the
   first draft required the 정정 전 restatement and silently missed it.

That shape is rights-type agnostic: ``회사합병 결정 → 회사합병 철회`` and
``전환사채권 발행결정 → … 철회`` satisfy it unchanged. **② is now corpus-exercised
and the four rules held with no change at all** (``P2.S7``): over **4,627 정정사항
rows in 808 ② 본문 documents**, ``철회`` appears in the 정정 후 cell of **10 rows**;
the shape accepts **9**, and all 9 are genuine withdrawals — **precision 9/9**,
against the keyword test's 71 % false-positive rate on ①/③, because a CB's 정정 후
cells carry none of the 매수청구 boilerplate. ③ still has no real case.

**The tenth row is a false NEGATIVE, and it is left uncaught on purpose.**
비트플래닛 ``20260616000274`` withdraws its CB in a 143-character *paragraph* under
``23. 기타 투자판단에 참고할 사항`` — ``발행대상자 … 의 투자 진행 철회 통보에 따라
부득이하게 철회하게 됨`` — which fails three of the four rules (too long, does not
*end* with 철회, numbered 항목). Relaxing any of them to admit it would re-admit the
①/③ boilerplate the rules exist to reject. It is safe to miss because the second
line of defence holds: its API detail row is blank in all 46 fields, so
:mod:`mijual.gates.exposure` refuses to render it anyway (``incomplete_api_row``).
Recorded, not rendered — but the *reason* shown is weaker than the truth.

**②'s withdrawals are invisible to every other layer, and worse than ①'s were.**
When a CB issuance is withdrawn OpenDART keeps the detail row and **blanks every
field to** ``-`` (46 keys, all empty — 베노티앤알 ``20260211001003``, 핀텔
``20260417000537``, 센서뷰 ``20260227007913`` …). So the API-completeness test in
:mod:`mijual.gates.exposure` already refuses to render them — but it refuses for
the wrong reason, saying *"we do not have the numbers"* about an event whose truth
is *"this was cancelled"*. Only this detector, reading the one 정정사항 row, turns
that silence into a citable sentence with a span behind it.

Corpus result (0 requests, 0 calls): ①'s 6 filings (N47/N55) plus **② 8 events /
9 filings** — 드래곤플라이 ``20250915000168``, 캔버스엔 ``20250806000321``, 아이톡시
``20251231000642``, 베노티앤알 ``20260211001003``, 코퍼스코리아 ``20260130000634`` +
``…642`` (one event, two filings), 센서뷰 ``20260227007913``, 핀텔
``20260417000537``, 대진첨단소재 ``20260714000506``. **None of the 8 would have been
rendered even without this detector** — their blanked API rows fail the
completeness test — so the value here is not the block, it is the *sentence*: they
move from ``no_detail``/``incomplete_api_row`` (a silence) to
``이 사채 발행은 철회되었습니다`` with a 정정사항 row and a span behind it. Two corps
(베노티앤알, 코퍼스코리아) withdrew a 유상증자 **and** a CB on the same day.

N55's rule stands and was demonstrated again: **the count is a floor at the
document coverage it was measured at.** 대진첨단소재 was found only after one more
본문 was fetched for an event the contract had blocked as ``incomplete_api_row`` —
which is why ``python -m mijual.cb documents --blocked`` exists.

Nothing here deletes anything. A withdrawal is recorded on the event and the
extractions stay exactly as they were: the evidence of what the filing once said
is the thing that makes "이 유상증자는 철회되었습니다" tellable at all.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from sqlalchemy.orm import Session

from mijual.bodydoc.correction import CorrectionItem, parse_correction
from mijual.db.models import Event, FilingVersion
from mijual.db.repository import document_of, readable_versions
from mijual.gates.context import squash

__all__ = [
    "MAX_AFTER_CHARS",
    "Withdrawal",
    "detect_withdrawal",
    "is_withdrawal_row",
]

#: A 정정 후 cell longer than this is prose, not a verdict on the filing itself.
#: Measured: over **1,282 정정사항 rows in 328 distinct documents**, exactly 4
#: rows have a 정정 후 cell containing ``철회`` within 40 squashed characters — and
#: all 4 are genuine withdrawals. The length bound alone carries the precision;
#: everything below it is defence in depth.
MAX_AFTER_CHARS = 30
_MARKERS = ("철회",)
#: The cell must *be* the withdrawal, not mention one.
_IS_WITHDRAWAL = re.compile(r"철회(?:함|한다|합니다|하였습니다|결정|의건|건)?$")
#: Stripped to leave the *subject* of the row (``유상증자 결정 철회`` → ``유상증자``).
#: Deliberately conservative: only the verdict words and punctuation are removed,
#: never a particle, or ``주식의 포괄적 교환`` would stop matching its own 정정 전.
_SUBJECT_NOISE = ("철회", "결정", "발행", "(", ")", "「", "」", "·", "-", "ㆍ")
#: A withdrawal names the filing's own subject. Keeps a hypothetical
#: ``기타 → 청약 철회`` row (a *field* being withdrawn) out.
_DECISION_SUBJECTS = (
    "유상증자",
    "무상증자",
    "합병",
    "분할",
    "주식교환",
    "주식이전",
    "포괄적교환",
    "전환사채",
    "신주인수권부사채",
    "교환사채",
    "자본감소",
    "영업양수",
    "영업양도",
    "공개매수",
    "자기주식",
)


def is_withdrawal_row(item: CorrectionItem) -> bool:
    """Does this ``3. 정정사항`` row say the filing's own decision was withdrawn?

    Four shape rules, each measured against the corpus rather than guessed —
    see the module docstring for why the obvious keyword test is not one of them.
    """
    after = squash(item.after)
    if not any(marker in after for marker in _MARKERS):
        return False
    if len(after) > MAX_AFTER_CHARS or not _IS_WITHDRAWAL.search(after):
        return False
    if item.item_number is not None:
        return False
    subject = after
    for noise in _SUBJECT_NOISE:
        subject = subject.replace(noise, "")
    if len(subject) < 2:
        return False
    # Either the row restates its own 정정 전 subject (``유상증자 결정`` →
    # ``유상증자 철회``), or the subject is a filing-level decision — which is what
    # covers 코퍼스코리아's ``전 항목`` → ``유상증자 발행 결정 철회``.
    return (
        subject in squash(item.before)
        or subject in squash(item.item)
        or any(known in subject for known in _DECISION_SUBJECTS)
    )


@dataclass(frozen=True)
class Withdrawal:
    """The evidence for a withdrawal — never a bare boolean."""

    rcept_no: str
    item: str
    before: str
    after: str
    span: tuple[int, int] | None

    @property
    def note(self) -> str:
        where = f" span={self.span}" if self.span else ""
        return f"{self.rcept_no} 정정사항 '{self.item}': {self.before} → {self.after}{where}"


def detect_withdrawal(session: Session, event: Event) -> Withdrawal | None:
    """Scan an event's stored 본문 snapshots, newest first, for a withdrawal row.

    Newest first because a withdrawal is terminal: once a filer withdraws, later
    versions of the same event do not un-withdraw it (a revived offering is a new
    filing with its own 접수일, i.e. a different event under the N2 key).
    """
    for version in reversed(readable_versions(event)):
        loaded = document_of(session, version)
        if loaded is None:
            continue
        block = parse_correction(loaded[1])
        for item in block.items:
            if is_withdrawal_row(item):
                return Withdrawal(
                    rcept_no=version.rcept_no,
                    item=" ".join(item.item.split())[:120],
                    before=" ".join(item.before.split())[:120],
                    after=" ".join(item.after.split())[:120],
                    span=item.after_span.as_tuple() if item.after_span else None,
                )
    return None


def scan_withdrawal_rows(session: Session, event: Event) -> list[tuple[FilingVersion, CorrectionItem]]:
    """Every 정정사항 row of an event whose 정정 후 mentions 철회 — detector *input*.

    Used by the CLI's audit view: it prints what the word-level signal would have
    caught so the shape rules stay honest about their own precision.
    """
    found: list[tuple[FilingVersion, CorrectionItem]] = []
    for version in readable_versions(event):
        loaded = document_of(session, version)
        if loaded is None:
            continue
        for item in parse_correction(loaded[1]).items:
            if any(marker in item.after or marker in item.item for marker in _MARKERS):
                found.append((version, item))
    return found
