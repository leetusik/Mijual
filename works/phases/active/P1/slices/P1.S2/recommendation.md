# MVP 권리 3종 — scope recommendation package (P1.S2)

| | |
|---|---|
| Produced by | `P1.S2`, 2026-08-19 |
| Inputs | `P1.S1` field matrix (`docs/reference/dart/field-matrix.md`), `P1.S3` recon (F17–F23), phase `intent.md` |
| New measurement done here | a **judging-week live-event scan** (2026-09-07 → 09-11) over the 1,002-request spike cache — read-only, no new API calls, key untouched |
| Status | **recommendation only.** Nothing is decided. The operator decides; this slice stops on `needs_operator`. |

Evidence rules from the phase constraints hold: every fact carries an `rcept_no` or a command; every estimate is marked `▷`; nothing is rounded up.

---

## 0. TL;DR — the recommended package

**Keep all three types. Cut depth, not breadth — with two named exclusions and one hard condition.**

| | recommendation | one-line reason |
|---|---|---|
| **① 유증 신주인수권** | **KEEP — make it the hero** | The only type whose MVP genuinely needs the AI-reading layer, the only killer user story, and — measured — it has live events inside the judging window. |
| **② CB 오버행** | **KEEP, with a condition** | Largest universe (263 reports) and the board's density, but **0 of 267 cached 2026 CB events have a 전환청구 개시일 before 2027**. Without a ≥12-month backfill it is a 2027 calendar with no urgency. |
| **② EB (교환사채)** | **DEMOTE out of MVP** | 20 events all year; its 정정 are mostly free-text; keeping the field mapping costs nothing, shipping it buys nothing. |
| **③ 매수청구권 (합병)** | **KEEP** | The plan feared zero live events at judging time. **Measured: 4 live + ~4 imminent.** Near-total structured coverage and it rides ②'s rails. |
| **③ siblings (분할합병·주식교환)** | **DEMOTE out of MVP** | Same field shape, ~doubles the universe — but it is a P2 scope-sizing win, not a 19-day win. Already a candidate deferred job. |
| **① 제3자배정 유증 (252 reports)** | **EXCLUDE by filter** | 84% of all 유상증자 filings, and **none** of them issue a 신주인수권증서. Publishing them would fill the board with non-rights events. |

**One extra recommendation that is not about scope but is decision-grade:** the board must render from **persisted snapshots, never a live OpenDART call in the request path** — see §4. This is a `결격` (F19) risk control, not polish.

---

## 1. The judging-week test (new measurement)

The plan asked one sharp question — *will anything actually be live on the board during 9/7–9/11, when the judge opens the URL unattended?* This was measured, not assumed.

**Method.** Read-only scan of the `P1.S1` response cache (`scripts/spike/samples/`, 1,002 cached requests, filings 2026-01-01 → 08-18, KOSPI+KOSDAQ). No new API calls; the key was never read into any output. Every date field of `piicDecsn` / `estkRs` / `cvbdIsDecsn` / `exbdIsDecsn` / `cmpMgDecsn` / `stkExtrDecsn` plus every cached 본문 ZIP was parsed and tested against the window `20260907 ≤ d ≤ 20260911`.

### 1.1 What a judge would see on, say, Wednesday 2026-09-09

Everything in the **verified** block is already on the public record as of 2026-08-18 — no new filing has to arrive for the board to be full.

**① 유증 — verified from 본문 (authoritative, 정정-후 values):**

| 종목 | live/upcoming item on 9/9 | evidence |
|---|---|---|
| **휴림에이텍** | **신주배정기준일 = 2026-09-09 — D-0, inside the window.** 주주명부폐쇄 9/10~9/14 also inside. 신주인수권증서 상장·매매기간 **9/30 ~ 10/07** → counts down at D-21 all week. 구주주 청약 10/19~10/20. | `20260804000486` 본문 |
| **이렘** | **신주인수권증서 상장·매매기간 = 2026-09-21 ~ 09-29 → D-12 on 9/9**, ticking down through the whole window. 구주주 청약 10/12~10/13. 주주명부폐쇄 9/3~**9/7**. | `20260811000481` 본문 |

Both are also **live 정정 stories**, which is exactly what the product exists for:
- 이렘 `20260811000481` 정정사항: 신주배정기준일 **8/13 → 9/2**, 청약 **9/17~9/18 → 10/12~10/13**, 증서 매매기간 **9/2~9/8 → 9/21~9/29**. A holder who acted on the original would have been ~19 days early.
- 휴림에이텍 `20260804000486` 정정사항: 신주배정기준일 **9/3 → 9/9**, 청약 **10/13~10/14 → 10/19~10/20**, 증서 매매기간 **9/22~9/30 → 9/30~10/07**.

**① 유증 — ▷ indicative only (from `estkRs`, which F11 proved version-stale):** four more 주주배정-계열 events show 구주주 청약기일 inside the window — 엔젠바이오 (`rpt_rcpn 20260716000637`) 9/9~9/10, 상지건설 (`20260724000278`) 9/9~9/10, HLB제약 (`20260803000211`) 9/10~9/11, 한울반도체 (`20260716000775`) 9/10~9/11 — and four more have 신주배정기준일 in early September (SK디앤디 9/2, 에코프로비엠 9/4, 엘앤씨바이오 9/4, 아이에이 9/16), which puts their 증서 매매기간 in late 9월~10월, i.e. **counting down during the window**. These are marked ▷ because `estkRs` carries the schedule as of the 신고서 filing: 휴림에이텍's `estkRs` still says 청약 9/4~9/7 while its current 본문 says 10/19~10/20. *(That gap is itself the product's pitch, and it is a P2 rule: the 주요사항보고서 본문 is the schedule's source of truth, not the 증권신고서.)*

**② CB — dense but slow:**
- **264 of 267** cached CB events have a 전환청구 개시일 after 9/11 → 264 countdowns on the board.
- But the **earliest is 2027-01-15** (`20260107000643` 빛과전자). **Zero** cached 2026-filed CB has a 전환청구 개시일 in calendar 2026; only 62 land within six months of the window.
- In-window near-term items are thin: 인콘 `20260806000441` 청약·납입 9/10, 이오플로우 `20260818000256` 청약 9/9·납입 9/9, 캔버스엔 `20260819000347` / `…343` 납입 9/9.
- **→ ② supplies volume and a 오버행 캘린더, not urgency — unless P2 backfills.** A CB issued around 2025-09 has its 전환청구 개시일 around 2026-09, i.e. live during judging week; our sample frame simply starts at 2026-01-01.

**③ 매수청구권 — the plan's pessimism was wrong:**

| 종목 | live item during 9/7–9/11 | 매수 예정가격 | evidence |
|---|---|---|---|
| **휴맥스홀딩스** | 매수청구 **행사기간 8/28 ~ 9/17** — open all week, D-6 on 9/11 | 6,839원 | `20260811000452` |
| **휴맥스** | 매수청구 **행사기간 8/28 ~ 9/17** — open all week | 6,591원 | `20260811000467` |
| **에코볼트** | **반대의사 통지 접수 9/8 ~ 9/22 — opens inside the window**; 매수청구 행사 9/23~10/14 | 1,968원 | `20260804000288` |
| **알에프텍** | **반대의사 통지 접수 9/8 ~ 9/22 — opens inside the window**; 매수청구 행사 9/23~10/14 | 9,325원 | `20260804000294` |

Imminent right behind them: 모다이노칩 `20260730000170` and 로젠 `20260730000215` (반대의사 접수 9/17~10/16 → D-6 on 9/11), 미래에셋비전스팩7호 `20260512000669` (9/22~), 파라택시스이더리움/코리아 `20260720000349`/`…352` (9/28~). In total **14 of the 19 매수청구권-bearing cached 합병 events still have a deadline on/after 9/7.**

And the correctness demo: **6 소규모합병 filings have a 반대의사 접수기간 overlapping the same window** — 금호석유화학 `20260810000482` (8/26~9/9), 한국카본 `20260814002642`/`…2685`/`…2795`/`…2868` (8/31~9/14), HLB글로벌 `20260807000649` (8/24~9/7) — and **none of them grants a 주식매수청구권** (F14b). A board that shows them is wrong; a board that suppresses them is demonstrably right. That is a 30-second differentiator in front of a 심사위원.

### 1.2 Verdict on the demo question

**A non-empty, countdown-active board during 9/7–9/11 is guaranteed by all three types, and each contributes something the others cannot:**

- ① supplies the **D-0 drama** (휴림에이텍 배정기준일 lands on 9/9) and the **killer countdown** (이렘 증서 매매 D-12).
- ② supplies **density** (264 cards) and the only "portfolio-scale" view.
- ③ supplies **money-on-the-table specificity** (휴맥스 6,839원, D-6) and the **negative-filter correctness demo**.

Nothing here depends on a filing arriving after 2026-08-18. The demo can be rehearsed today and will still be true on 9/9.

---

## 2. Per rights type — the full call

### ① 유상증자 신주인수권 — **KEEP, and lead with it**

- **Universe (measured):** 299 유상증자결정 reports in 2026-01-01~08-18, of which **32 (11%)** are 주주배정 계열 → ▷ ~4–5/month. The remaining 252 제3자배정 + 14 일반공모 issue no 증서 and must be filtered out. ▷ Open filter question for P2: the 1 `주주우선공모증자` (상지건설 `20260807000339`) is *probably* 증서 미발행 and should likely be excluded too — unverified, so P2 must check the 본문 `18. 신주인수권양도여부` rather than trust `ic_mthn`.
- **Structured / LLM split:** thin API (`piicDecsn` = 19 keys, no dates, no prices) but a **~6,000-character 본문 with 10/10 numbered labels present in 9/9 filings**. Deterministic skeleton; **~5 prose fields**, of which exactly one is service-critical — 신주인수권증서 상장·매매기간 (recovered from prose 8/9).
- **Demo strength: highest.** "당신의 권리를 팔 수 있는 마지막 날" with a real D-day is the whole product in one card, and §1.1 proves it will be live.
- **Build cost in the remaining ~19 days: the largest of the three, and still bounded.** It is the only type that requires the 본문 fetch + label parse + LLM extraction + 결정론 게이트 path. But the volume is tiny — **32 events in 7.5 months ⇒ ~32 one-shot LLM calls over the whole backfill**, on 6k-character documents. Cost is a rounding error; the work is the code path, not the inference.
- **Why demoting it would be a mistake even though it is the most expensive:** it is the only type whose MVP *needs* the §3.6 AI-reading layer at all (see ② and ③ below — both ship fine with zero extraction). 첨부1 §5 asks explicitly what role the 생성형 AI 모델 performs (F18). Drop ①, and the honest answer shrinks to "요약을 씁니다".

### ② CB 오버행 — **KEEP, conditional on a backfill; EB out**

- **Universe (measured):** CB **263 reports / 236 corps**; EB 20 reports / 20 corps. By far the largest.
- **Structured / LLM split: excellent.** 전환가액, 전환비율, 전환청구기간, 오버행 주식수·비율 all **47/47**; 리픽싱 floor 36/47. The 🔴 prose fields (콜·풋 세부, 리픽싱 산식, 보호예수) are **all droppable from the MVP** — none is needed to render an 오버행 카드 with a countdown. **② can ship with zero LLM extraction.**
- **Demo strength: density, not urgency.** 264 live countdowns, earliest 2027-01-15.
- **The condition, stated precisely:** for ② to show any *urgent* 오버행 event during judging week, P2 must backfill CB filings back to at least **2025-06**, because 전환청구 개시일 sits ~1 year after 납입. ▷ Cost estimate: `list.json` at 3-month windows (F6) plus one `cvbdIsDecsn` call per corp per window ≈ **300–600 additional requests** on the already-proven code path — well inside the ~1,000-request session S1 already sustained without a quota error (F15). ▷ Roughly half a day. **If the operator will not fund that half-day, ② should be demoted to a static "오버행 캘린더" tab rather than a countdown source, because a board whose nearest deadline is 500 days away is not a 관제 현황판.**
- **EB — demote.** 20 events all year; 31 of 52 정정 항목 in the EB sample were free-text 기타 투자판단 blocks; and one of the ten sampled EB corrections was a full **발행결정 철회** (`20260306001019` 위닉스), meaning EB needs an event-invalidation path that nothing else needs. Keep the field mapping in the matrix, ship the code later.

### ③ 매수청구권 — **KEEP** (the plan's demotion candidate survives on measurement)

- **Universe (measured):** 83 회사합병 reports, but **65 are 소규모합병** → **15–17 real events** in 7.5 months → ▷ ~2/month. Smallest by far.
- **Structured / LLM split: near-total.** 반대의사 통지 접수기간 **41/41**, 주주확정기준일 41/41, 합병일정 41/41, 매수 예정가격 15/83 and 행사기간 17/83 (the low fill is *semantic* — 소규모합병 grants no right). Only 반대의사 통지 **방법·절차** is prose, and the **기한** — the part a countdown needs — is structured. **③ can also ship with zero LLM extraction.**
- **Demo strength: much better than feared.** §1.1: 4 live events inside the window, 14 of 19 with a deadline on/after 9/7, plus the 소규모합병 suppression demo.
- **Build cost: the lowest.** One endpoint on the same rails as ②, plus one filter rule (`mg_stn != 소규모합병` **and** `aprskh_*` present — use both, per F14b). ▷ Under a day once ②'s pipeline exists.
- **Keep the siblings out.** `cmpDvmgDecsn` / `stkExtrDecsn` carry the same field shape (`20260522000296`) and would roughly double ③'s universe cheaply — but "cheap" is relative to a 19-day budget with P2, P3 and P4 unbuilt. Record as deferred.

---

## 3. Alternatives — what each would cost and gain

| package | gain | cost / what breaks |
|---|---|---|
| **A. ① + ② (CB, backfilled) + ③ — RECOMMENDED** | Full board: D-0 drama, 264-card density, money-specific 매수청구 cards, and a correctness demo. Every §3.6 layer exercised. | The widest surface. Requires the ② backfill and the ① LLM path to both land. Mitigation: ② and ③ ship with zero LLM, so ① failing degrades the board rather than emptying it. |
| **B. ② only** (max volume, min risk) | Smallest build; zero LLM; hardest to get wrong. | No killer story, no urgency (earliest countdown 2027-01-15), and 첨부1 §5's "생성형 AI 역할" question has almost no answer. Judged on 구현 완성도 this may look complete and pointless at once. **Not recommended.** |
| **C. ① + ③ (drop ②)** | Sharpest story; every card is urgent and human. Zero backfill work. | Board density collapses to ▷ ~10 live cards. "관제 현황판" becomes "알림 목록". Loses the only portfolio-scale view. Saves ▷ ~1 day. |
| **D. ① + ② (drop ③)** | Marginally simpler. | Saves ▷ well under a day, loses 4 live in-window events, the most money-specific card type, and the suppression demo. **Worst trade on the table.** |
| **E. all three + EB + 분할합병·주식교환** | ~2× the ③ universe, complete coverage. | Adds an event-invalidation path (EB 철회) and two more endpoints in the last third of the schedule. **Not recommended at D-19.** |

If the operator wants a single lever to pull under time pressure, the **drop order is: EB → 분할합병·주식교환 (already out) → ②'s backfill (degrade ② to a calendar) → ③ → ②**. ① is the last thing to drop, not the first.

---

## 4. One non-scope recommendation the scope decision depends on

F19 makes 9/7 11:00 → 9/11 23:59 a **결격** window: if the URL is unreachable, the entry is disqualified — and F15 measured **transient HTTP 503 from OpenDART** under sustained calling. Therefore:

**The board must render from persisted snapshots. No OpenDART call may sit in the request path.** A live-fetch design would turn an upstream 503 during an unattended judging week into an empty or erroring board. This also makes §1.1's guarantee real: the events listed there are already collected, so the board stays correct even if collection stops entirely on 9/6.

Corollary for P2, already implied by F11 but now load-bearing for the demo: snapshot **every version** of each event and key by `(corp_code, subtype, original_rcept_dt)` — the 이렘 / 휴림에이텍 정정 stories in §1.1 only exist if the superseded version was captured.

---

## 5. Operator round-trip — the question set

Five questions, one round-trip. Items 2–5 are `P1.S3`'s prepared bullets, relayed as written.

### Q1 — Rights scope (the actual gate)

> **Recommendation: keep all three — ① 유증 신주인수권 (hero) + ② CB 오버행 + ③ 매수청구권 — with EB and 분할합병·주식교환 out of the MVP, 제3자배정 유증 filtered out, and ②'s CB backfill (▷ ~half a day) funded.**
>
> The matrix did not demote anything: ① turned out mixed rather than LLM-heavy (deterministic skeleton + ~5 prose fields, only 32 events/year), and ② and ③ can both ship with **zero** LLM extraction. Measured judging-week check: **휴림에이텍 신주배정기준일 falls on 9/9**, **이렘 신주인수권증서 매매 opens 9/21 (D-12 during the window)**, **휴맥스·휴맥스홀딩스 매수청구 마감 9/17**, **에코볼트·알에프텍 반대의사 접수 opens 9/8** — all already on the public record, so the demo board is guaranteed non-empty.
>
> **Answer one of:** (a) approve the recommended package; (b) approve but cut something specific (the drop order is EB → ②의 backfill → ③ → ②; ① last); (c) a different package from §3.

### Q2 — Domain: decide before deploy freeze, not before 9/7

> The challenge only requires "실행 가능한 링크", so a platform hostname (Vercel/Fly/…) is legal. But the submitted URL is **frozen at submission** ("제출한 URL만 인정됩니다") and must stay reachable 9/7 11:00 → 9/11 23:59 or we are **결격** — so if you want a branded URL, it must be bought and wired *before* P4 freezes the deployment.
>
> - **`mijual.ai`** — AVAILABLE (verified `whois.nic.ai` → `Domain not found`). ~**$82.70/yr**, but **.ai has a 2-year minimum term** → **~$165 upfront** (▷ exact checkout total unverified; no purchase was made). Best fit for the pitch: an AI-challenge entry on a `.ai` domain.
> - **`mijual.kr`** — AVAILABLE. **22,000원/yr + VAT** (도레지; ▷ 가비아·후이즈 comparable). ~1/8 the cost, and arguably the better fit for a Korean-only retail-investor product.
> - **`mijual.co.kr`** — also AVAILABLE (not previously checked), same price tier.
> - **`mijual.io`** — also AVAILABLE (not previously checked), if you want a third option.
> - **`mijual.com`** — **strike it from the list.** It is registered *and actively in use* (it forwards to `https://blog.naver.com/tou2me`). Its registration expires 2026-08-28, but under the ICANN lifecycle (up to 45d grace → 30d redemption → 5d pendingDelete) its earliest possible drop is **2026-10-02** — 25 days after the deadline. Waiting on it is not an option, and the owner looks like a renewer.
> - **Buying is yours alone** — I made no purchase and created no account. If you want both `.ai` and `.kr`, that is ~$165 + ~24,000원.

### Q3 — Registration: do this now, not on 9/7

> 참가 신청 **closes 2026-09-07 10:00 KST, the same instant as the submission deadline**, and it requires a **`dacon.io` account** (one account only; no dual registration). Solo entry carries **no penalty**: no separate track, no handicap, and the '팀으로 전환' step simply does not apply. Any account or verification hiccup at T-0 would be fatal.

### Q4 — Schedule: three flags against your 9/1 availability (flags only — this is yours to weigh)

> - **The decisive build week is the week a job could start.** Submission is **9/7 (월) 10:00** — so 9/6 (일) is the last full working day and there is no morning-of buffer. Your 입사 가능일 is 9/1. That week is roughly the last third of the 2~3 weeks of real capacity in the handoff.
> - **9/7 11:00 → 9/11 (금) 23:59 is a five-business-day unattended uptime window, and failing it is 결격, not a deduction.** If you are at a new job that week, the service has to hold up on `ssh h` without you watching it.
> - **10/13 (화) 10:00–16:00 is an offline PT** (15min + 5min Q&A), *if* we make the ~11-team cut announced 9/22. That is a weekday of leave ~6 weeks into a new job, and solo means no one can attend in your place (DACON confirmed no 대리인 for the 시상식). ▷ Venue is unannounced, so travel cost is unknown.
> - Contrast: **9/23 → 10/8** (발표자료 PDF + 소스 ZIP) is a 2-week packaging window that evenings and weekends can absorb even if employed.
> - Not for me to weigh: the goal is 재취업, and 입상 confers 금융보안원 입사 지원 우대 — so starting early protects the goal but threatens the instrument, and vice versa.

### Q5 — Two rules that change what we build (no decision needed, just confirm you saw them)

> - **Web only.** A mobile app or an app-download page is explicitly rejected; a **mobile-first responsive web service is explicitly accepted**.
> - **Commercial LLM APIs (GPT etc.) are explicitly allowed**, at our own cost — the §3.6 architecture is unblocked. Dummy data is also allowed if disclosed, which means running on **real DART filings is a differentiator we get for free**.

---

## 6. Method, and what is *not* established here

- The judging-week scan reads **only** the on-disk cache from `P1.S1`; it made no network call and never touched the API key. Scripts lived in session scratch space and are not committed — the numbers are reproducible from the cache plus `python3 scripts/spike/survey.py population`.
- **The scan's frame is the spike's frame**: KOSPI+KOSDAQ, filings 2026-01-01 → 08-18. Events filed **after 2026-08-18** are not in it, so §1.1 is a *floor*, not a forecast — ▷ another ~4–5 주주배정 유증, ~35 CB and ~2 real 합병 will be filed before 9/7 on the measured monthly rates.
- **`estkRs`-derived schedules are version-stale** (F11), so every ①-schedule claim not backed by a 본문 read is marked ▷. The two 본문-verified events (이렘, 휴림에이텍) are facts.
- ▷ Minor, non-material: the date scan saw 306 distinct `piicDecsn` rows / 34 주주배정-계열 rows in the cache against the `population` census's 299 / 32, because the cache also holds rows fetched under overlapping windows and superseded `rcept_no` values. The census numbers in the matrix are the ones to quote.
- **Not established here:** whether `주주우선공모증자` issues a 증서; the OpenDART daily quota (still unmeasured, F15); the real cost of the ② backfill beyond a ▷ request-count estimate; anything about the operator's employment decision, which is stated as a flag and nothing more.
