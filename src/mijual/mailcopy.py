"""Every Korean string a mail carries, and where each one comes from.

The same rule ``frontend/lib/copy.ts`` states for the browser, applied to the one
surface the browser never renders: **Korean-only product surface means inventing
a Korean string is a design change**, not an implementation detail. So this
module is a transcription with a citation per line, it is the *only* place in the
backend that spells a sentence a reader will read, and a string with no citation
does not belong in it.

Three provenances appear below and they are not the same thing:

* **signed** — R5's build prompt (``docs/reference/design/rounds/05-account/
  output/build-prompt.md`` § 알림) and its round record § *Proposed copy → Notify*
  wrote these exactly. They are transcribed, never paraphrased.
* **drafted P4.S2** — R5 signed the mail's *skeleton* (제목 · 사실 블록 · 보기 링크
  · 푸터) and the two sentences the footer carries, but not every label inside the
  블록, and it wrote no password-reset mail at all beyond the UI line 「재설정
  링크를 보냈습니다 — 메일함을 확인해 주세요.」. Those are drafted here and go to
  the operator **literally, at the P4 acceptance gate** — the route `intent.md`
  fixes for new Korean copy in this phase ("the phase drafts them; the operator
  approves the exact strings at the gate, not through a design round").
* **drafted P13 — approved literally at the P13 gate** — the 가입 인증 mail. P13
  adds a hard email-verification gate at 가입 and no design round with it, so its
  strings take the same route ``P4.S2`` took: drafted here, listed verbatim in
  the acceptance walkthrough, approved by the operator literally.

**One re-signature, by operator decision.** R5's subject reads ``[미주알] …``.
The 2026-09-02 operator answer to D23 (`intent.md` § *Clarifications Resolved*)
retires that name everywhere: the product is 주주의관제탑 and 미주알 appears
nowhere, including in the 보기 link's sentence.

**Three hard rules this module keeps structurally**, each one R5's:

* **확정발행가 전 금액 금지 — 메일에도 동일.** There is no won amount anywhere in
  this module: no format string takes one, and the 발행가 line states a *state*
  (확정 / 확정 전 + 확정 예정일), never a figure. ②/③ carry no price line at all
  because neither type has a price fact to state.
* **알림 외 메일 금지. Three kinds exist, and the third was added in a diff.**
  마감 알림 (the deadline alert the reader configured) · 비밀번호 재설정 (the reset
  they asked for) · 가입 인증 (``P13``'s 6-digit code, which the reader asked for
  by pressing 계정 만들기). Every one of the three is a mail a reader *initiated*;
  none is sent to them because somebody decided they should hear from us. The
  rule has not been loosened — what it forbids is a marketing or digest
  template, and adding one would still be visible as exactly what it is: a new
  function in this file, in a diff, in a review. The count in this sentence is
  the guard, so it is written out rather than left implied.
* **D-표기 and 마감명 are reused verbatim, never re-spelled.** ``dday`` is
  :attr:`mijual.calc.DDay.label` as the API served it (so 당일 reads ``D-DAY``,
  as the board does) and ``label_ko`` is
  :data:`mijual.present.event.COUNTDOWN_LABELS_KO`. A second spelling of either
  would eventually disagree with the board, and the mail is the copy the reader
  checks the board against.

This module imports nothing but the standard library — it sits under a request
path (the reset mail) and inside a worker (the deadline mail) alike.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timedelta, timezone

__all__ = [
    "DEADLINE_SUBJECT_TEMPLATE",
    "PRODUCT_NAME",
    "RESET_SUBJECT",
    "SIGNUP_VERIFICATION_SUBJECT",
    "deadline_body",
    "deadline_subject",
    "password_reset_body",
    "password_reset_subject",
    "signup_verification_body",
    "signup_verification_subject",
]

#: The product's name. Re-signed from 미주알 by operator decision (D23,
#: `intent.md` 2026-09-02): the retired name appears nowhere.
PRODUCT_NAME = "주주의관제탑"

#: 제목 — **signed** (R5 build-prompt § 알림: ``"[미주알] {종목} — {마감명} D-{n}
#: ({date})"``), with the bracketed name re-signed per D23. ``dday`` is the
#: served label rather than ``D-{n}``, which is the same string on every day but
#: 당일: the board says ``D-DAY`` there and so must the mail.
DEADLINE_SUBJECT_TEMPLATE = "[{product}] {corp_name} — {label_ko} {dday} ({date})"

#: 사실 블록 labels — **drafted P4.S2** (R5 names the four facts —「마감 mono D-표기
#: · 기간 · 보유 N주 기준 주수 · 발행가 상태」— but not the words that label them).
LABEL_DEADLINE = "마감"
LABEL_WINDOW = "기간"
LABEL_HOLDING = "보유"
LABEL_PRICE = "발행가"

#: 발행가 상태 — **drafted P4.S2**. A *state*, never a figure: 확정발행가 전 금액
#: 금지 applies to the mail identically (R5 § 알림, and `security` § 확정발행가).
PRICE_CONFIRMED = "확정"
PRICE_PENDING = "확정 전"
PRICE_PENDING_WITH_DATE = "확정 전 (확정 예정일 {final_price_date})"

#: 보기 링크 — **signed** as 「미주알에서 보기 →」 (R5 build-prompt § 알림), the
#: name re-signed per D23.
VIEW_LINK_LABEL = "{product}에서 보기 →"

#: 푸터 — the 출처 half is **drafted P4.S2** (R5 requires 「rcept_no 출처」 and
#: fixes no wording); the 해지 sentence is **signed verbatim** (R5 round record
#: § *Proposed copy → Notify*).
FOOTER_SOURCE = "출처: 공시 접수번호 {rcept_no}"
FOOTER_UNSUBSCRIBE = (
    "이 메일은 회원님이 설정한 마감 알림입니다 — 알림 설정에서 끌 수 있습니다."
)
FOOTER_SETTINGS_LINK = "알림 설정: {settings_url}"

#: 비밀번호 재설정 메일 — **drafted P4.S2, entirely**. R5 signed only the surface
#: line 「재설정 링크를 보냈습니다 — 메일함을 확인해 주세요.」; the mail behind it was
#: never written, because P5 had no transport (`mijual.mail`'s own history). Its
#: four obligations: say what it is, carry the link, say how long it lives, and
#: tell somebody who did not ask that they may ignore it.
RESET_SUBJECT = "[{product}] 비밀번호 재설정"
RESET_INTRO = "비밀번호 재설정 링크입니다. 아래 주소를 열어 새 비밀번호를 설정해 주세요."
RESET_EXPIRY = "이 링크는 {expires_at}까지 사용할 수 있습니다."
RESET_IGNORE = "요청하지 않으셨다면 이 메일을 무시해 주세요. 비밀번호는 그대로입니다."

#: 가입 인증 메일 — **drafted P13 — approved literally at the P13 gate**, all four
#: lines. No design round wrote them (`intent.md`: the phase extends the signed
#: R5/R12 auth vocabulary and the operator approves the exact strings at the
#: gate). Its four obligations are the reset mail's, one of them changed: say
#: what it is, **carry the number itself** (there is no link in this mail — the
#: reader types the code into the panel they already have open), say how long it
#: lives, and tell somebody who did not ask that they may ignore it. The ignore
#: line states what happens if they do nothing, and it is true: an unverified
#: account cannot log in, and the address is re-takeable by a later 가입.
SIGNUP_VERIFICATION_SUBJECT = "[{product}] 가입 인증번호"
SIGNUP_VERIFICATION_INTRO = "가입 인증번호입니다. 아래 6자리 숫자를 입력해 주세요."
SIGNUP_VERIFICATION_EXPIRY = "이 번호는 {expires_at}까지 사용할 수 있습니다."
SIGNUP_VERIFICATION_IGNORE = (
    "요청하지 않으셨다면 이 메일을 무시해 주세요. 인증하지 않으면 계정은 사용되지 않습니다."
)

_RULE = "—" * 24


def _get(data: Mapping[str, str], key: str) -> str | None:
    value = data.get(key)
    text = str(value).strip() if value is not None else ""
    return text or None


def deadline_subject(data: Mapping[str, str]) -> str:
    """``[주주의관제탑] 계양전기 — 신주인수권증서 매매 마감 D-7 (2026-09-09)``."""
    return DEADLINE_SUBJECT_TEMPLATE.format(
        product=PRODUCT_NAME,
        corp_name=_get(data, "corp_name") or _get(data, "corp_code") or "",
        label_ko=_get(data, "label_ko") or "",
        dday=_get(data, "dday") or "",
        date=_get(data, "date") or "",
    )


def deadline_body(data: Mapping[str, str]) -> str:
    """사실 블록 + 보기 링크 + 푸터, as ``text/plain``.

    **Every line is omitted when its fact is absent** rather than rendered blank
    or with a placeholder — the same "absent, never null" rule the API contract
    keeps (`states-and-trust` §4). An ② row therefore has no 발행가 line at all,
    and a ① with no stored 배정비율 states the holding without converting it
    instead of inventing a share count.
    """
    lines: list[str] = []
    corp_name = _get(data, "corp_name") or _get(data, "corp_code") or ""
    label_ko = _get(data, "label_ko")
    lines.append(f"{corp_name} — {label_ko}" if label_ko else corp_name)
    lines.append("")

    dday, date = _get(data, "dday"), _get(data, "date")
    if dday and date:
        lines.append(f"{LABEL_DEADLINE}: {dday} ({date})")
    elif date:
        lines.append(f"{LABEL_DEADLINE}: {date}")

    start, end = _get(data, "window_start"), _get(data, "window_end")
    if start and end:
        lines.append(f"{LABEL_WINDOW}: {start} ~ {end}")
    elif start or end:
        lines.append(f"{LABEL_WINDOW}: {start or end}")

    shares, allotted = _get(data, "shares"), _get(data, "allotted_shares")
    if shares and allotted:
        # R5's 「보유 N주 기준 주수」 — ① only; ② and ③ have no share conversion.
        lines.append(f"{LABEL_HOLDING}: {shares}주 기준 {allotted}주")
    elif shares:
        lines.append(f"{LABEL_HOLDING}: {shares}주")

    price_state = _get(data, "price_state")
    final_price_date = _get(data, "final_price_date")
    if price_state == "confirmed":
        lines.append(f"{LABEL_PRICE}: {PRICE_CONFIRMED}")
    elif price_state == "pending":
        lines.append(
            f"{LABEL_PRICE}: "
            + (
                PRICE_PENDING_WITH_DATE.format(final_price_date=final_price_date)
                if final_price_date
                else PRICE_PENDING
            )
        )

    event_url = _get(data, "event_url")
    if event_url:
        lines.extend(["", VIEW_LINK_LABEL.format(product=PRODUCT_NAME), event_url])

    lines.extend(["", _RULE])
    rcept_no = _get(data, "rcept_no")
    if rcept_no:
        lines.append(FOOTER_SOURCE.format(rcept_no=rcept_no))
    lines.append(FOOTER_UNSUBSCRIBE)
    settings_url = _get(data, "settings_url")
    if settings_url:
        lines.append(FOOTER_SETTINGS_LINK.format(settings_url=settings_url))
    return "\n".join(lines) + "\n"


def password_reset_subject(data: Mapping[str, str] | None = None) -> str:
    return RESET_SUBJECT.format(product=PRODUCT_NAME)


def password_reset_body(data: Mapping[str, str]) -> str:
    """The link, its validity in KST, and permission to ignore it."""
    lines = [RESET_INTRO, ""]
    url = _get(data, "url")
    if url:
        lines.extend([url, ""])
    expires_at = _get(data, "expires_at")
    if expires_at:
        lines.append(RESET_EXPIRY.format(expires_at=kst_stamp(expires_at)))
    lines.append(RESET_IGNORE)
    return "\n".join(lines) + "\n"


def signup_verification_subject(data: Mapping[str, str] | None = None) -> str:
    return SIGNUP_VERIFICATION_SUBJECT.format(product=PRODUCT_NAME)


def signup_verification_body(data: Mapping[str, str]) -> str:
    """The 6-digit code on its own line, its validity in KST, and permission to ignore.

    The code is given a line of its own with nothing else on it because that is
    the line the reader copies or reads aloud to themselves while typing. It is a
    **string** everywhere — ``mijual.web.auth.new_code`` keeps the leading zeros
    — so it is never reformatted here, spaced, or grouped: 「012345」 must arrive
    as the six characters the panel will compare.
    """
    lines = [SIGNUP_VERIFICATION_INTRO, ""]
    code = _get(data, "code")
    if code:
        lines.extend([code, ""])
    expires_at = _get(data, "expires_at")
    if expires_at:
        lines.append(SIGNUP_VERIFICATION_EXPIRY.format(expires_at=kst_stamp(expires_at)))
    lines.append(SIGNUP_VERIFICATION_IGNORE)
    return "\n".join(lines) + "\n"


def kst_stamp(value: str) -> str:
    """``2026-09-02T15:04:05+09:00`` → ``2026-09-02 15:04 (KST)``.

    The API emits absolute KST instants with a literal ``+09:00``
    (:mod:`mijual.web.clock`), which is right for a browser that *diffs* them and
    wrong for a sentence a person reads. A value this cannot parse is passed
    through unchanged rather than dropped: an ugly timestamp is a smaller failure
    than a reset mail that does not say when its link dies.
    """
    try:
        moment = datetime.fromisoformat(value)
    except ValueError:
        return value
    return moment.strftime("%Y-%m-%d %H:%M (KST)")
