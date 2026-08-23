# Intent — P8

- Captured at: 2026-08-23T13:22:39+09:00
- Origin: operator

## Original Input (verbatim)

> ---
> you make design phase part 2. no new features but polish.
> make slices, and you ask what's wrong about the slice's stuff, I'll answer how it should be fixed. then design work and so on.
> no exception, we gonna audit and polish the whole things. 
> --
> Encountered two children with the same key, `t1`. Keys should be unique so that components maintain their identity across updates. Non-unique keys may cause children to be duplicated and/or omitted — the behavior is unsupported and could change in a future version.
> components/ask/AskWidget.tsx (96:11) @ <unknown>
>
>
>   94 |
>   95 |         {state.turns.map((turn) => (
> > 96 |           <div key={turn.id} className={styles.turn}>
>      |           ^
>   97 |             <p className={styles.question}>{turn.question}</p>
>   98 |             {/* A `pending` turn mounts no answer bubble at all: the button already
>   99 |                 says 답변 준비 중…, and an empty bubble would be a placeholder for a this also happens.

## Confirmed Intent (refined + clarified)

**Second design phase — polish only, no new features — covering the whole product, no exceptions.** P5 (web build), P6 (AI 질문 agent) and P7 (fix pass) are done; P8 audits and polishes every surface, ordered **before P4 (Ship & Submit)** at phase order 3.8.

**Per-surface rhythm (operator's words: "design part a slice -> apply part a slice -> design part b slice -> so on"):**

1. **Interview — walk first, then ask.** At the design slice's turn the orchestrator opens the surface in the operator's runtime (`## Operator Runtime`, operations doc), lists what it finds as a first-time user — dead/no-op controls, confusing bits, copy, states, mobile — with URLs/screenshots, sets the slice `pending`, and asks the operator "what's wrong and how should it be fixed?".
2. **Design round.** The operator's answers feed the round's `handoff.md` as direction / REFERENCE data (Claude Design + the operator still make every visual decision, per `design-cowork`); one `co-work` slice = one round = one handoff + one `pending` gate + read-back + SIGNOFF. Rounds continue the existing record (`docs/reference/design/rounds/08-…`, same Claude Design project "Mijual Design System", `SIGNOFF.md` accumulates).
3. **Apply.** An implementation slice, ordered immediately after that round, implements the signed round faithfully (RESPECT THE DESIGN), with its own fidelity + functional sweep in the operator's runtime (and the production build when behaviour differs). Its `plan.md` is written only after the round's SIGNOFF, from the landed `build-prompt.md`.
4. Next surface.

**Shape — a deliberate operator override of the standard mixed-phase form.** One phase, interleaved design → apply per surface; **no `DECOMP2`**. `P8.DECOMP` cuts, per surface, one `co-work` design slice (`--risk high`) followed by one bare apply slice (`--kind implementation --risk high`); re-shaping after a round goes in at fractional orders. The phase opens with `P8.S1` — a `fix` slice for the AskWidget `t1` duplicate-key bug.

**The 8 surfaces** (one round + one apply slice each; this order unless `DECOMP` finds a better one; mobile behaviour belongs to every surface, never its own slice):

1. foundations/tokens + global chrome (nav, footer, vocky feedback touchpoint)
2. landing 관제 현황판 + board
3. event detail — ① 유증 / ② CB / ③ 매수청구 + trust states
4. 내 종목 조회 + 놓친 돈 조회기 (`/stocks`, `/stocks/[corp_code]`)
5. auth (login / reset)
6. portfolio + notifications
7. AI 질문 (launcher / widget / `/ask` / question strip)
8. admin `/ops/*`

**Bug folded in (first slice):** React duplicate-key `t1` in `frontend/components/ask/AskWidget.tsx:96`. Root cause (orchestrator, read-only check): `frontend/lib/ask.ts:252` keeps a module-level `counter` that restarts at 0 on every page load, while `hydrate()` restores sessionStorage turns already named `t1…`, so the first fresh turn collides with a restored one.

**Operator runtime (operator-confirmed here; seeded into `## Operator Runtime` in the operations doc at phase creation):** dev mode via `make stack-up` (API on 127.0.0.1:8000, `next dev` on 0.0.0.0:3000 with `MIJUAL_DEV_ORIGINS`); the operator browses **http://127.0.0.1:3000 in Chrome desktop on this Mac** and the **Tailscale URL** from `make stack-status`; the **production build** (`cd frontend && npm run build && npm run start`) is checked additionally when behaviour differs; logs in `var/stack/{api,web}.log`.

**Shared working rules:** think/converse/document in English; the **product surface is Korean-only**. Acceptance gate to be declared at the `DECOMP` boundary — the phase changes operator-visible surfaces everywhere, so `accept-gate P8 --require` is expected.

## Clarifications Resolved

- Q: Phase shape — two phases (design → apply), one mixed phase (rounds → `DECOMP2` → build), or no Claude Design rounds (P7-style direct fixes)? — A (operator verbatim): **"design part a slice -> apply part a slice -> design part b slice -> so on."** → one phase, interleaved design/apply per surface, no `DECOMP2`.
- Q: Slice granularity — 8 surfaces as listed, fewer bigger rounds, or an operator-supplied list? — A: **8 surfaces as listed.**
- Q: Interview step — walk the surface first and present findings, or just ask with URLs? — A: **Walk it first, then ask.**
- Q: Where does the `t1` duplicate-key bug go? — A: **First slice of this phase** (`fix`, order 1, before any round).
- Q: Operator runtime for the walks and fidelity checks (no `## Operator Runtime` manifest existed yet)? — A: **`make stack-up` · 127.0.0.1:3000 + Tailscale URL · dev mode · Chrome desktop**; production build checked when behaviour differs.

## Notes

- Phase order 3.8: after P6 (3.7) and P7 (3.5), before P4 Ship & Submit (4).
- `create-phase` created only `P8.DECOMP` + `P8.REVIEW`; decomposition (including `P8.S1` and the per-surface pairs) is the `DECOMP` slice's job when the phase is executed.
- The `## Operator Runtime` manifest was seeded in the operations doc at phase creation (operator-confirmed, plan-approved) so the first real-browser slice does not stall on an absent manifest.
