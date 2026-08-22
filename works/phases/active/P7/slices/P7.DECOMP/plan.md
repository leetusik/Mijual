# Plan — P7.DECOMP: decompose the 실서비스 정상화 fix pass

## What this phase is

P5 (web build) and P6 (AI 질문 agent) are `done` and reviewed, but the operator ran the
product and found it broken or rough in **11 confirmed ways**. `intent.md` (phase root) is
the confirmed record — read it first; the 11 numbered items there are the whole scope. This
is a **fix pass, not a feature phase**: make the already-built product actually work.

Two framing facts decided at intent capture:

- **No design round.** The operator ruled "respect the design, double check everything": no
  `co-work` slice, no `DECOMP2`, no new Claude Design round. Every fix is checked against the
  signed P3 record (`docs/reference/design/` — `SIGNOFF.md` first, then the governing round's
  `output/build-prompt.md` + `result.md`; supersession table in `docs/current/frontend.md`).
  Where an operator ask seems to collide with the record (items 3, 9, 10 especially), the
  slice must find what the record actually says and implement *that* — e.g. item 3: the blue
  focus ring is almost certainly the UA default leaking and being clipped by the 조회 button;
  the fix is the record's own focus treatment (and keyboard `:focus-visible` a11y preserved —
  `frontend` v0002 calls the focus ring "the shell's" a11y floor), never a freelance restyle.
  Record your reading of each such collision in `phase.md` so the slices inherit it.
- **Ordered before P4 (Ship & Submit)** — phase order 3.5. The product must work on the dev
  stack (`make stack-up` / `make stack-status`; frontend `http://127.0.0.1:3000`, API
  `127.0.0.1:8000` via the Next `/api/*` rewrite) before it ships.

## Your job (decomposition only)

1. **Read**: `CLAUDE.md`, `works/phases/active/P7/intent.md`, `phase.md`, `docs/current/frontend.md`
   (esp. "Where the design lives", the supersession table, "Where things live", and the
   fidelity rules), `docs/current/experience.md` / `product.md` / `api.md` as needed, the P5 and
   P6 `phase.md` decomposition tables + the notes for the surfaces involved (landing board,
   lookup, chrome/nav/account slot, auth, portfolio, ask widget/launcher, SSE/agent route), and
   the code under `frontend/` that each item touches.
2. **Reproduce / root-cause, read-only, before cutting slices.** Do not fix anything. For each
   of the 11 items find the seat of the defect and whether items share a root cause — e.g.
   **8 and 11** (AI 질문 send dead + widget not rendering — `components/chrome/SiteChrome.tsx`
   mounts `AskSurface`, which "renders nothing at ≤480px, nothing on `/ask`, nothing under
   `/ops`" — is it gated on something that is false on dev? env? the agent route / SSE path?
   **의견 (vocky)** is also reported broken — `VockyScript` / `NEXT_PUBLIC_VOCKY_SRC`),
   **5** (login: `app/auth/login/page.tsx`, `components/auth/*`, `chrome/AccountSlot.tsx`,
   `lib/session*.ts`, `MIJUAL_COOKIE_SECURE` — is the slot hidden, the route unlinked, or the
   API failing?), **6 and 7** (countdowns static + auto-refresh stomps state — both about how
   the landing refreshes: request-time server render + a reload-style refresh vs. a client
   tick + data-only refresh that preserves input), **2** (typeahead — is there a stocks search
   endpoint in the API, or does this need a backend route too? `docs/current/api.md`),
   **4** (board shows everything; the 펼치기 toggles on the 전환청구 진행 중 / 일정 추후결정
   headers do nothing — `components/landing/Board.tsx`/`BoardRow.tsx` — what did R2 specify
   for these sections and for list length?), **9** (`components/portfolio/*`, `lib/sample.ts` —
   the 챙겼습니다 action and the 놓친 돈 display; what does R5 say the click does?), **10** (grep
   for the self-narrating copy pattern — `localStorage`, "본인 표시", "이 브라우저에", and any
   other implementation-detail sentence across `*/copy.ts` and components; list every hit),
   **1** (`chrome/copy.ts` `NAV_LINKS` + `lib/routes.ts` — dropping the 내 종목 조회 nav item;
   note the R6 "final three-slot nav" supersession and record that this is an operator
   override of that slot, verified against the record for what else references it). Use the
   running stack (`make stack-status`; start it if down) and `curl` / the API where it helps
   — e.g. confirm the ask/agent route and the auth routes respond. Record findings per item in
   `phase.md` ("Findings & Notes") with file paths — these are what the slice plans will be
   written from.
3. **Cut the middle slices** with `python3 scripts/workflow.py new-slice --phase P7 --slice
   P7.S<n> --name "..." --kind fix --risk <low|high> --order <n> [--depends-on ...]`. Bare
   folders only — **never write another slice's `plan.md`**. Group by root cause and blast
   radius, not by the operator's numbering; a sensible shape (revise it on what you find) is
   roughly: the AI 질문 surfaces (8 + 11 + 의견) · login (5) · landing liveness (6 + 7) · board
   length + working 펼치기 (4) · search typeahead (2, backend route if needed) · focus treatment
   (3) · nav item removal (1) · self-narrating copy sweep (10) · sample portfolio tidy +
   챙겼습니다 (9) · and a **final real-browser fidelity sweep** across all fixes (the way
   `P5.S19` / `P6.S7` did — headless Chrome over CDP against `next build && next start`,
   widths incl. 1440/768/390, checked against each governing round) ordered last before
   `P7.REVIEW`. Merge or split as the root causes dictate; fewer, well-bounded slices beat many
   thin ones. Order the "totally broken" ones (8/11, 5) early and anything whose fix another
   depends on before it. Every fix slice must leave each fix **verified in a real browser on
   the dev stack**, not just type-checked; say so in its name/notes only if useful — the
   orchestrator writes the plans.
4. **Risk is the cost lever.** `low` → `slice-executor-mid`: only a one-line / few-line edit or
   docs touching one file (item 1 may qualify if it is truly a `NAV_LINKS` entry removal and
   nothing else). Anything that writes real code, or touches more than one file, is `high`.
   The fidelity sweep is `high`.
5. **Write `phase.md`**: the slice table (id · order · what it covers · which of the 11 items ·
   why grouped so), the per-item root-cause findings, the design-collision readings from the
   framing above, constraints (RESPECT THE DESIGN; record read-only; no `doc-new-version` in
   fix slices — "Doc impact" notes only; how to run the stack; how the browser check is done),
   and open questions. Keep `REVIEW` last by order.
6. **Validate**: `python3 scripts/workflow.py validate` (must pass) and `python3
   scripts/workflow.py next` shows `P7.S1` as next after this slice. Write `result.md`
   (what you created, what you found, deviations). `doc_impact`: `none` expected (decomposition
   changes no durable truth), unless investigation reveals a doc that is already wrong — then
   append a "Doc impact" line for the review.

## Don'ts

No code changes, no `co-work` slices, no `DECOMP2`, no pre-filled plans, no commits, no state
transitions besides `new-slice`. Do not start or stop the dev stack in a way that leaves it
worse than you found it (if you start it, leave it running; note its state in `result.md`).
