# Result — P1.S3: Recon (daker.ai submission requirements + mijual domain availability)

**Status: done.** Q5 and Q6 are both answered with sourced facts. All work was read-only
against the outside world: no account created, no form submitted, nothing purchased.

## What this slice produced

- **Findings `F17`–`F23` in `phase.md`** — the durable record. F17/F18/F21 answer Q5
  (solo rules, deliverables + no video, the timeline vs the operator's constraints), F22
  answers Q6 (domain fact sheet), F19 isolates the two 결격 clauses, F20 covers the
  게시판 amendments check, F23 states the gaps honestly.
- **Two doc-impact notes** appended (`operations`, `decisions`) — for `P1.REVIEW` to consolidate.
- **`docs/reference/challenge/submission/`** — the two mandatory `.hwpx` 양식 committed with
  a `README.md` carrying source URLs, SHA-256, a stdlib snippet for reading `.hwpx`, and the
  **full required section structure extracted verbatim** from both templates.

## Verification of the advisory brief

The orchestrator's probe checked out on every claim I could test. Confirmed as-is:
the three-stage deliverable set and its deadlines, the 9/7 11:00–9/11 23:59 uptime 결격
clause, no video, team 1–4인 with no dual registration, judging = 100% internal review →
~11 teams → 10/13 offline PT 15min + Q&A 5min PDF-only, the 5-year non-exclusive
winner licence with the two reuse bans, no dataset provided, and all three whois results.

Where I found **more or different** than the advisory:

1. **The `stages` array gave the exact dates the prose omits** — 발표 심사 대상 명단 발표
   **2026-09-22 10:00**, 최종 산출물 window **09-23 → 10-08 23:59**, 발표 심사
   **10-13 10:00–16:00**, 최종 결과 **10-23**. Every weekday cross-checks against the
   Korean prose. The advisory's "~late Sep 본선" is now a precise 9/7→9/22 internal window.
2. **참가 신청 closes at 2026-09-07 10:00 — the same instant as submission** (advisory
   didn't surface this). Registering is a real gate, not a day-of formality.
3. **The form schema settles the video question structurally**, not just by absence:
   the MVP stage's `linkConfig` is `{demo: required, github: disabled, youtube: disabled}`.
4. **The MVP stage sets `pdfConfig.required: false`** even though the rules require the
   기능명세서 PDF — the platform will not stop you from submitting incomplete, and a
   missing 제출물 is 결격. Recorded in F19.
5. **A second 결격-grade clause the advisory missed**: DACON.GM, 2026-08-19 —
   "배포 URL은 최종 제출 이후 변경된다면 불이익이 발생할 수 있습니다. (제출한 URL만 인정됩니다)".
   The URL is frozen at submission, which is what makes the domain decision time-critical.
6. **`.ai` requires a 2-year minimum term** — so ~$165 upfront, not "$70–90/yr". The
   advisory's per-year framing understated the commitment by ~2x.
7. **`mijual.com` is not a lapsing parked domain** — it actively forwards to
   `https://blog.naver.com/tou2me`. And the ICANN lifecycle makes its earliest possible
   drop **2026-10-02**, 25 days *after* the deadline. The "expiry watch" option is dead;
   I removed it from the decision rather than leaving it as an uncertainty.

## Gap-fills the plan asked for

- **게시판/공지 amendments check → no amendments.** The board is fully public and
  unauthenticated. `counts` = `{all: 27, notice: 0, general: 27}` — **zero official
  notices have ever been posted**, so nothing has amended the rules. Official answers
  exist only as `DACON.GM` comments on participant threads; I read all 8 genuine Q&A
  threads and their replies (the other 19 posts are auto-generated "요약: …" marketing
  content with no authority). Six answers bind or unblock us — see F20; the two that
  matter most are that **commercial LLM APIs are explicitly allowed** and that the
  service must be **web-only, though mobile-first responsive is explicitly fine**.
  Caveat recorded: the brief is edited in place with no changelog (`updatedAt`
  2026-08-18), so re-reading it before 9/7 is a P4 task.
- **Templates downloaded and readable.** `.hwpx` turned out to be a ZIP of OWPML XML, so
  I extracted the structure with the stdlib — no Hangul needed, and no honest "unreadable
  in this environment" caveat required. 기획서 = 7 sections (1–6 필수);
  기능명세서 = 5 sections (all 필수). Two items bind **P3**, not just P4: §2 wants a
  `관련 화면` per feature and §5 wants a judge-executable verification script with
  테스트 계정 / 샘플 입력값 / 예상 결과 — the service must be verifiable by a stranger,
  unattended, from the URL alone.
- **Schedule-conflict layout (Q5)** — the full table is F21. One sharp conflict (the
  decisive 09-01→09-07 build week is exactly the week employment could start, ending at
  a Monday *morning* deadline with no buffer), one 결격 risk that overlaps it (5 business
  days of unattended uptime on `ssh h`), one contingent conflict (10-13 is a weekday
  offline PT, ~6 weeks into a new job, and solo means nobody can stand in), and one
  low-friction stretch (09-23→10-08 packaging). The strategic tension — 재취업 is the
  goal, and 입상 confers 금융보안원 입사 지원 우대 — is stated, not resolved: it is the
  operator's call in S2.
- **Domain fact sheet (Q6)** — F22. All whois run directly against the registries
  (`whois.nic.ai`, `whois.kr`, `whois.verisign-grs.com`, `whois.nic.io`); the default
  `whois` on this machine only returns the IANA TLD record, so `-h <registry>` was
  required. `.co.kr` and `.io` checked as bonus options; both available.

## The operator-facing bullet list for `P1.S2` to relay

Copy this into S2's operator round-trip verbatim — it is the domain decision plus the
schedule flags, batched into the one round-trip the decomposition planned for.

> **1. Domain — decide before deploy freeze, not before 9/7.**
> The challenge only requires "실행 가능한 링크", so a platform hostname (Vercel/Fly/…)
> is legal. But the submitted URL is **frozen at submission** ("제출한 URL만 인정됩니다")
> and must stay reachable 9/7 11:00 → 9/11 23:59 or we are **결격** — so if you want a
> branded URL, it must be bought and wired *before* P4 freezes the deployment.
>
> - **`mijual.ai`** — AVAILABLE (verified `whois.nic.ai` → `Domain not found`).
>   ~**$82.70/yr**, but **.ai has a 2-year minimum term** → **~$165 upfront**
>   (▷ exact checkout total unverified; no purchase was made). Best fit for the pitch:
>   an AI-challenge entry on a `.ai` domain.
> - **`mijual.kr`** — AVAILABLE. **22,000원/yr + VAT** (도레지; ▷ 가비아·후이즈 comparable).
>   ~1/8 the cost, and arguably the better fit for a Korean-only retail-investor product.
> - **`mijual.co.kr`** — also AVAILABLE (not previously checked), same price tier.
> - **`mijual.io`** — also AVAILABLE (not previously checked), if you want a third option.
> - **`mijual.com`** — **strike it from the list.** It is registered *and actively in use*
>   (it forwards to `https://blog.naver.com/tou2me`). Its registration expires 2026-08-28,
>   but under the ICANN lifecycle (up to 45d grace → 30d redemption → 5d pendingDelete)
>   its earliest possible drop is **2026-10-02** — 25 days after the deadline. Waiting on
>   it is not an option, and the owner looks like a renewer.
> - **Buying is yours alone** — I made no purchase and created no account. If you want both
>   `.ai` and `.kr`, that is ~$165 + ~24,000원.
>
> **2. Registration — do this now, not on 9/7.**
> 참가 신청 **closes 2026-09-07 10:00 KST, the same instant as the submission deadline**,
> and it requires a **`dacon.io` account** (one account only; no dual registration).
> Solo entry carries **no penalty**: no separate track, no handicap, and the '팀으로 전환'
> step simply does not apply. Any account or verification hiccup at T-0 would be fatal.
>
> **3. Schedule — three flags against your 9/1 availability.**
> - **The decisive build week is the week a job could start.** Submission is
>   **9/7 (월) 10:00** — so 9/6 (일) is the last full working day and there is no
>   morning-of buffer. Your 입사 가능일 is 9/1. That week is roughly the last third of the
>   2~3 weeks of real capacity in the handoff.
> - **9/7 11:00 → 9/11 (금) 23:59 is a five-business-day unattended uptime window, and
>   failing it is 결격, not a deduction.** If you are at a new job that week, the service
>   has to hold up on `ssh h` without you watching it.
> - **10/13 (화) 10:00–16:00 is an offline PT** (15min + 5min Q&A), *if* we make the
>   ~11-team cut announced 9/22. That is a weekday of leave ~6 weeks into a new job, and
>   solo means no one can attend in your place (DACON confirmed no 대리인 for the 시상식).
>   ▷ Venue is unannounced, so travel cost is unknown.
> - Contrast: **9/23 → 10/8** (발표자료 PDF + 소스 ZIP) is a 2-week packaging window that
>   evenings and weekends can absorb even if employed.
> - Not for me to weigh: the goal is 재취업, and 입상 confers 금융보안원 입사 지원 우대 —
>   so starting early protects the goal but threatens the instrument, and vice versa.
>
> **4. Two rules that change what we build (no decision needed, just confirm you saw them).**
> - **Web only.** A mobile app or an app-download page is explicitly rejected; a
>   **mobile-first responsive web service is explicitly accepted**.
> - **Commercial LLM APIs (GPT etc.) are explicitly allowed**, at our own cost — the
>   §3.6 architecture is unblocked. Dummy data is also allowed if disclosed, which means
>   running on **real DART filings is a differentiator we get for free**.

## Validation

| Command / check | Outcome |
|---|---|
| `curl https://daker.ai/api/hackathons/2026-finance-ai-challenge` | PASS — HTTP 200, 52,262 B JSON; brief, rules, evaluationCriteria, consentTerms, 7 stages |
| `curl https://daker.ai/api/hackathons/<id>/posts` + `/posts/<post_id>/comments` (×8) | PASS — HTTP 200; 27 posts, `notice: 0`; all DACON.GM replies read |
| `curl -L` ×2 on the `cfiles.dacon.co.kr` 양식 URLs | PASS — HTTP 200, 47,372 B + 45,456 B, SHA-256 recorded in the folder README |
| `zipfile` + regex extraction of `Contents/section0.xml` from both `.hwpx` | PASS — 26 and 24 text paragraphs; full section structure recovered |
| `whois -h whois.nic.ai mijual.ai` | PASS — `Domain not found.` → available |
| `whois -h whois.kr mijual.kr` / `mijual.co.kr` | PASS — "등록되어 있지 않습니다" → available |
| `whois -h whois.nic.io mijual.io` | PASS — `Domain not found.` → available |
| `whois -h whois.verisign-grs.com "domain mijual.com"` | PASS — registered, expiry 2026-08-28T11:06:44Z, GoDaddy |
| `curl -L http://mijual.com` + `dig` | PASS — 200, redirects to `https://blog.naver.com/tou2me`; NS `ns75/76.domaincontrol.com` |
| Pricing: `porkbun.com/tld/ai`, Domain Name Wire 2026-02-02, `doregi.com/cs/price.php` | PASS — $82.70 w/ 2-yr minimum; wholesale $160/2yr from 2026-03-05; 22,000원/yr for .kr |
| Every recorded fact carries a source; estimates marked `▷` | PASS — sources block at the head of the F17–F23 block; `▷` used for all 9 estimates |
| Q5 and Q6 have explicit answers in `phase.md` | PASS — Q5 in F17/F18/F21, Q6 in F22; unresolved items listed explicitly in F23 |
| `python3 scripts/workflow.py validate` | PASS — `VALIDATE OK` |

## Deviations from `plan.md`

None in substance. Three things worth flagging:

1. The plan allowed recording honestly that `.hwpx` content might be unreadable here.
   It was readable, so the full template structure is recorded instead of a deferral.
   The `.hwpx` *authoring* problem still belongs to P4 and is named as such.
2. The plan scoped the domain check to `.ai` / `.kr` / `.com`. I also checked
   `mijual.co.kr` and `mijual.io` (two extra whois calls, both available) because the
   `.com` option collapsed and the operator deserves live alternatives in the same
   round-trip. No scope growth beyond those two commands.
3. The optional notes file under `docs/reference/challenge/submission/` was written
   (`README.md`) — the templates are binaries, and provenance plus the extracted section
   structure is what makes them usable to P4 without re-downloading.

Boundaries held: no purchase, no account, no registration, no form submission; no
기획서/기능명세서 content drafted; spike code and the field matrix untouched; no commits
and no status transitions.
