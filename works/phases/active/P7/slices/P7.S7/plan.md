# Plan — P7.S7: copy sweep — remove self-narrating implementation copy across the reader surfaces

## Why

Operator item 10: "'본인 표시 · 이 브라우저(localStorage)에' — this kind of descriptive bullshit
everywhere. remove this kind of things." `P7.DECOMP` inventoried the rendered hits (`phase.md` →
"Item 10" table) and wrote **Design-collision reading #6**, which is this slice's rule: **separate
the narration from the promise** — strip implementation mechanism (`localStorage`, `이 브라우저`,
`브라우저 세션`, storage/technology words a non-developer gains nothing from), **keep the trust
promises** the record leans on (`서버 전송 없음`; the AI 질문 anonymity line; `계정에 저장` where it
tells the reader their data follows their account). Anything you cannot cleanly classify is not
deleted — it goes to the review's operator questions (`result.md` + `phase.md`).

Korean-only surface; no invented sentences — every edit shortens or trims an existing string, never
mints new phrasing (removing a segment of a ` · `-joined caption is trimming). Where a signed
literal is trimmed, record it as a P7 operator override in the Doc impact line.

## Decisions already made (apply them; do not re-argue)

| constant (file) | today | do |
|---|---|---|
| `CLAIM_CAPTION_LOCAL_KO` (`components/portfolio/copy.ts`) | `본인 표시 · 이 브라우저(localStorage)에` | → `본인 표시` (the operator's literal example; the R5-8 caption is "본인 표시"; the storage clause was the build prompt's, not the card's) |
| `CLAIM_CAPTION_ACCOUNT_KO` (same) | `본인 표시 · 계정에 저장` | **keep** — "계정에 저장" is the reader's fact (the mark follows the account), not mechanism. (If you judge both captions should read identically for consistency, say so in `result.md` as a question; do not change it.) |
| `HOLDING_CAPTION_KO` (`components/portfolio/copy.ts`) | `계정에 저장 · 마감 알림의 기준` | **keep** — both halves are reader facts (R5's own literal) |
| `HOLDING_CAPTION_KO` (`components/lookup/copy.ts`) | `브라우저 세션에만 저장 · 서버 전송 없음` | → `서버 전송 없음` — the promise stays verbatim, the mechanism clause goes (R4 §3 literal trimmed: **operator override**, Doc impact + operator question) |
| `ANONYMOUS_PROMISE_KO` (`components/ops/copy.ts`, rendered on `/ops` and in the AI 질문 empty state via `components/ask/copy.ts:59`) | `대화는 익명으로 저장됩니다 (품질 점검용)` | **keep** — a trust promise and a purpose, signed by R6/R7; not narration |

Then **re-run the inventory yourself** — the DECOMP table came from one keyword grep. Sweep every
rendered string (all `components/*/copy.ts`, `lib/copy.ts`, and literals inside `*.tsx`, including
`app/`) for implementation narration: storage/technology words (`localStorage`, `sessionStorage`,
`쿠키`, `캐시`, `세션`, `브라우저`, `서버`, `API`, `클라이언트`, `렌더`, `hydrat`, `SSE`, `스트리밍`,
`토큰`, `DB`, `쿼리`, `엔드포인트`, `rewrite`, `프록시`, `빌드`, `환경 변수`, `localhost`), and sentences
that explain *how* the product works rather than *what the reader gets*. Comments and docstrings
are **not** in scope — only text a reader can see. The `/ops` admin surface (`components/ops/*`)
is operator-facing: leave its own operational copy alone unless it is the same pattern shown to
readers. Also look at: the auth panel's PII inset and sample entry text, the portfolio sample mode
copy, the AI 질문 widget empty state / footer, the 404 page, the footer disclaimer. For every hit:
classify (narration → trim/remove; promise → keep; unsure → list), and record the full table in
`result.md` (file:line · before · after · rationale). Do not touch copy whose only "technology" word
is a product noun the reader needs (`DART`, `공시`, `KST`, `원문`, `근거`).

When a constant's doc comment cites the round literal, amend the comment to say the P7 trim and why
(one clause) — keep the citation.

## Verify — operator runtime

Dev stack up; Fast Refresh. `cd frontend && npm run typecheck && npm run smoke`. Headless Chrome
over CDP on `http://127.0.0.1:3000` (fresh profile; the S1–S5 `result.md` files show the approach):
`/portfolio` in **sample mode** (load the sample via the product's 샘플 entry) — the past-deadline
rows' caption reads `본인 표시` and contains no `localStorage`/`브라우저`; `/stocks/{corp_code}` with
a holding typed — the caption reads `서버 전송 없음`; the AI 질문 widget empty state still shows its
anonymity line; `document.body.innerText` on `/`, `/stocks`, a stock page, `/portfolio` (sample),
`/auth/login`, `/ask` contains none of: `localStorage`, `sessionStorage`, `브라우저 세션`, `이 브라우저`
(report counts). One pass on the Tailscale origin for `/portfolio`. Isolated production build
(`P7.S2` method) + `next start -p 3100`: grep the served HTML of `/portfolio?` / the sample for the
same tokens, kill it. `python3 scripts/workflow.py validate`. Leave the dev stack running.

## Record

`result.md` (the full hit table, commands/outcomes, operator questions). `phase.md`: Findings note
+ Doc impact lines — **`frontend`** (the trimmed captions; which signed literals were trimmed as
P7 operator overrides), **`experience`**/`product` if they quote the trimmed sentences (grep
`docs/current/*.md` for each before-string and list the docs that carry it). No `doc-new-version`,
no commits, no state transitions.

## Out of scope

Portfolio layout / 챙겼습니다 behaviour (S8), any non-copy change, anything in `docs/`.
