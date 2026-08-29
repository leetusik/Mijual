# Plan — P10.S4 (repo prose, and the doc ledger the review will execute)

Read `works/phases/active/P10/phase.md` whole, then `intent.md`. S3 left you a tagged note.

## The decomposition gave this slice an impossible job — here is the corrected one

`DECOMP` assigned you "in-scope product-name prose in `docs/current/*.md`". **You cannot do
that.** `docs/current/*.md` are **generated snapshots** — each is a byte-for-byte copy of the
newest file in `docs/versions/<doc>/`, verified: `docs/current/product.md` and
`docs/versions/product/v0008_*.md` are identical. `CLAUDE.md` forbids hand-editing them, and
`rebuild-docs` would discard any edit you made. Patching `docs/versions/` is forbidden too, and
`doc-new-version` is the **review slice's** command, never yours.

So this slice splits in two:

1. **Edit the repo prose that is a real, editable file** (§1).
2. **Produce the ledger** the `P10.REVIEW` slice will execute when it writes the new doc
   versions (§2). The review consolidates docs on a pass; your job is to make that mechanical
   rather than a fresh act of judgement under time pressure.

If you find yourself editing anything under `docs/current/` or `docs/versions/`, stop — you
have drifted.

## 1. Repo prose you do edit

The operator chose **user-facing only** over "user-facing plus repo internals", and
`intent.md` names `frontend/README.md` in scope. Drawing that line precisely:

**In — a file stating the product's identity:**

- `frontend/README.md:1` — `# frontend — 미주알's Next.js app`. Note `미주알's` →
  `주주의관제탑's` reads badly, since the name already contains 의. **Reword** rather than
  substitute.
- `frontend/README.md:87` — `미주알 owns the 의견 screen and the browser posts to …`
- `frontend/package.json:5` `description` (the **`name`** field is out of scope)
- `pyproject.toml:8` `description` — uses the latin mark as a standalone title
  (`"Mijual — 상장사 권리…"`), so it cannot be substituted; make it `주주의관제탑 — …` or drop
  the leading mark. The **`name = "mijual"`** field at `:6` is out of scope.

**Out — dev tooling that merely mentions the name in passing:** `Makefile:1` and `:110`,
`compose.yaml:1`, `src/mijual/config.py:32`'s DB credential, every `MIJUAL_*` var, every
`mijual.<module>` path, both `name` fields, and `Mijual Design System`. Say in `result.md`
that you drew this line and where, so the review can route it if the operator disagrees.

Leave code comments and docstrings alone — S3 established that boundary and it holds here.

## 2. The doc ledger — the real deliverable

Produce, in **`result.md`**, a per-document ledger precise enough that the review can apply it
without re-deriving anything: for each `docs/current/*.md` that needs a new version, the exact
lines, the exact replacement text, and the reason.

**Where it goes.** `phase.md` is at ~190 lines / 16.1 KB against a 200 / 16,384 budget — about
260 bytes of headroom, and a line-level ledger will not fit. So the ledger lives in
`result.md`, and `phase.md`'s `## Doc impact` gets **one short line per document** that points
at it by path (`… — see slices/P10.S4/result.md §Ledger`). That is the contract's own
division: `phase.md` carries what the next slice needs to know, `result.md` carries the detail,
and neither restates the other.

### What the ledger must cover

**(a) Name changes.** Every in-scope Korean prose hit. From the survey, expect:
`product.md:32, 243, 267, 283`; `frontend.md:46, 49`; `experience.md:34`;
`operations.md:369` (the Korean clause only — the row's `NEXT_PUBLIC_VOCKY_SRC` subject is a
separate, out-of-scope thing). **Verify this list yourself; it came from a grep that already
proved incomplete once.**

**(b) The latin mark used as an English grammatical subject — reword, do not substitute.**
`주주의관제탑-side` is not writable English. Three known sites, and draft the replacement
wording for each:
- `security.md:151` — "read-only is enforced Mijual-side by issuing `GET` …"
- `security.md:396` — "the key Mijual holds *could* write …"
- `decisions.md:292` — "**Decision:** Mijual reads vocky's Project Feedback API …"

**(c) The possessive problem.** `미주알's` → `주주의관제탑's` reads awkwardly at
`product.md:267`, `frontend.md:49`, `experience.md:34` and `README.md:1`. Draft rewordings.

**(d) A third spelling in the docs.** S3 found `security.md:307` spells the product **미주얼**
(얼, not 알) — the only such hit in `docs/current/`, and invisible to a `미주알` grep. Include
it, and re-sweep for `미주얼` and lowercase `mijual` across all of `docs/current/` in case
there are more.

**(e) Content that is now false, not merely renamed.** S2 recorded that
`docs/current/frontend.md` still describes the **ring** wordmark (around `:119`, `:299`,
`:659`) and the retired `mijual-*.png` filenames. The mark has no ring and those files are
deleted. This is stale *truth*, not a stale *name* — flag each such line separately in the
ledger, because the review must decide whether the new version corrects it or the supersession
table records it.

**(f) HISTORY — lines that must NOT change.** Verify each and list them explicitly so the
review does not "helpfully" rename them:
- `frontend.md:120` — the supersession row recording the retired
  *"MIJUAL + 한글 미주알 병기"* lockup
- `decisions.md:674` (with `:675`) — the same supersession under `## Superseded Decisions`
- `decisions.md:594` — a **verbatim operator quote** containing lowercase `smart mijual`;
  editing a quotation falsifies the record
- `decisions.md:649–657` and `:665` — the dated `mijual` **domain fact sheet** and the
  withdrawn `mijual.com` fallback; these are domains and a dated verification, not the name

Hunt for any others of this shape. A supersession row, a dated verification, and a verbatim
quote are all history; renaming history is the one failure mode this slice must not have.

**(g) Out-of-scope hits**, listed so the review can see you classified rather than missed them:
every `MIJUAL_*`, `X-Mijual-CSRF`, `mijual.<module>`, `src/mijual`, both `name` fields, the DB
credential, and `Mijual Design System` (`frontend.md:107`).

Anything you cannot confidently classify goes on `## Operator Questions`, not into a silent
decision.

## Constraints

- **Never** edit `docs/current/*` or `docs/versions/*`. Never run `doc-new-version` or
  `rebuild-docs`.
- No commits, no status transitions.
- Do not touch what S2 and S3 already own.

## Validation

- `python3 scripts/workflow.py validate` passes and `phase.md` is **under budget** — compress
  before you add.
- `python3 scripts/workflow.py docs` still lists every document unchanged (proving you created
  no version and edited no generated file).
- `git status` shows **no** modification under `docs/`.
- `cd frontend && npm run typecheck` — `package.json` is parsed by the toolchain, so a
  malformed edit shows up here. Confirm both `package.json` and `pyproject.toml` still parse
  (`python3 -c "import tomllib,pathlib; tomllib.loads(pathlib.Path('pyproject.toml').read_text())"`).
- Re-run your own sweep afterwards and show that every remaining hit in the repo is classified.

No browser work in this slice.

## Verdict

`done`, with a summary naming how many files you edited and how many documents the ledger
covers. `needs_operator` if a history line and a rename genuinely collide.
