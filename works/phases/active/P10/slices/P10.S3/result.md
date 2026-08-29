# Result — P10.S3 (the rendered-string sweep, including the assistant's own name)

- **status:** `done`
- **summary:** Swapped the product's name in **15 live strings** — the two the decomposition
  knew about (`event/copy.ts:114` 실권주 disclaimer, `app.py:57` OpenAPI `TITLE`) plus **13
  live agent prompt strings** it never saw, because the prompts spelled the product 미주얼
  (얼) rather than 미주알. Name only: no sentence reflowed, reordered or rewritten.
- **files_changed:**
  - `frontend/components/event/copy.ts`
  - `src/mijual/web/app.py`
  - `src/mijual/agent/instructions.py`
  - `src/mijual/agent/tools.py`
  - `src/mijual/agent/declarations.py`
  - `works/phases/active/P10/phase.md`
  - `works/phases/active/P10/slices/P10.S3/result.md`
- **validation:**
  - `cd frontend && npm run typecheck` — **pass** (`tsc --noEmit`, no output)
  - `cd frontend && npm run smoke` — **pass**, 22/22
  - `.venv/bin/python -m pytest` — **pass**, 154 passed, 1 pre-existing starlette warning
  - `python3 scripts/workflow.py validate` — **pass** (2 pre-existing P9 `kind: research` warnings)
  - real browser, **dev**, operator runtime (`make stack-up` targets, `next dev` on
    `0.0.0.0:3000`, `http://127.0.0.1:3000`, Chrome 152 on this Mac at dsf 2, plus a 390x844
    mobile viewport): both 실권주 render sites measured old-string vs new-string in place —
    **identical boxes**, no new wrap, no clip, no overflow
  - `curl http://127.0.0.1:8000/openapi.json` and `/docs` — both read `주주의관제탑 API`
  - eight reader pages swept for old-name `innerText` — **zero** hits
  - **live agent**, four Korean meta questions through `POST /ask` against real Gemini —
    every answer names 주주의관제탑, none says 미주얼 or 미주알
- **deviations:** three, all small; see *Deviations* below.
- **doc_impact:** three lines appended to `phase.md` (backend.md + architecture.md — the agent
  prompt names the product 주주의관제탑, latin gloss dropped, cache prefix invalidated once;
  api.md — the served OpenAPI title; security.md — `docs/current/security.md:307` is the one
  미주얼 in `docs/current/`, flagged for S4).

---

## 1. What changed

**15 live strings, and one comment.** Everything else in the phase's grep is an identifier, a
comment, `docs/current/` prose (S4's) or history.

### 1.1 The 실권주 disclaimer (1 rendered string)

`frontend/components/event/copy.ts` `MISMATCH_HEADER_KO`:

```
… 두 값을 제시합니다 — 미주알은 어느 쪽도 …   →   … 두 값을 제시합니다 — 주주의관제탑은 어느 쪽도 …
```

**Particle re-checked, not assumed:** 알 (ㄹ) and 탑 (ㅂ) both end in a consonant, so the
subject particle stays `은`. Nothing else in the sentence moved.

Re-exported unchanged through `components/lookup/copy.ts:55`; rendered at
`components/event/Offering.tsx:301` and `components/lookup/MissedMoney.tsx:395`.

### 1.2 The served API title (1 served string)

`src/mijual/web/app.py:57` `TITLE = "미주알 API"` → `"주주의관제탑 API"`, reaching
`FastAPI(title=TITLE)` at `:113`. No particle follows. `DESCRIPTION` is untouched (its one
`mijual.agent` is a module path, out of scope).

### 1.3 The assistant's own name — 13 live prompt strings

The plan's list was verified line by line against the file before editing, and it was correct.

| file | lines | block |
|---|---|---|
| `agent/instructions.py` | 52, 83, 122, 134, 141, 151, 162, 198, 213 | `_ROLE`, `_CITATIONS`, `_CALCULATOR`, `_OUT_OF_SCOPE` ×2, `_SECURITY` ×2, `_TOOL_NOTES`, `_FINALLY` |
| `agent/tools.py` | 260 | `DATA_BOUNDARY` |
| `agent/declarations.py` | 139, 283, 300 | `save_feedback` and `security_check` descriptions |

Excluded as comments, confirmed by reading each: `instructions.py:130` (`#:` block),
`citations.py:19`, and every module docstring.

**Two shapes of edit, as the plan called for:**

- `instructions.py:52` — `You are 미주얼(Mijual)'s 해설 agent.` → `You are 주주의관제탑's 해설
  agent.` The parenthesized latin gloss is **dropped, not translated**: there is no romanized
  replacement by operator decision.
- `declarations.py:139` — *Mijual* was an **English noun** ("a suggestion about Mijual
  itself"), which cannot take a Korean proper noun cleanly. Reworded to **"this product
  itself"** (see *Deviations* #1 for why not the plan's example wording).

**Constraint honoured:** only names changed. No line was reflowed, reordered, retitled or
tightened, and no line-wrap position moved — the diff is 13 single-line substitutions, each
line simply longer. `instructions.py`'s own header (`:26–36`) declares the instruction order a
cache key; that order is byte-identical, and the one-time implicit-cache invalidation from the
changed prefix bytes is the accepted cost the plan named.

### 1.4 The one comment fixed

`frontend/components/event/copy.ts:104` opened `The 발행사 기재 불일치 sentences, R3 §State
pages verbatim.` After the swap the header is **no longer verbatim R3**, so the comment would
have been flatly false about the constant directly beneath it — the plan's single exception,
and S2's precedent for `BRAND_ALT_KO`/`COPYRIGHT_KO`. Rewritten to say what is now true, with
the historical 미주알 token kept inside the explicitly historical clause. **No other comment
was touched** anywhere in the repo.

## 2. The product had been shipping two spellings of its own name

Worth stating plainly rather than silently normalising: until this slice the **UI said 미주알**
and the **assistant said 미주얼**. Both were the product's name; neither was a typo confined to
one line (미주얼 appears 14 times in `src/`, 13 of them live prompt text). A reader who asked
the assistant "너 이름이 뭐야?" got a different spelling from the one in the footer beside it.

The rename incidentally fixes that, because both spellings converge on 주주의관제탑. **No
operator question was filed** — the plan asks for one only if something needs deciding, and
nothing does: both spellings were the old name and both are in scope under "the name the
product uses when it talks to a user". It is recorded as a `## Decisions` entry in `phase.md`
and here.

## 3. Proving the sweep is complete

Searched `미주알`, `미주얼`, `MIJUAL`, `Mijual`, `mijual` across the repo excluding
`node_modules`, `.next`, `works/`, `docs/versions/`, `.venv`, `var/`. **Every surviving hit
classifies, and none is an unclassifiable one:**

| class | where |
|---|---|
| **Live product string** | **none left** — this slice was the last one |
| Out-of-scope identifier | `MIJUAL_*` env vars; `X-Mijual-CSRF` (`web/csrf.py:45`, `web/ops.py:52`); `mijual.<module>` / `from mijual` / `src/mijual` everywhere; `compose.yaml:37–45` local DB user/password/db + `container_name: mijual-postgres`; `evalset/labels.json:354` (an absolute path containing the repo directory name); `tests/test_web_auth.py:28` + `test_web_portfolio.py:268` fixture emails `Reader@Mijual.KR`; `"Mijual Design System"` (`assets/README.md:9`) |
| Comment / docstring (**out of scope by operator decision**) | `src/`: `agent/instructions.py:130`, `agent/citations.py:19`, `agent/client.py:117,395`, `agent/loop.py:322`, `web/vocky.py:32,37,40,61,143`, `web/routers/feedback.py:5`, `mijual/__init__.py:1`. `frontend/`: `lib/api.ts:2`, `lib/copy.ts:41`, `app/shell.css:1`, `app/events/[rcept_no]/page.tsx:26`, `components/auth/copy.ts:30,196`, `components/portfolio/copy.ts:26`, `components/event/Offering.tsx:288`, `components/event/copy.ts:105` (mine, historical), `components/chrome/{copy.ts:25,44,179,188, Nav.tsx:33, Footer.tsx:15,33, Feedback.tsx:29,33,39, SiteChrome.tsx:22, AccountSlot.tsx:40,170, index.ts:12, Wordmark.tsx:15, Footer.module.css:31}`, `components/ops/copy.ts:30,31` |
| **Vendored — never edited** | `frontend/public/foundations/tokens.css:6`, `fonts.css:7`. Byte-verbatim design foundations; their comments name the old product and are publicly fetchable. Deliberately left alone |
| **S4's** (do not touch here) | `docs/current/*.md` (11 `미주알` + **1 `미주얼` at `security.md:307`**), `frontend/README.md:1,87`, `frontend/package.json:5` `description`, `pyproject.toml:8` `description`, `Makefile:1,110`, `compose.yaml:1` |
| History / record — must not change | `docs/reference/design/**` (the signed design record, incl. `SIGNOFF.md`), `docs/versions/**`, `frontend/public/assets/README.md:23,151,154,161` (the `mijual-*` retirement record), `docs/current/frontend.md:120` + `decisions.md:674` (supersession rows) |
| Out of this phase's scope, already an open operator question | `src/mijual/mail.py:14` — P4's unimplemented R5 mail subject `[미주알] …` |

**One finding worth handing on** (it is now in the S4 note in `phase.md`): the decomposition's
count for `docs/current/` was built from a `미주알`-only grep, so it **missed
`docs/current/security.md:307`**, which spells the product 미주얼 inside the lethal-trifecta
paragraph. It is in scope for S4 and a `미주알` grep will not find it.

## 4. Verification, in the operator runtime

Manifest: `docs/current/operations.md` `## Operator Runtime` — present, no `UNFILLED`. Ran the
`make stack-up` targets (`db-ensure`, `api-up`, `web-up`), so `next dev` on `0.0.0.0:3000`,
uvicorn on `127.0.0.1:8000`, browsed `http://127.0.0.1:3000` in Chrome on this Mac at
`deviceScaleFactor: 2` plus a 390x844 mobile viewport. The plan explicitly does not require a
production build of me (S5 does the comprehensive pass), and I did not run one.

### 4.1 The disclaimer's two render sites — measured A/B, in place

The plan warned the sentence grows four syllables and asked whether either caption now wraps or
clips. I measured the **same DOM node twice** — once with the new string, once with the old —
so the comparison is exact rather than remembered:

| viewport | route | node | new | old |
|---|---|---|---|---|
| 1280x800 @2 | `/events/20260223002079` | `p.mismatchHead` (12px / 18.6px) | 996x18.59, **1 line** | 996x18.59, 1 line |
| 1280x800 @2 | `/stocks/00113261` | `span.cap` (11px / 17.05px) | 246.25x51.14, **3 lines** | 246.25x51.14, 3 lines |
| 390x844 @3 | `/events/20260223002079` | `p.mismatchHead` | 290x37.19, **2 lines** | 290x37.19, 2 lines |
| 390x844 @3 | `/stocks/00113261` | `span.cap` | 306x34.09, **2 lines** | 306x34.09, 2 lines |

**Identical to the hundredth of a pixel in all four.** `scrollWidth == clientWidth` and
`scrollHeight == clientHeight` on every node, `overflow: visible`, `text-overflow: clip`, and
`document.documentElement.scrollWidth == 390` at mobile — so **nothing wraps differently,
nothing clips, and nothing overflows.** No operator question arises.

**Correcting the plan's premise:** it describes both sites as "single-line captions". They are
not. `span.cap` on `/stocks/*` already ran to **three** lines at desktop and two at 390 with the
old string, and `p.mismatchHead` already ran to two lines at 390. The four extra syllables land
inside existing slack in every case, so the conclusion is unchanged, but the reason is
"the boxes already wrap and had room", not "the captions still fit on one line".

Live data for the mismatch state is rare — the corpus holds **5** `issuer_disagreement` rows out
of 69 performance reports. The pair above (대한광통신) exercises both components; the other four
corps are `01251489`, `00654175`, `00412348`, `00409371`.

### 4.2 The API title

`GET /openapi.json` → `info.title == "주주의관제탑 API"`; `GET /docs` →
`<title>주주의관제탑 API - Swagger UI</title>`. `/api/health` through the Next rewrite: 200.

### 4.3 Page sweep

`/`, `/ask`, `/stocks`, `/stocks/00113261`, `/events/20260223002079`, `/portfolio`,
`/auth/login`, and a 404 path. Every one: `document.title == "주주의관제탑"`, and `body.innerText`
contains **no** `미주알`, **no** `미주얼`, **no** `MIJUAL`/`Mijual`, and **does** contain
주주의관제탑.

### 4.4 The live agent — it was run, not skipped

`GEMINI_API_KEY` **is** configured in the repo-root `.env`, so this check did **not** have to be
handed to S5. Four Korean meta questions through `POST /ask` (SSE) against the real model
(`gemini-3.7-flash`):

| question | answer |
|---|---|
| `너 이름이 뭐야?` | `주주의관제탑의 공시 해설 에이전트입니다. …` |
| `너는 뭐야?` | `저는 주주의관제탑의 공시 해설 에이전트입니다. …` |
| `이 서비스 이름이 뭐예요?` | `이 서비스의 이름은 주주의관제탑입니다. …` |
| `너 미주얼이야?` | `저는 주주의관제탑의 공시 해설 에이전트입니다. …` |

None contains 미주얼 or 미주알. The fourth is the interesting one: asked the old name directly,
the assistant answers with the new one and does **not** echo the old, and correctly did **not**
fire `security_check` (a meta question is not an attack — the `_SECURITY` anti-overtrigger rule
still holds after the edit). `tool_calls: 0`, `rounds: 1` on each, matching `_FINALLY`'s "메타
질문 … with **no tool call at all**".

Production was **not** exercised for this check — noted in the S5 note in `phase.md`.

## 5. Deviations

1. **`declarations.py:139` reworded to "this product itself", not the plan's example "this
   service itself".** The plan's wording was explicitly an `e.g.`. The sentence immediately
   before it in the same description already says *"Save the reader's feedback about **this
   product**…"*, so "service" would have introduced a second noun for the same referent inside
   one tool description the model reads to decide when to call `save_feedback`. Echoing the
   description's own noun keeps the contrast the sentence exists to draw (feedback about the
   product, not about a filing) and invents nothing. Worth naming as an alternative that was
   **not** taken: `declarations.py:283` and `:300` do carry `주주의관제탑` inside English
   sentences, so substituting there was possible — but the plan directs rewording where the
   mark is an English **noun**, and "a suggestion about 주주의관제탑 itself" reads as naming a
   third party rather than the speaker's own product.
2. **One comment edited** — `event/copy.ts:104`, under the plan's stated exception, because it
   asserted the string beneath it was R3-verbatim and the swap made that false. §1.4.
3. **Postgres host port, again.** `make stack-up` still fails at `db-up`: host port 5433 is held
   by `changple_web_dev_postgres` from an unrelated project. Same way through S2 documented —
   same `postgres:16` image, same `mijual_mijual-pgdata` volume, host port **5434** via a
   scratchpad compose fragment using the `!override` tag, and
   `DATABASE_URL=postgresql+psycopg://mijual:mijual@localhost:5434/mijual` on the API process
   only. **The browser-facing runtime is unchanged** — same `next dev` on `0.0.0.0:3000`, same
   `http://127.0.0.1:3000` origin, same API on `127.0.0.1:8000`, same Chrome. **Restored
   afterwards:** `make stack-down`, then the container recreated from the **unmodified**
   `compose.yaml` (5433) and left **stopped**, exactly as found; the other project's container
   was never touched and the override fragment never entered the repo.

## 6. Dead ends and things checked that produced nothing

- **Looked for a second rendered frontend string and found none.** S2's tagged note said the
  remaining rendered set was exactly two; a fresh grep of all of `frontend/` confirmed it —
  every other Korean-name hit in `.tsx`/`.ts`/`.css` is inside a comment.
- **Tried `/events/{performance rcept_no}` first** to find a live mismatch and got 404s: the
  `issuer_disagreement` rows are keyed by the **실적보고서** receipt number, and the event page
  wants the **decision** receipt number (`lapse.rows[].decision_rcept_no` on `/stocks/{corp}`).
  That mapping is how `/events/20260223002079` was found.
- **No lint gate exists** (`pyproject.toml` configures only pytest; no ruff/black/mypy config,
  no Makefile lint target), so lengthening prompt lines past any column limit was not a concern
  and no reflow was forced. This is the mechanical reason the "change only the name" constraint
  could be honoured literally.
