# UI traps

Five ways to render this data wrongly. Each one is a real property of the corpus, each is easy to trip
over while designing, and each has a sample in [`samples/`](samples/) to check against.

---

## 1. `option_schedule` dates are not a period

**Trap:** `option_schedule.options[].start_date` / `end_date` look like a window, so they get rendered
as `2028-04-24 ~ 2030-07-24` — or worse, as a progress bar.

**Truth:** those two dates bracket a **recurring claim right**, not a continuous one. 대동기어's 풋 says
*발행일로부터 30개월이 되는 날인 2028년 04월 24일 및 이후 **매 3개월에 해당하는 날***: the holder may
claim on quarterly dates inside the bracket, not on any day of it. Some filings instead enumerate
numbered 청구기간 (`1차 청구기간 2028-08-25 ~ 2028-09-24 … 8차 …`).

**Rule:** the stored value carries **no `date_basis` marker**, so the two dates alone cannot tell you
which convention a given filing used. Render the `detail` string (which states the convention in the
filer's own words), or design an explicit basis marker and have the apply phase populate it. **Do not
render the pair as a plain 기간.** See `samples/r2-option-schedule.json`.

---

## 2. `발행사 기재 불일치` is the answer, not a bug to fix

**Trap:** two numbers for the same quantity — the issuer's stated 실권주 and the one its own table
implies — look like a parsing failure, so the UI picks one, averages them, or hides the conflict.

**Truth:** in five 증권발행실적보고서 the issuer's own cell disagrees with the issuer's own Ⅶ table.
대한광통신 states 실권주 **2,117,937** while 발행 23,465,365 − 청약 21,382,063 = **2,083,302**. Both are
cited with spans into the same document. It is an **issuer table error**, and the product's total uses
발행 − 청약 because 단수주 was never issued as a 증서 at all.

**Rule:** the exposed contract is the literal string **"발행사 기재 불일치"**. Show that the issuer's
filing contradicts itself, never silently reconcile it — and do not phrase it so the user thinks 미주알
made the mistake. See `samples/r1-lapse-mismatch.json`.

---

## 3. `corp_name` is a display value, and it can disagree with the filing

**Trap:** the card shows the master `corp_name`, the user taps through to the 원문, and the document
header says a different company.

**Truth:** `rcept_no 20250930000508` stores `corp_name` **풍전약품** while its 본문 header reads
**에스씨엠생명과학 주식회사**. It is a DART master-data artifact and affects **display only** — the
전환가액, the 오버행, and the 전환청구기간 are all correct. (Note that the ordinary case is *not* a
mismatch: the filing simply prints the legal-form suffix, `한화솔루션(주)` vs `한화솔루션`.)

**Rule:** decide deliberately what identity a card shows — master name, 본문 name, ticker, or a pair —
and make the transition to the 원문 survive the case where they differ. See
`samples/r2-corpname-trap.json`.

---

## 4. 추후결정 means *no date*, not *unknown date*

**Trap:** a schedule field with no date reads as missing data, so the UI fills the slot: the previous
date greyed out, "미정 (예상 9월)", a dash where the countdown was, a skeleton that never resolves.

**Truth:** `gate_status: tbd` carries `display: 추후결정` and **`value: null`**. The superseded date is
not withheld — it is structurally absent from the contract and cannot leak. The event is otherwise
perfectly live: 경남제약's 초과청약 비율 and 발행가 산식 render normally beside it.

**Rule:** 추후결정 is a complete, intentional state. Render it as an answer, never as an absence, and
never show a date next to it. See `samples/r1-tbd-schedule.json`.

---

## 5. "지남" does not mean the same thing in every rights type

**Trap:** one board component sorts by key date and labels everything behind today as "종료" or
"마감", so a live ② is filed under "지난 일".

**Truth:** the three countdowns run in different directions.

| | key date | a date in the past means |
|---|---|---|
| ① | 신주인수권증서 매매 마감 | the right **has lapsed** — history |
| ② | 전환청구 **개시**일 | the window is **already open** — the dilution is live right now |
| ③ | 반대의사 통지 마감 | the deadline **has passed** — history |

On the measurement date, 56 of the 422 exposable ② events have an opening date behind us. Calling them
"종료" would be exactly backwards.

**Rule:** the board's time language is per rights type. Whether past ① and ③ events appear at all — and
how a live-but-already-open ② is phrased — is a design question for R2, but it must be answered
per type. See `board-snapshot.md` §Urgency distribution.
