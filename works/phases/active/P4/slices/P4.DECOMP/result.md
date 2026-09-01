# P4.DECOMP — result

- **status:** done
- **summary:** Cut P4 into eight bare middle slices (S1→S8, all `high`) in the plan's forced order — deploy leads, documents close — promoted D7 → `P4.S2`, D15 → `P4.S4` and D5 → `P4.S5`, and rewrote `phase.md` from the legacy template into the current notebook shape carrying the phase's decisions, five operator questions and the per-slice constraint blocks.
- **files_changed:**
  - `works/phases/active/P4/phase.md` (rewritten)
  - `works/phases/active/P4/slices/{P4.S1,P4.S2,P4.S3,P4.S4,P4.S5,P4.S6,P4.S7,P4.S8}/slice.json` (created)
  - `works/phases/active/P4/slices/{P4.S2,P4.S4,P4.S5}/plan.md` (created by `promote-deferred`, engine-written deferred context only — see *Deviations*)
  - `works/deferred/promoted/{D5,D7,D15}/` (moved out of `open/`)
  - `works/phases/active/P4/slices/P4.DECOMP/result.md` (this file)
  - regenerated: `works/backlog.md`, `works/deferred.md`, `works/index.json`, `works/state.json`
- **validation:**
  - `python3 scripts/workflow.py validate` → **passed** (`Workflow validation passed.`, exit 0)
  - `python3 scripts/workflow.py next` → `next_slice=P4.S1` ✅
  - `works/backlog.md` lists all eight new slices with the intended kinds ✅
  - `phase.md` = **124 lines / 16383 bytes** against the 200-line / 16384-byte budget ✅ (see *Notes on the budget*)
  - `intent.md` untouched by this slice; its verbatim block is byte-identical ✅
- **deviations:** three, all forced by engine mechanics or by the notebook's own template version — detailed below.
- **doc_impact:** none. `P4.DECOMP` changed no durable truth. (It *found* one durable-truth gap — the dev-only `## Operator Runtime` — but that is `P4.S4`'s change to make, and it is recorded as a note for S4, not as a doc-impact line here.)

---

## The slice set as created

| Order | Slice | Kind / risk | depends_on | Promoted job |
|---|---|---|---|---|
| 1 | `P4.S1` Containerize | implementation / high | — | — |
| 2 | `P4.S2` Real `Mailer` over SMTP + D-day send path | implementation / high | S1 | **D7** |
| 3 | `P4.S3` Deploy artifacts (vhost, deploy/rollback, runbook) | implementation / high | S1 | — |
| 4 | `P4.S4` Execute the deploy + Cloudflare | implementation / high | S3 | **D15** |
| 5 | `P4.S5` SEO | implementation / high | S4 | **D5** |
| 6 | `P4.S6` Smoke suite + uptime | qa / high | S4 | — |
| 7 | `P4.S7` 첨부1 공모전 기획서 | docs / high | — | — |
| 8 | `P4.S8` 첨부2 기능명세서 | docs / high | S4, S5 | — |

The cut is the plan's, unchanged. Every folder is bare (`slice.json` only) except the three the engine touched — no `plan.md` was authored for any of them.

`depends_on` is my addition (the plan did not specify it). It is advisory and `validate` only checks that the ids exist, but it records the real graph, and it makes one thing explicit that the plan left implicit: **`P4.S7` depends on nothing.** See *Proposals*.

### Commands run, in this order

```
promote-deferred D7  --phase P4 --slice P4.S2 --name "…" --kind implementation --risk high --order 2 --depends-on P4.S1
promote-deferred D15 --phase P4 --slice P4.S4 --name "…" --kind implementation --risk high --order 4 --depends-on P4.S3
promote-deferred D5  --phase P4 --slice P4.S5 --name "…" --kind implementation --risk high --order 5 --depends-on P4.S4
new-slice --phase P4 --slice P4.S1 …  (order 1)
new-slice --phase P4 --slice P4.S3 …  (order 3, depends-on P4.S1)
new-slice --phase P4 --slice P4.S6 …  (order 6, qa,   depends-on P4.S4)
new-slice --phase P4 --slice P4.S7 …  (order 7, docs)
new-slice --phase P4 --slice P4.S8 …  (order 8, docs, depends-on P4.S4 P4.S5)
rebuild ; validate ; next
```

**Sequencing rationale.** `promote-deferred` calls the same `create_slice` as `new-slice` (`scripts/workflow.py:1962`), and `create_slice` hard-errors on an existing folder (`slice already exists`, line 1001). So a promotion can only ever *create* its target slice, never attach to one. The promotions therefore had to run **first**, each creating the slice it lands in; the five slices with no promoted job were created afterwards with `new-slice`. `--name` was passed on every promotion so the slice carries the plan's name rather than the deferred job's title. No duplicate or mis-ordered slice resulted; the final order is 1–8 with `P4.REVIEW` at 9999.

---

## D15 — the judgment call, and what I decided

**Decision: promoted into `P4.S4`.** Its trigger is literally *"Before P4 Ship & Submit"*, and this phase is what makes the `/ops` login page publicly reachable. Two of the four rules rendering as 11px text under the login button describe the **security posture** (uniform + constant-time failure; credential rotation from env/secrets) — not a credential leak, but not text to leave on a public login door either. It is small, and `P4.S4` is the last slice before public exposure, so landing it there means the text is gone in the image that first serves the public origin rather than one release later.

Two things I weighed and want on the record:

1. **S5 would have been the better *topical* fit** — it is the reader-chrome/copy slice and it is also where `/ops` gets `noindex`. But S5 is ordered *after* the deploy (SEO needs the real origin), so putting D15 there leaves the text publicly visible across the S4→S5 window. And mechanically it was impossible anyway: `P4.S5` is created by D5's promotion, so a second promotion into it would have hit the same `slice already exists` error.
2. **It is a copy decision, not a cleanup.** Removing R7 record text drops a designed element, so it needs the operator's literal approval — `P4.S4` already stops `pending` for the Cloudflare account actions, which is the natural window to raise it. It is filed in `phase.md`'s `## Operator Questions` so the review cannot pass without routing it.

---

## Deviations from `plan.md`

**1. D23 could not be promoted, and stays deferred.** The plan asked for D7 **and** D23 into `P4.S2`. The engine cannot do that: `promote-deferred` only creates a slice, so only one of the two could land there. I promoted **D7** and left **D23** in `works/deferred/open/D23/`.

Why D7 and not D23: D7 is a measured correctness bug (`PUT /portfolio/notifications` read-then-insert → `UniqueViolation` on `uq_notification_pref_account`) with no other forcing mechanism, and its `brief.md` — which `promote-deferred` copies into the slice's `plan.md` — carries the traceback detail the S2 executor wants. D23 is a **copy re-signature**, and the phase already routes all mail copy to the acceptance gate for literal operator approval (intent point 10), so it surfaces there whether or not it is a promoted job. It is now recorded three ways so it cannot be lost: a `## Decisions` line, an `## Operator Questions` entry, and a note tagged for `P4.S2`.

*For the orchestrator:* once `P4.S2` lands with a re-signed subject, the clean close is `drop-deferred D23 --reason "landed inside P4.S2"` — your command, not mine.

**2. `phase.md` was rewritten into the current template shape, not just filled.** P4's notebook was still on the **pre-v32 template** (`## Context` / `## Decomposition` / `## Findings & Notes` / `## Constraints` / `## Open Questions`) with **no `<!-- slices:begin -->` / `<!-- slices:end -->` markers at all**. `refresh_phase_md_slices` (line 663) returns untouched when the markers are absent — deliberately, so legacy notebooks are a silent no-op — so P4 would have run the whole phase with no generated slice table. I rewrote it to `works/templates/phase.md`'s current section set and added the marker pair; `rebuild` then spliced the table. I wrote the markers and the surrounding sections only; the eleven generated rows between them are the engine's.

**3. `phase.md`'s `## Objective` was resynced to `phase.json`.** The heading still carried the stale objective (deck, video, daker.ai, `ssh h`); `phase.json` had already been corrected by the orchestrator this session. `## Objective` in the notebook is not generated, so I brought it in line with the corrected `phase.json` (compressed to fit the budget). No state file was hand-edited.

**Not a deviation, but worth flagging:** `promote-deferred` **writes a `plan.md`** into its target slice — `## Promoted Deferred Context` followed by the job's `brief.md` (lines 1966–1971). `P4.S2`, `P4.S4` and `P4.S5` therefore have a non-empty `plan.md` that I did not author and that contains **no plan**, only the deferred job's context. That is engine behaviour, not me pre-filling another slice's plan. The orchestrator should write each slice's real plan over/around it at that slice's turn and keep the promoted block.

---

## Findings the plan did not anticipate

1. **The `edge` repo path in the plan is one level short.** The plan says `~/projects/personal/edge/conf.d/…`; that directory does not exist. The conf tree is **`~/projects/personal/edge/edge/conf.d/`** — the repo has an inner `edge/` holding `compose.yml`, `conf.d/`, `certs/`, `validate.sh`, `stage.sh`, `deploy.sh`, `cutover.sh`, `README.md`. Verified present: `00-default.conf`, `changple-web.conf`, `changple5.conf`, `hi2vi.conf`, `knowledge.conf`, `vocky.conf`. Every file the plan names in `hi2vi_web` also exists as named. The doubled path is called out explicitly in `phase.md` so S3/S4 do not lose an hour to it.

2. **The repo already has a scheduler, and it changes S1's shape.** `operations.md` §*Schedule and Budgets*: `mijual.scheduler` is **Celery beat + worker on the compose Redis** (profile `scheduling`), with the beat schedule and the run-lock key declared exactly once in `mijual.beat`. Two consequences the plan's containerization bullet does not state: `compose.prod.yml` must carry **beat, worker and Redis**, not just API + web; and the D-day send in `P4.S2` is a **new beat task**, not a new scheduling mechanism. Both are now notes for S1 and S2. (A first grep for "scheduler/cron" in `src/` found nothing and I nearly recorded "there is no scheduler" — the scheduler is documented in `operations.md`, and the module name does not contain the words I searched for. Recording the dead end because the next reader might repeat it.)

3. **The `## Operator Runtime` manifest is dev-only and will block the review's gate.** It is filled (not `UNFILLED`), but it describes only `make stack-up` → `127.0.0.1:3010` / tailnet, plus `npm run build && npm run start` on the same port. It names **no production origin**. Since the phase will take `accept-gate --require` and the review must open the running product in the manifest runtime, `P4.S4` has to add `https://jujutower.com` and its access path to that section, with a Doc impact line. If it does not, `P4.REVIEW` is obliged to return `needs_operator` at gate stage 1. This is now a note tagged for S4 and REVIEW.

4. **`hi2vi_web/deploy/` has more than the plan lists** — alongside `deploy.sh` / `rollback.sh` / `runbook.md` / `monitoring/` there are `oracle-production-deploy-remote.sh`, `github-actions-production-deploy.sh` and an `edge/` directory. S3 should look at the Oracle-specific script before writing its own; I did not read them (out of this slice's scope) and only note that they exist.

---

## Proposals (flagged, not taken)

**On the eight-slices-in-five-days concern.** I looked for a materially cheaper cut and did not find one that still delivers the ten confirmed intent points. The merges I considered and rejected: S3+S4 (authoring in-repo vs. executing on a live shared box — keeping them split is what lets a bad vhost fail `nginx -t` before it reaches the box); S6 into S4 (the deploy slice is already the `pending`-heaviest, and the smoke suite is real test authoring); S7+S8 (they have *different* dependencies — see below — so merging them would couple 첨부1 to the deploy for no reason). The deadline is also not binding: the operator is not submitting, so 09-07 is a design input.

**The one lever I would pull, and did not.** `P4.S7` (첨부1 공모전 기획서) has **no dependency on the deploy** — only 첨부2 §5 needs the live URL and its 관련 화면 screenshots. The plan's own "honest note on scale" says the order to protect is *documents → deploy → SEO → monitoring*, yet both documents sit last, behind a first production deploy onto a shared box. Since the documents are the operator's headline deliverable ("no submit, only prepare the document"), I would move `P4.S7` to **`--order 0.5`** so 첨부1 is finished before anything can stall. I left the order as planned because the dispatch asked me to preserve the plan's ordering rationale and to propose rather than take a change like this; `--order` accepts fractions, so it is a one-command change at any point. The option is recorded in `phase.md`'s `## Decisions` and `## Now` so a later slice can act on it.

---

## Notes on the budget

`phase.md` finished at **16383 / 16384 bytes** — one byte under, and 124 / 200 lines. It took five compression passes; the honest read is that this phase is unusually constraint-dense (a first production deploy onto a multi-tenant box, plus SEO from zero, plus two authored documents) and the 16 KB ceiling is genuinely tight for it. What I did to fit:

- Line 3 links `slices/P4.DECOMP/plan.md`, which holds every constraint block verbatim and is committed and immutable. Anything I compressed is recoverable there in one read.
- Cut outright: the standalone "reference repos" block (every path in it is already named inside the mail / SEO / no-harm / uptime blocks), the 양식 section enumerations (verbatim in `docs/reference/challenge/submission/README.md`), the enumerated nginx streaming directives (the instruction is "copy the `/bff/` block wholesale", so listing them invites hand-assembly), the written-out gate walkthrough, and the one `## Decisions` line that duplicated a note.
- Kept whole, deliberately: every outage-grade fact (the three `vocky.conf` rules, the Cloudflare 524 cap and stand-up order, the eight env vars, the two-table schema bootstrap, the SEO build-arg assertion trap), all five operator questions, and the measured numbers with their caveats.

**The notebook is at its ceiling, so the next slices must actually consume their notes.** Each tagged block is addressed to specific slices; a slice that finishes should delete the block written for it rather than only appending. If a later slice needs headroom and has nothing to drop, the SEO and documents blocks are the ones whose full text is most cheaply re-read from `P4.DECOMP/plan.md`.

## What I did not do

No product code (this is a decomposition slice). No commit, no `start-slice` / `finish-slice` / `set-slice-status` / `set-phase-status` / `accept-gate` / `review-phase` / `doc-new-version` / `defer-job` / `drop-deferred`. No `plan.md` authored for any created slice. Nothing inside the `## Slices` marker block was hand-edited. The two sibling repos were read (directory listings only) and not modified.

**Still owed by the orchestrator:** `accept-gate P4 --require` right after `finish-slice P4.DECOMP` — a public deployed site, new SEO metadata and notification email are all operator-visible, so the plan is right that there is no judgment left in it.
