# Result — P7.S7: the self-narrating copy, swept

**Two rendered strings changed, three code comments corrected, four strings listed for the
operator, and nothing else touched.** The sweep covered **346 Hangul string literals** across
`frontend/app`, `frontend/components` and `frontend/lib` (comments and docstrings excluded by a
real tokenizer, not a grep — see *Method*), plus JSX bare text, every `aria-label`/`title`/
`placeholder`/`alt`, the document metadata, and the reader-facing Korean the backend composes.
After the edits **no string a reader can see contains `localStorage`, `sessionStorage`,
`브라우저 세션`, `이 브라우저`, or even the word `브라우저`** — measured on both operator origins in
`next dev` and in an isolated production build.

## The two edits

| file:line | before | after | rationale |
|---|---|---|---|
| `frontend/components/portfolio/copy.ts:195` (`CLAIM_CAPTION_LOCAL_KO`) | `본인 표시 · 이 브라우저(localStorage)에` | `본인 표시` | The operator's own literal example. R5-8's caption **is** 「본인 표시」; the storage clause came from the build prompt's parenthetical about where a sample/anonymous mark is kept, which is mechanism the reader gains nothing from. Trim, not a rewrite. |
| `frontend/components/lookup/copy.ts:101` (`HOLDING_CAPTION_KO`) | `브라우저 세션에만 저장 · 서버 전송 없음` | `서버 전송 없음` | Design-collision reading #6 exactly: the mechanism clause goes, **the promise stays verbatim**. This is an **R4 §3 signed literal trimmed — a P7 operator override**, listed below and in the Doc impact line. The promise is still true by construction (`lib/holding.ts` writes sessionStorage; `GET /stocks*` has no `n` parameter). |

Comments corrected so nothing in the tree still claims the old caption is what renders (comment-only,
no behaviour):

| file:line | what changed |
|---|---|
| `frontend/components/portfolio/copy.ts:184-194` | The R5-8 + build-prompt citation **kept**; a paragraph added stating the P7 item-10 trim, why the account half keeps 계정에 저장, and that the two captions no longer differ only in storage. |
| `frontend/components/lookup/copy.ts:93-100` | The R4 §3 literal **kept and named as the literal**; the doc comment now says P7 trimmed it to the promise half, calls it a P7 operator override, and re-states why the promise remains true. |
| `frontend/components/lookup/HoldingStrip.tsx:22-24` | The round's blockquote is verbatim and stays; one sentence added — what renders is 「서버 전송 없음」. |
| `frontend/lib/holding.ts:206-211` | Had said the caption states the session-only rule "on the surface" — no longer true; now says the surface renders only the promise and the storage is still exactly this module. |
| `src/mijual/web/routers/stocks.py:36-40` | The "no holding count is ever received here" rationale quoted the full caption; it now quotes 「서버 전송 없음」 and notes the P7 trim. The API rule it justifies is unchanged — the trimmed half is the half the rule leans on. |

## The full inventory (every rendered string that touched the sweep's vocabulary)

`kept` = a reader fact or trust promise; `changed` = trimmed above; `ask` = listed for the operator;
`n/a` = operator-facing `/ops`, out of scope by the plan.

| file:line | constant | string | verdict |
|---|---|---|---|
| `components/portfolio/copy.ts:195` | `CLAIM_CAPTION_LOCAL_KO` | `본인 표시 · 이 브라우저(localStorage)에` | **changed → `본인 표시`** |
| `components/lookup/copy.ts:101` | `HOLDING_CAPTION_KO` | `브라우저 세션에만 저장 · 서버 전송 없음` | **changed → `서버 전송 없음`** |
| `components/portfolio/copy.ts:194` | `CLAIM_CAPTION_ACCOUNT_KO` | `본인 표시 · 계정에 저장` | kept — where the mark lives is the reader's own fact (plan's decision); consistency question below |
| `components/portfolio/copy.ts:103` | `HOLDING_CAPTION_KO` | `계정에 저장 · 마감 알림의 기준` | kept — both halves are reader facts (R5's literal) |
| `components/ops/copy.ts:215` (+ `components/ask/copy.ts:58`) | `ANONYMOUS_PROMISE_KO` / `ANONYMITY_KO` | `… 대화는 익명으로 저장됩니다 (품질 점검용)` | kept — the trust promise + its purpose; R6-6 forbids the alternatives |
| `components/auth/copy.ts:152` | `PII_NOT_STORED_KO` | `저장하지 않는 것은 유출되지 않습니다` | kept — the PII inset's promise (R5-1) |
| `components/auth/copy.ts:151` | `PII_RECEIVES_KO` | `미주알이 받는 것: 이메일 주소와 비밀번호` | kept — states what is taken, not how |
| `components/auth/copy.ts:162` | `CONVERT_SESSION_KO` | `이 보유량은 탭을 닫으면 사라집니다` | kept — the *consequence* in reader language; the model of what item 10 wants, not an instance of it |
| `components/auth/copy.ts:164` | `CONVERT_BODY_KO` | `계정에 저장하면 마감이 다가올 때 이메일로 알립니다 — …` | kept — an offer and its benefit |
| `components/ask/copy.ts:46` | `AGENT_INTRO_KO` | `검증을 통과한 공시에 대해서만 답합니다 …` | kept — the agent's signed promise |
| `components/ask/copy.ts:201` | `VERIFIED_ONLY_KO` | `검증된 필드만 근거로 답합니다 — 모든 답에 원문 인용` | kept — R6 calls it "the promise line"; 필드 is the detail page's own reader vocabulary |
| `components/ask/copy.ts:108` | `DISCONNECTED_KO` | `연결이 끊겼습니다 — 답변이 여기서 중단되었습니다.` | kept — the reader's state (their answer stopped), the only sentence R6 writes for an unfinished turn |
| `components/ask/copy.ts:159` | feedback confirm | `의견을 저장했습니다 — 운영자가 확인합니다.` | kept — a confirmation and who acts next |
| `components/ask/copy.ts:118` | `API_TIER_KO` | `DART 공시 API 수치 — 원문 스팬 없음, 접수번호가 인용 핸들` | **ask** (Q-A) |
| `components/event/copy.ts:134` | `SPARSE_CLOSING_KO` | `공시 본문에서 확인된 추가 조건이 없습니다 — 위 값은 DART 공시 API 기준입니다` | **ask** (Q-B) |
| `components/chrome/copy.ts:156` | `GATE_COST_TAIL_KO` | `은 할인율 인용이 게이트를 통과하지 못해 총액에서 제외했습니다` | **ask** (Q-C) |
| `components/portfolio/copy.ts:135` | `carryOverKo` | `조회에서 입력한 {stock} {shares}주가 이 세션에 남아 있습니다` | **ask** (Q-D) |
| `components/event/copy.ts:243` | fields provenance | `모든 값은 DART 공시에서만 나왔습니다 · 각 항목의 [근거]가 …` | kept — provenance promise, product nouns only |
| `components/chrome/copy.ts:137` | `PROVENANCE_KO` | `모든 수치는 DART 공시에서만 나왔고, 추정치는 [추정] …` | kept — same |
| `components/landing/copy.ts:141` | stale banner | `데이터가 갱신되지 않고 있습니다. 아래 값은 기준 시각의 …` | kept — a freshness fact the record requires ("stale, never dark") |
| `components/lookup/copy.ts:253`, `:208`, `:242` | disclaimer/footnotes | `… 시장 가격을 사용하지 않습니다`, `실제 손익은 …`, `놓친 돈은 집계 범위 …` | kept — scope and method claims about the *number*, not about the software |
| `components/ops/copy.ts` (≈30 strings: `렌더 가능 필드`, `차단 플래그`, `세션 해시`, `API shape 확정 대기`, `코퍼스 게이트 차단율` …) | — | — | n/a — `/ops` is operator-facing, behind its own login, never linked from reader chrome (`copy.ts:103`); the plan scopes it out and none of it is the reader pattern |

Checked and **clean** (no hit): `lib/copy.ts`, `lib/format.ts`, `lib/types.ts`, `components/landing/*`,
`components/event/*` (except the row above), `components/chrome/*` (except the row above),
`app/**` (the only document-level string is `title: "미주알"`; there is no `not-found.tsx` — the 404
is the framework's English default, catalogue #1/Q6, **not** an item-10 hit and not touched), every
`aria-label` / `placeholder` / `alt` (all of them read a `copy.ts` constant), and the Korean the
**backend** composes for readers (`src/mijual/agent/copy.py`: the 도구 행 like `이벤트 읽기 → …` and
`의견 저장 → 운영자 검토 대기열` name *product actions* — R6's signed transparency rows — and no
refusal sentence or tool row mentions storage, a browser or a transport).

## Listed for the operator (not edited — the plan's "unsure ⇒ ask" branch)

1. **Q-A `API_TIER_KO`** (`components/ask/copy.ts:118`) — `DART 공시 API 수치 — 원문 스팬 없음,
   접수번호가 인용 핸들`. Three developer words (API 수치 · 원문 스팬 · 인용 핸들) in a sentence
   whose *job* is trust: it is what an answer prints when a fact has no verbatim quote, and it
   explains why the citation is a filing number instead. Every clause carries part of that
   explanation, so there is nothing to trim — only a rewrite, which would mint Korean. **Ask:
   does the operator want it re-said in reader language (a new sentence = a copy decision), or
   left as signed?**
2. **Q-B `SPARSE_CLOSING_KO`** (`components/event/copy.ts:134`) — `… 위 값은 DART 공시 API
   기준입니다`. Same class, R3 verbatim. A one-word trim exists (`위 값은 DART 공시 기준입니다`) and
   reads fine, but it erases the 본문 ↔ API distinction that is exactly why those rows carry a
   접수번호 link and no `[근거]` chip. Not applied.
3. **Q-C `GATE_COST_TAIL_KO`** (`components/chrome/copy.ts:156`) — `49.2억원은 할인율 인용이
   **게이트**를 통과하지 못해 총액에서 제외했습니다`. 게이트 is internal machinery vocabulary sitting
   in the footer of every page; the sentence is R2 §Copy verbatim, signed at the gate, and is also
   the product's one disclosure of a number it deliberately excluded. No clause can go without
   killing the disclosure.
4. **Q-D `carryOverKo`** (`components/portfolio/copy.ts:135`) — `조회에서 입력한 계양전기 500주가
   **이 세션에** 남아 있습니다`. `세션` is on the sweep's own keyword list, but here it is also the
   only thing telling the reader the value is temporary. A pure trim exists (`… 500주가 남아
   있습니다`) — **not applied**, because R5-3 wrote the sentence whole and the impermanence would go
   with the word.
5. **Q-E (the plan's invited consistency question)** — with the sample caption now `본인 표시`, the
   account caption still reads `본인 표시 · 계정에 저장`. The plan says keep it, and it is kept. If
   the operator prefers one caption everywhere, `CLAIM_CAPTION_ACCOUNT_KO` → `본인 표시` is a
   one-line change and `Deadlines.tsx`'s ternary could then go entirely.
6. **Not a hit, recorded because the plan asked me to look:** the 404 is the framework's English
   sentence (no `app/not-found.tsx`; both `notFound()` call sites document the choice) — it is
   catalogue #1 / Q6, an English-copy question, not implementation narration.

## Validation

The dev stack was up throughout (`make stack-status`: postgres healthy, api pid 25177, web pid
13009) and **is still up**; port 3100 is free again.

| command / probe | outcome |
|---|---|
| `cd frontend && npm run typecheck` | **pass** (`tsc --noEmit`, clean) |
| `cd frontend && npm run smoke` | **pass** — 15/15 `node --test lib/*.test.ts` |
| `.venv/bin/python -m pytest` | **pass** — 139 passed, 3.2 s (the Python edit is a docstring; run because it is a source file) |
| `python3 scripts/workflow.py validate` | **pass** — `Workflow validation passed.` |
| CDP, `next dev` `http://127.0.0.1:3000`, 1440×900, fresh profile — **sample portfolio entered by clicking the product's own 샘플 포트폴리오로 둘러보기 link** on `/auth/login` | **pass** — link `href="/portfolio?sample=1"`, landed there hydrated; **both** 청약·매도로 챙겼습니다 rows' captions read exactly `본인 표시`; page innerText: `localStorage` 0, `sessionStorage` 0, `브라우저 세션` 0, `이 브라우저` 0, `브라우저` **0** |
| same session, `/stocks/00102618` (계양전기) with **500 typed into 보유 주식 수** | **pass** — caption reads `서버 전송 없음` before and after typing; the strip renders 보유 주식 수 · 주 · 100/500/1,000주 · `서버 전송 없음`, and the 500주 conversion (배정 신주 115주, 초과청약 +23주) recomputed, so the input still drives the page |
| same session, AI 질문 **widget** opened from the launcher | **pass** — empty state still prints the intro *and* `완전 익명 — 로그인도, 질문 수 제한도 없습니다 · 대화는 익명으로 저장됩니다 (품질 점검용)` |
| `document.body.innerText` token counts, `next dev` `127.0.0.1`, on `/`, `/stocks`, `/stocks/00102618`, `/portfolio?sample=1`, `/auth/login`, `/ask` | **pass — 0 / 0 / 0 / 0 for all four tokens on all six pages** (and `브라우저` 0 as well). `서버 전송 없음` present only on the stock page; `본인 표시` only on the sample. No console errors or warnings. |
| **before/after control** — the two constants temporarily reverted on disk, Fast Refresh, re-measured, then restored | **pass, and it proves the probe measures something**: before = sample `localStorage` **2**, `이 브라우저` **2**, captions `본인 표시 · 이 브라우저(localStorage)에` ×2; stock `브라우저 세션` **1**, caption `브라우저 세션에만 저장 · 서버 전송 없음`. After restore: all **0**, captions as designed |
| CDP on the **Tailscale** origin `http://100.77.164.42:3000` | **pass** — byte-identical result: captions `본인 표시` ×2 and `서버 전송 없음`, all tokens 0 |
| **Isolated production build** (`P7.S2` method: `rsync` of `frontend/` to session scratch, `npx next build` there, dev `.next` untouched) | **pass** — build clean, 16 routes |
| `next start -H 127.0.0.1 -p 3100` + served-HTML grep (`grep -o …` piped to `wc -l`, per `P7.S6`'s counting gotcha) on the same six paths | **pass** — every token **0** on every path; `서버 전송 없음` 1× on the stock page, `본인 표시` 2× on the sample page (the two past ① rows) |
| built bundles grepped for the old strings | **pass** — `이 브라우저` / `브라우저 세션에만 저장` appear **only inside `.js.map` source maps** (the round citations kept in the comments); **no emitted `.js` carries either string** |
| server stopped, `lsof -ti tcp:3100` | empty — port free; dev stack left running as found |

## Deviations from `plan.md`

1. **One backend file was edited — comment only.** `src/mijual/web/routers/stocks.py:36-40` quoted
   the full 조회 caption as the justification for "no holding count is ever received here". Leaving
   it would have left a docstring asserting on-screen copy that no longer renders. No code, no
   behaviour, no API change; `pytest` run to prove it.
2. **A before/after control measurement** was added beyond the plan's checks (the two constants
   temporarily reverted, measured, restored). `frontend` v0004's rule cuts both ways — a probe that
   can only report 0 proves nothing — so the before numbers are in the table above. The tree was
   restored and re-measured; the current state is the trimmed one.
3. **`carryOverKo` was left alone** although `세션` is on the plan's own keyword list — it went to
   the operator list (Q-D) instead, under the plan's "cannot cleanly classify ⇒ ask, never delete".
4. No `doc-new-version`, no commit, no state transition. Two Doc impact lines appended to
   `phase.md`.

## Scratch artefacts (session scratch, not the repo)

`scan.py` (the comment-aware string extractor), `probe_copy.py` / `probe_min.py` (CDP), the
before/after/tailscale JSON, `build.log`, and the 357 MB isolated build copy live in the session
scratchpad.
