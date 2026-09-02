# P4.S8 — 첨부2 기능명세서

## What this slice is

Write the second mandatory 양식 document: **(첨부2) 2026 금융 AI Challenge 기능명세서** — English
body, the five Korean section headings verbatim, a Markdown source of truth beside 첨부1 and a
rendered PDF through the path `P4.S7` built. **Nothing is submitted.** Kind `docs`, risk `high`.

It was ordered after the deploy for one reason: §5 is a **judge-executable script against the live
URL**, and every claim in §1–§4 must be true of `https://jujutower.com` as it runs today. The URL is
live (`P4.S4`), SEO is on it (`P4.S5` + `P4.S6`), the smoke suite passes 17/17, and the 샘플
포트폴리오 picks live issuers per state (`P4.F1`). The deploy freeze opens 2026-09-07 11:00 KST;
after it nothing ships but a rollback, so the document describes **what is deployed now**.

## Read first

- `works/phases/active/P4/phase.md` — whole. Consume the notes tagged **for P4.S8** (from
  `P4.S2`, `P4.S7`, `P4.S4`, `P4.S5`, `P4.F1`); drop them when you finish. The `## Operator
  Questions` list is what the gate will decide — do not re-ask any of it, but §5 must not assert
  what is still undecided (the D-day demo has not been sent from production).
- `docs/reference/challenge/submission/README.md` — **the 양식's five sections, extracted
  verbatim.** Do not re-derive, do not invent a sixth.
- `docs/reference/challenge/submission/drafts/01_공모전기획서.md` — the landed 첨부1: header table,
  the "On this document" note, the `[근거]` / `▷` discipline, the 출처 목록 style, and every
  measured number 첨부2 may quote (§2, §5.1, §7.1, §7.4). 첨부2 **restates none of its argument**:
  it is the specification of what runs, not the pitch.
- `docs/current/product.md` (sections: Summary, the shipped surfaces, What P8 changed),
  `docs/current/security.md` (Secret Handling, the no-third-party property, the 비밀번호 / session
  model), `docs/current/data.md` (Storage Schema — 19 tables incl. `notification_send`),
  `docs/current/api.md` (the route list), `docs/current/qa.md` `## Regression Checklist` headings
  only. Sections, never whole docs; the `docs` command flags STALE docs — a stale doc is evidence
  to check against the notebook's Doc impact notes, not truth.
- `scripts/smoke_production.py` — the 17 checks are the measured truth of what the live URL does;
  `make smoke-prod` is the operator's own verification command and §5 may cite it.
- `frontend/lib/routes.ts`, `frontend/components/ops/routes.ts` — the 관련 화면 route map.
- `scripts/render_submission_pdf.py` — the renderer (`<in.md> <out.pdf>`; its Markdown subset:
  ATX headings, lists with one level of nesting, pipe tables, fenced code, blockquotes, hr,
  inline code/bold/italic/links; Chrome never exits after `--print-to-pdf` and the script handles
  it — do not change it).

## The 양식's required structure (all five 필수)

Header: `팀명` (주주의관제탑 — settled) and `구성원 성명` (`〈제출자 직접 기재〉 — 개인(1인) 참가`, as
첨부1). Then, headings **Korean-verbatim, body English**, product strings and 공시 terms Korean:

1. `MVP 구현 범위` — what is implemented; **미구현·향후 구현 예정 기능은 제외**.
2. `주요 기능 목록` — per working feature: **기능명 · 기능 설명 · 관련 화면 · 구현 상태**.
3. `사용자 이용 흐름` — the order a user meets the main features after opening the 배포 URL.
4. `AI 및 데이터 처리 방식` — the AI's role, the data used, input/output data, and whether
   개인정보/민감정보 are processed.
5. `MVP 검증 방법` — the procedure a **judge** follows on the deployed URL to verify each main
   feature, with **테스트 계정 · 샘플 입력값 · 예상 결과**, browser/runtime restrictions, limitations.

## What goes in each section

- **§1** — the deployed scope on 2026-09-0x at `https://jujutower.com`: the 관제 현황판 (①②③ across
  the market, D-day ranking, 소멸주의보, the 2026 lapsed-value headline), 내 종목 조회 (`/stocks`,
  `/stocks/{corp_code}`, 놓친 돈 breakdown), 이벤트 상세 (`/events/{rcept_no}`: facts with citation
  spans, DART link, 정정 history), AI 질문 (`/ask`, streamed, tool rows, citation-forced), 계정 +
  내 포트폴리오 + 챙긴 돈 (`/auth/*`, `/portfolio`), 샘플 포트폴리오 (anonymous, **four live issuers
  per state**, example 보유량), 알림 설정 + **마감 임박 이메일** (08:30 KST beat, chips 7/3/1/당일,
  no won amount in mail — 구현 완료; say "deployed and transport-proven", **not** "demonstrated",
  unless the gate demo has run by then), 비밀번호 재설정 mail, 의견 보내기, 운영 관제 `/ops`
  (implemented, operator-only, 「심사 대상 아님」). **Excluded by the 양식's own rule**: 카카오톡 알림
  (「예정」 chip only), 마이데이터, the MCP server, anything the roadmap names. Say the exclusion
  explicitly so a judge does not look for them.
- **§2** — one table or one block per feature, exactly the four columns. 관련 화면 = the route and
  the Korean surface name. 구현 상태 = 「구현 완료 · 배포됨」 for everything listed (there is no
  「부분」 row — a partial feature belongs in §1's exclusions, not here). Include the two mails as
  features with 관련 화면 = the reader's inbox + `/portfolio/notifications`.
- **§3** — one primary path a stranger takes: landing → a 종목 검색 → 이벤트 상세 → AI 질문 →
  샘플 포트폴리오 → 회원가입 → 담기 → 알림 설정 → (mail). One or two alternate entries (a shared
  `/events/{rcept_no}` link; the 소멸주의보 strip). Mobile-first: say the 390-wide phone is a
  first-class path.
- **§4** — the three-layer split from 첨부1 §5.2 in **specification** form, not pitch: reads
  (schema-driven extraction from filing prose, the fields), verifies (deterministic gates —
  arithmetic, date order, citation-span existence; a failed field is never shown), speaks (the
  agent answers only with citations; money and D-day arithmetic LLM-free). Data: OpenDART
  (`list`, the 본문 documents, the endpoints), the 19-table store, what is input (a 종목명 / 보유
  주수 / a question) and output (D-day, 배정 주수, 놓친 돈, a cited answer, a mail). **개인정보**:
  email + scrypt password hash, holdings (corp_code + shares), notification chips, the anonymous
  conversation log for AI 질문, a 챙긴 돈 mark — stored on the operator's box, never shared, deleted
  with the account (계정 삭제); no 민감정보; mails carry no won amount; the operator door is a
  separate credential with no join to reader data; no third-party origin on any page (measured).
  The 98.6 % figure may appear **only** with its D-7 cross-model caveat in the same sentence; the
  same for any 첨부1 number (name the command or the `rcept_no`).
- **§5** — **the load-bearing section.** A numbered script a judge runs in a browser, one block
  per feature: URL → action → 예상 결과 (a Korean string the surface actually shows, quoted). Sample
  inputs: a 종목명 that exists today with a live deadline (take it from the live board on the day
  you write — name the date), the 샘플 포트폴리오 (`/portfolio?sample=1`, 「오늘의 실제 공시에서 상태별로
  고른 4종목, 보유량은 예시」), one AI 질문 (a start card's own sentence), one bad `rcept_no` → the
  404 page. **테스트 계정**: primary path = **self-signup** at `/auth/login` (email + password, no
  verification mail, instant), so no credential is handed to strangers and no PII is printed;
  secondary = 「운영자가 심사용 계정을 별도 전달」, listed as an open decision for the gate (the
  agent cannot create reader accounts on production — measured in `P4.S4`; the operator can).
  Browser/runtime restrictions: modern Chrome/Safari, https only, KST dates, phone 390 and desktop
  1280 both supported, no install. Limitations, honestly: corpus refresh twice daily (07:30/19:30
  KST) so a filing from the last hours may be absent; the 발행가 확정 전 amount rule; ② fields 6–8
  by hand; the mail arrives only at 08:30 KST for chips that match; the staleness banner; Cloudflare
  in front (a 52x means the origin, not the product). Also cite `make smoke-prod` as the
  reproducible check and list what its 17 checks assert.

## Numbers and caveats

Only what the record carries, with the discipline 첨부1 set: the live board's figures on the day
you write **as a dated snapshot** (감시 중 N건 · 30일 이내 마감 N건 · 2026년 소멸 가치 ▷ N억원 — read
them off `https://jujutower.com/api/board` / the landing that day, and say the date), 19 tables,
1359 seeded events on 2026-09-02, 800 sitemap URLs (dated), 98.6 % **with** its caveat, 409 vs
418 renderable fields (name the command you quote; 첨부1 used 409). 미주알 nowhere; no
fine-tuning/PyTorch/HF framing; no users, no adoption figures.

## Output

- `docs/reference/challenge/submission/drafts/02_기능명세서.md` — the source of truth.
- `docs/reference/challenge/submission/drafts/02_기능명세서.pdf` — rendered by the S7 script,
  committed beside it.
- No product code, no `docs/current/` edit, no `frontend/` or `src/` change.

## Validation — the script must have been run once by you

- The five headings byte-identical to the README's extraction, in order, no sixth `##`.
- `grep -ci` for `미주알`, `mijual` (outside code identifiers — there should be none in prose),
  `파인튜닝`, `fine-tun`, `PyTorch`, `Hugging Face` → 0.
- Every URL in §5 answers as the script says: `curl` each (200 / 404 / 301 as written).
- **Execute §5 yourself, once, against `https://jujutower.com`** in a real browser (Chrome over
  CDP, headful via `open -na`, a fresh port and a throwaway profile; never the operator's) at
  **390 and 1280**, step by step, recording expected vs observed for each block. Self-signup with a
  throwaway address you control? — **no**: creating reader accounts on production was denied to the
  agent in `P4.S4` and is not yours to do; execute every anonymous block (board, 종목 조회, 이벤트,
  AI 질문 with **one** real question — one model call, accepted cost, say so — 샘플 포트폴리오,
  404) and mark the account-bound blocks (회원가입 · 담기 · 알림 설정 · mail) as 「운영자 검증 항목」
  for the gate walkthrough, with the exact expected strings still written.
- `python3 scripts/render_submission_pdf.py <in> <out>` → open the PDF (the Read tool renders
  pages): Korean renders as Korean, tables intact, the §5 numbered blocks readable.
- `python3 scripts/workflow.py validate` clean.

## Notebook

`## Operator Questions`: (1) the 심사용 테스트 계정 — self-signup only, or an operator-made
account whose credentials go into §5 literally; (2) anything §5 could not be written honestly
without. Notes **(from P4.S8, for P4.REVIEW)**: the account-bound §5 blocks the operator verifies
at the gate; the snapshot date of every live figure; where the two PDFs are. `## Doc impact`:
`none` unless you changed durable truth (a draft document is not durable truth) — but if you find a
place where `docs/current/` contradicts the live product, record it as a finding in `result.md`
and as a Doc impact line naming the doc. Drop the consumed `for P4.S8` notes; rewrite `## Now`
(≤ 15 lines) last; never touch the generated `## Slices` block.

## Return

A structured verdict (`status`, `summary`, `files_changed`, `validation`, `deviations`,
`doc_impact`, `doc_versions: n/a`, `review_verdict: n/a`, `walkthrough: none`, `explain: n/a`).
In `result.md`: what you wrote and why it is shaped so, the §5 execution log (expected vs
observed, per block, with the date and the instrument), any place the sources disagreed, and
anything a judge would ask that the document does not answer. If a section cannot be written
honestly from what runs, say so rather than writing around it.

## Reconciled against P4.F1 (2026-09-02, orchestrator)

- `P4.F1` is **live on production** (`96f7141`): the 샘플 포트폴리오 shows four distinct issuers with
  one ① counting down (아이에이, D-43, 발행가 확정 전 on 2026-09-02). §1/§2/§5 describe that; the
  example 보유량 stay 500/300/500/100 and the composition changes with the corpus — say so.
- **This was the last planned deploy before the freeze.** Nothing in this slice ships code, so
  nothing here needs one.
- **Local resolver trap:** this Mac's Tailscale MagicDNS answers `www.jujutower.com` with
  non-Cloudflare addresses, so a plain `curl https://www.jujutower.com/` from here can fail while
  production is correct. For any `www` line in §5's verification use
  `curl --resolve www.jujutower.com:443:104.21.21.26 …` (or `dig @1.1.1.1` first) and say so in
  `result.md`; the document itself just states the redirect.
