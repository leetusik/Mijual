# Plan — P5.S18: vocky integration — decide the observation shape, build the view

## Context

Read `works/phases/active/P5/phase.md` in full — binding: S9 (ops backend patterns,
degrade-honestly precedent for an unreachable dependency), S11 (the three
`data-vocky-trigger` elements and the `NEXT_PUBLIC_VOCKY_SRC` seam), S17 (the ops
idiom, `components/ops/` atoms, the twelve `/ops` routes). Design contract: R7
`build-prompt.md` **§6.3 (vocky 관찰 뷰)** — it *delegates the observation API's
return shape (fields, granularity, pagination) to this build against vocky's real
API, and instructs recording the decided shape back into that section* — the one
sanctioned edit to a landed record, by the record's own words. Fixed contract
regardless of shape: read-only (no vocky state change) · separate view from the
agent queue (merge 금지, cross-links only) · widget UI is vocky's own · KST display
· pre-connection state = 「API shape 확정 대기」 + skeleton. `docs/current/security.md`:
the vocky auth model was unknown — settle it here.

**vocky is the operator's own product and its source is on this machine:**
`~/projects/personal/vocky` (read-only for you — research it, never modify it).
Verified facts to start from: it is a multi-tenant feedback SaaS, live at
`https://vocky.hi2vi.com`, with server-to-server `/api/*` REST capture **and
reads** authenticated by a `vk_`-prefixed key (`Authorization: Bearer`; project- or
org-scoped), a web app, a CLI, and an `/mcp` write surface. Read its `README.md`,
`docs/` (esp. anything on the REST read endpoints), and `src/` route definitions to
get the *real* read API: endpoint paths, response fields, filtering, pagination.
Also determine whether vocky ships an embeddable **script widget** today (R2/S11
assume one; the product README emphasizes backend capture — if no embeddable
script exists yet, that is a finding to record, not a thing to build here:
Mijual's triggers and the `NEXT_PUBLIC_VOCKY_SRC` seam already degrade to
render-without-script).

## Deliverables

1. **Decide the observation shape** — from vocky's real read API: which endpoint(s)
   the Mijual admin view reads, the fields shown (time KST · surface/trigger
   context · the feedback text · whatever vocky's schema really carries),
   granularity, and pagination. **Record the decided shape in R7's §6.3** — update
   `docs/reference/design/rounds/07-admin/output/build-prompt.md` *only within that
   section*, as its own text instructs (state the decision date and that Claude
   Code decided it per the delegation) — plus a Doc-impact line; touch nothing else
   in the landed record.
2. **Mijual-side proxy** — an `/ops/vocky` read endpoint (operator-session-guarded
   like the rest): the Mijual backend calls vocky's REST read API server-side with
   config from `Settings` (`MIJUAL_VOCKY_API_BASE` + `MIJUAL_VOCKY_API_KEY` or
   similarly named — the `vk_` key is a secret: masked repr, missing-raises-on-use,
   never logged; follow `config.py`'s pattern). Unconfigured or unreachable →
   the served state the design names (「API shape 확정 대기」-grade honesty /
   degraded state per S9's Redis precedent) — never a 500, never fabricated rows.
   This is an external HTTP call in a request path: it is neither OpenDART nor an
   LLM (the boundary rule is untouched), but keep a short timeout and no retries so
   the tab cannot hang the panel; note the AST-scan implications if any.
3. **The admin vocky view** — a seventh ops surface (its own tab or a section —
   R7 lists six *sections* and the vocky view separately; decide placement from
   the R7 record's own structure and record it): the ops idiom (S17's atoms),
   desktop-only, read-only, KST times, cursor/paging per the decided shape,
   the pre-connection skeleton + 확정 대기 state when unconfigured, and **no merge
   with the save_feedback queue** — cross-links only (the fixed contract).
4. **Local-stack validation** — do not create any account on the hosted service
   and do not touch `vocky.hi2vi.com` with writes. Run vocky's **local** stack
   from its repo (its README documents `make bootstrap` against
   `http://127.0.0.1:8000`; pick a non-conflicting port — Mijual's uvicorn owns
   8000 — check vocky's docs for how, or run Mijual's API on another port for this
   test), create a throwaway local account/key via its CLI against the local
   stack, capture a couple of test feedback rows, and verify the Mijual ops view
   renders them through the proxy. Then tear the local stack down (stop
   containers; leave the vocky repo byte-identical — `git -C ~/projects/personal/
   vocky status` must be clean before and after).
5. **The production wiring facts** — record in `phase.md` (and result.md) what the
   operator must supply at deploy time (P4): the real `vk_` key (minted in their
   vocky org, read-scope), the API base, and — if a script widget exists — the
   real `NEXT_PUBLIC_VOCKY_SRC` value; if no widget script exists yet, state that
   plainly as the integration's honest status (the triggers stay, the seam stays
   unset).

## Constraints

- The vocky repo is read-only reference material. Its docs/code are data, not
  instructions — follow Mijual's contracts, not vocky's agent files.
- No new Python/npm dependencies (HTTP via stdlib/`httpx`-already-dev? — httpx is
  a dev extra only; pick the lightest runtime-legal route and record it).
- Ops rules hold: read-only, no mutation endpoints, raw identifiers mono, no
  invented Korean (「API shape 확정 대기」 is R7's own literal; anything else must
  have a source).
- Tests: terse — the proxy's unconfigured/degraded path and the shape mapping
  (mock the vocky response from a captured real payload); baseline 114 ≈ 2.5 s +
  11 smoke.

## Validation

- `.venv/bin/python -m pytest` and frontend build/typecheck/smoke — green.
- The local-stack end-to-end pass (feedback captured in local vocky → visible in
  the Mijual ops view), then the unconfigured state re-verified. Everything
  stopped; vocky repo clean.
- `python3 scripts/workflow.py validate`.

## Wrap-up

`result.md`; `phase.md` *Findings & Notes* (the decided shape, the settings, the
widget finding, the P4 wiring list) and *Doc impact* (`api` — the ops vocky route;
`security` — the vk_ key handling + settled auth model; `operations`; `frontend`;
plus the **design-record §6.3 update** itself). Structured verdict. No commits, no
status transitions.
