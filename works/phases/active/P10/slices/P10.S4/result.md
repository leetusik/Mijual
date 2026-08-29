# Result — P10.S4 (repo prose, and the doc ledger the review will execute)

- **status:** `done`
- **summary:** Renamed the product in the **4 editable repo-prose sites** (`frontend/README.md:1,87`,
  `frontend/package.json:5` `description`, `pyproject.toml:8` `description`) and produced the
  **§Ledger** below — a line-level, per-document instruction set covering **6 `docs/current` documents**
  that `P10.REVIEW` executes when it writes the new versions. Edited **nothing** under `docs/`;
  all 11 `docs/current/*.md` are still byte-identical to their newest `docs/versions/` file.
- **files_changed:**
  - `frontend/README.md`
  - `frontend/package.json`
  - `pyproject.toml`
  - `works/phases/active/P10/phase.md`
  - `works/phases/active/P10/slices/P10.S4/result.md`
- **validation:**
  - `python3 scripts/workflow.py validate` — **pass** (2 pre-existing warnings, `P9.S1` / `P9.S1B`
    unknown kind `research`; unrelated to this slice, present before it)
  - `python3 scripts/workflow.py docs` — **pass**: 11 documents, every `latest=` string identical to
    the pre-edit run. No version created.
  - `git status --porcelain -- docs/` — **pass**: 0 lines. Nothing under `docs/` modified.
  - `cmp docs/current/<doc>.md docs/versions/<doc>/<newest>` for all 11 docs — **pass**: 11/11
    IDENTICAL (this also re-verifies the plan's premise beyond `product.md`)
  - `cd frontend && npm run typecheck` (`tsc --noEmit`) — **pass**, clean, no output
  - `python3 -c "import tomllib,pathlib,json; ..."` — **pass**: `pyproject.toml` parses,
    `project.description` reads `주주의관제탑 — 상장사 권리(…)`; `frontend/package.json` parses,
    `description` reads `주주의관제탑 Next.js frontend — …`, `name` still `mijual-frontend` (untouched)
  - Post-edit sweep for `미주알` / `미주얼` / `Mijual` / `MIJUAL` / `mijual` across the whole tracked
    tree — **pass**: every remaining hit is classified in §Out-of-scope inventory below
- **deviations:** two, both to follow the plan where it diverges from `DECOMP` — see §Deviations.
- **doc_impact:** 7 lines appended to `phase.md` `## Doc impact` (one per affected document plus one
  for the repo prose), each pointing at this file's §Ledger by path.
- **doc_versions:** n/a (non-review slice — ran no `doc-new-version`, no `rebuild-docs`)

---

## 1. What I edited (§1 of the plan)

Four sites in three files. Everything else that spells the name is classified, not touched.

| file:line | before | after | why this wording |
|---|---|---|---|
| `frontend/README.md:1` | `# frontend — 미주알's Next.js app` | `# frontend — the 주주의관제탑 Next.js app` | **Reworded, not substituted.** `주주의관제탑's` stacks an English genitive on a name that already contains the Korean genitive 의 — "of-shareholders-control-tower's". Dropping the possessive for an article keeps the title's shape and reads. |
| `frontend/README.md:87` | `미주알 owns the 의견 screen and the browser posts to …` | `주주의관제탑 owns the 의견 screen and the browser posts to …` | Plain subject position, no possessive, no compound — a straight swap is correct here. |
| `frontend/package.json:5` | `"description": "미주알 Next.js frontend — built from the signed P3 design record …"` | `"description": "주주의관제탑 Next.js frontend — …"` | Attributive slot, same shape. `"name": "mijual-frontend"` at `:2` deliberately **untouched** (intent.md excludes it). |
| `pyproject.toml:8` | `description = "Mijual — 상장사 권리(…) 수집·추출·검증 파이프라인"` | `description = "주주의관제탑 — 상장사 권리(…) 수집·추출·검증 파이프라인"` | The latin mark sits in a **standalone title slot**, not inside English grammar, so the Korean name substitutes cleanly. `name = "mijual"` at `:6` deliberately **untouched**. |

Code comments and docstrings were left alone throughout, per S3's boundary. That includes the 28
sites across `frontend/` and `src/mijual/` that still spell 미주알 / 미주얼 / Mijual — listed under
§Out-of-scope inventory, and already flagged to the review by S2's standing note.

### Where I drew the "user-facing" line, and the one place it is contestable

**In:** a file that *states the product's identity* — a README title, a package description.
**Out:** dev tooling that mentions the name *in passing* — `Makefile:1` (`# Mijual dev stack.`),
`Makefile:110` (`@echo "── mijual dev stack ───…"`), `compose.yaml:1`
(`# Local development infrastructure for the Mijual pipeline.`).

`DECOMP`'s note put `Makefile:1` **in** scope; this slice's `plan.md` §1 explicitly puts it **out**.
I followed the plan. But the two disagree, and one fact cuts against "in passing":
`make stack-status` **prints** `── mijual dev stack ───` to the operator's own terminal, so it is
weakly operator-visible in the runtime the manifest names. Left unchanged and routed as an operator
question rather than silently decided either way.

---

## 2. §Ledger — what `P10.REVIEW` executes

**Scope of this ledger: 6 documents need a new version for name/brand reasons.**
`api.md`, `architecture.md`, `backend.md`, `data.md`, `qa.md` need **no rename** — every `mijual`
in them is a module path. (`api.md` / `architecture.md` / `backend.md` still carry P10.S3's separate
"Doc impact" additions, and `qa.md` gets the review's own `## Regression Checklist` append; neither
is this slice's business.)

Line numbers are against `docs/current/*.md` **as of this slice**, verified by `sed -n '<n>p'`, and
are stable because nothing under `docs/` changed. The corresponding edit target is
`doc-new-version`'s returned `edit_path`, not these files.

Categories follow the plan: **(a)** name change · **(b)** latin mark as an English grammatical
subject, reword · **(c)** possessive problem · **(d)** the third spelling · **(e)** content now
**false**, not merely stale · **(f)** **HISTORY — do not change**.

---

### 2.1 `product.md` — 4 changes, all names

| line | category | current | recommended |
|---|---|---|---|
| `32` | (a) | `**미주알** watches Korean disclosure (DART) for *shareholder rights with a deadline* — rights that` | `**주주의관제탑** watches Korean disclosure (DART) for *shareholder rights with a deadline* — rights that` |
| `243` | (a) | `- No trading, no brokerage integration, no purchase or exercise flow — 미주알 informs; the user acts` | `… — 주주의관제탑 informs; the user acts` |
| `267` | **(c)** | `  mistyped address and an unmatched path all render 미주알's own Korean not-found, which **still says` | `  mistyped address and an unmatched path all render the product's own Korean not-found, which **still says` |
| `283` | (a) | `- **계정 삭제 states its consequence only while armed**, and 미주알 owns its 의견 screen — a reader's` | `…, and 주주의관제탑 owns its 의견 screen — a reader's` |

- `:32`, `:243`, `:283` are **subject position with no possessive** — a straight substitution is
  correct, and `:32` establishes that this doc set already uses a bold Korean name as an English
  subject, so the pattern is not new.
- `:267` is the possessive problem. Recommended `the product's own`; the alternative if the review
  prefers the name present is `주주의관제탑's own`, which is grammatical English but reads as a double
  genitive to a Korean reader. One choice, applied consistently across `:267`, `frontend.md:49` and
  `experience.md:34` — they are the same construction three times.
- **Additive, not a rename:** S1's standing "Doc impact" line says the symbol-mark / favicon gap is
  **open again**. `product.md` contains no favicon or wordmark claim at all (verified by grep), so
  that is an *addition* the review makes here or in `frontend.md`, not a line to correct. The
  existing gap statements live at `frontend.md:119` and `:659` — see 2.2.

### 2.2 `frontend.md` — 3 names, 3 false-content sites, 1 history row, 1 out-of-scope

**Names**

| line | category | current | recommended |
|---|---|---|---|
| `46` | (a) | `- **미주알 owns its 404.** \`app/not-found.tsx\` + \`RequestedPath.tsx\` render the Korean not-found for` | `- **주주의관제탑 owns its 404.** …` |
| `49` | **(c)** | `  \`NEXT_PUBLIC_VOCKY_SRC\` are deleted; \`components/chrome/Feedback.tsx\` is 미주알's own 의견 surface` | `  … is the product's own 의견 surface` |
| `675` | (a) | `  \`이메일\`, \`비밀번호\`, \`계정 이전\`, \`© 미주알\`); and the sample's signed **4건** subline above **five**` | `  \`이메일\`, \`비밀번호\`, \`계정 이전\`, \`© 주주의관제탑\`); …` |

`:675` deserves a sentence, because it looks like history and is not. It sits under
**"Copy the record does not contain"** — i.e. it lists strings the *build composes* and the design
record does **not** hold. P10.S2 actually changed that build string: `components/chrome/copy.ts`
now exports `COPYRIGHT_KO = "© 주주의관제탑"` (verified in the file, with S2's own comment
"the record's `© 미주알` became `© 주주의관제탑`, same shape, same symbol"). So renaming it makes the
doc true; leaving it makes the doc false. This site was **not** in the plan's expected list — my sweep
found it.

**(e) Content now false**

- **`:119`** — supersession-table row:
  `| R1 "no favicon-scale symbol mark" gap | **R2** | ring logo assets (\`mijual-logo-ring-{charcoal,white}.png\`) |`
  This is a **row in the design-record supersession chain**, so its own text is history: R2 really did
  close that gap with those assets. But the effect is now false — P10 deleted them and re-opened the
  gap. **This is the "correct it or record it" decision the plan hands the review. My recommendation:
  record it** — leave `:119` verbatim and append one new row to the same table:

  ```
  | R2 ring logo assets (`mijual-logo-ring-{charcoal,white}.png`) | **P10 (operator's mark)** | `juju-wordmark-{black,white}.png` — a Korean wordmark with a sparkle cluster and **no ring**; the favicon-scale gap is **open again** (the mark does not reduce to 32px) |
  ```

  Rationale: the table's whole contract is *"a round's landed record is immutable; later rounds
  supersede earlier ones"* (`:110–112`). Editing a row breaks that contract; adding one honours it.

- **`:299–302`** — false on **three** counts, not one:

  ```
  **The wordmark is the delivered `mijual-logo-ring-white.png` rendered height-constrained through a
  plain `<img>` — never `next/image`**, which would ship a re-compressed derivative of an asset that is
  never re-encoded. The five binary assets (two wordmark PNGs, two ring logos, `PretendardVariable.woff2`)
  are in the repo byte-for-byte and checksummed; **replacing one means a new export from the design
  project, never a local edit**.
  ```

  1. the filename is now `juju-wordmark-white.png`;
  2. **"five binary assets" is now four** — `frontend/public/assets/` holds
     `juju-logo-source.png`, `juju-wordmark-black.png`, `juju-wordmark-white.png`,
     `fonts/PretendardVariable.woff2` (verified by `find`);
  3. **"a new export from the design project, never a local edit" is now false** — the white variant
     *is* a local derivation (S1: alpha-preserving `+level-colors white,white` with
     `-define png:color-type=6`, verified **by pixel signature, never sha256**, because ImageMagick
     stamps `png:tIME`).

  Recommended replacement for `:299–302`:

  ```
  **The wordmark is the operator-delivered mark rendered height-constrained through a
  plain `<img>` — never `next/image`**, which would ship a re-compressed derivative of an asset that is
  never re-encoded. The four binary assets (`juju-logo-source.png`, the black and white wordmark
  derivations, `PretendardVariable.woff2`) are in the repo byte-for-byte and checksummed;
  **replacing an operator-delivered one means a new file from the operator, never a local edit** — the
  white variant is the one sanctioned exception, a repo-generated alpha-preserving recolor of the
  operator's own file, verified by pixel signature rather than file hash.
  ```

  The review should take the exact provenance wording from `frontend/public/assets/README.md`
  (rewritten by S1) rather than from this paraphrase — that README is the authority on the three
  provenance classes.

- **`:658–660`** — the `Open Questions` bullet:

  ```
  - ~~Binary assets~~ — **closed 2026-08-22** by the operator's export; all five are in the repo
    byte-for-byte and checksummed. There is still **no SVG wordmark and no favicon** — the ring PNG is
    2178×346 and re-encoding a delivered asset is not an implementation call.
  ```

  False: *"all five"*, and *"the ring PNG is 2178×346"* (the asset is gone; the natural pair is now
  **1213×319**). Still true: **no SVG wordmark and no favicon**. Recommended:

  ```
  - ~~Binary assets~~ — **re-closed 2026-08-30 (P10)** by the operator's new mark; the four in the repo
    are byte-for-byte and checksummed. There is still **no SVG wordmark and no favicon** — the natural
    wordmark pair is 1213×319, the mark does not reduce legibly to 32px (an open operator question),
    and re-encoding a delivered asset is not an implementation call.
  ```

**(f) HISTORY — do not change**

- **`:120`** — `| R1 lockup "MIJUAL + 한글 미주알 병기" | **R1 revision (operator)** | English wordmark **alone** |`
  A supersession row that records the retired lockup **by name**. Renaming it would assert the
  operator revised a lockup that never existed. **Verified in place; leave verbatim.**

**Out of scope in this document**

- `:107` — `("Mijual Design System")`, the Claude Design project's own name. `intent.md` excludes it
  explicitly. Leave.
- `:169` — `mijual.estimate.won`, a module path. Leave.

**Lookalikes a "ring" sweep must not touch** (checked, none is the brand):
`:203–207` the **AI 질문 launcher's Saturn ring** (a CSS-drawn ambient mark, "22px Saturn, rotating
band 4.5s, ring split front/back"); `:357` the hero's `.orbits` ring clip; `:507–529` `--focus-ring`.
The only brand-ring sites are `:119`, `:299`, `:301`, `:659`.

### 2.3 `experience.md` — 1 name, 2 false-content sites

| line | category | current | recommended |
|---|---|---|---|
| `34` | **(c)** | `  the gate-cost and 면책 sentences are **dropped, not relocated**. 의견 보내기 is 미주알's own screen` | `  … 의견 보내기 is the product's own screen` |
| `28` | **(e)** | `- **Chrome.** Two nav destinations (AI 질문 · 보유 종목) — 관제 현황판 *is* the ring wordmark, so the` | `- **Chrome.** … — 관제 현황판 *is* the wordmark, so the` |
| `102` | **(e)** | `- **Global chrome (R2):** 52px nav (white ring wordmark), mobile top bar + sheet menu, footer with the` | `- **Global chrome (R2):** 52px nav (white wordmark), mobile top bar + sheet menu, footer with the` |

- `:34` is the same possessive construction as `product.md:267` and `frontend.md:49` — decide once.
- `:28` and `:102` both sit in **descriptions of the current build** (`## Route / Screen Map`),
  not in a supersession chain, so deleting the word "ring" corrects them minimally and preserves the
  claim each is actually making (`:28`: the wordmark *is* the board's link; `:102`: the nav renders
  the white mark). The mark now has no ring — `intent.md` §Notes states this outright.
- `:102`'s `**(R2)**` attributes the *design source*. If the review would rather not restate an R2
  description, the alternative is
  `52px nav (white wordmark — R2's asset was the ring, retired in P10)`. My recommendation is the
  minimal deletion: the parenthetical describes what renders, and what renders has no ring.
- **These two sites were not in the plan's list** — my `ring wordmark` sweep found them.
- `:145` `mijual.calc.allotted_shares` is a module path — leave.

### 2.4 `operations.md` — 1 name, in one clause of one row

| line | category | current fragment | recommended |
|---|---|---|---|
| `369` | (a) | `… R8 deleted \`VockyTrigger\`, \`VockyScript\` and every \`data-vocky-trigger\`, and 미주알 now owns the 의견 screen (\`components/chrome/Feedback.tsx\` → \`POST /feedback\`). Do not reintroduce the variable` | `… and 주주의관제탑 now owns the 의견 screen (…). Do not reintroduce the variable` |

**Change the Korean clause only.** The row's subject is `~~\`NEXT_PUBLIC_VOCKY_SRC\`~~` — an env-var
name, out of scope — as is every other `MIJUAL_*` row in that table (`MIJUAL_API_ORIGIN`,
`MIJUAL_DEV_ORIGINS`, `MIJUAL_VOCKY_API_BASE` / `_KEY`, …). This slice touched nothing in
`## Operator Runtime`.

Note for the review: `operations.md` also carries S2's separate "Doc impact" line (the port-5433
`!override` workaround). Same document, unrelated change — fold both into one version.

### 2.5 `decisions.md` — 1 reword, and **5 history sites that must not move**

**(b) Reword**

| line | current | recommended |
|---|---|---|
| `292` | `- **Decision:** Mijual reads vocky's **Project Feedback API** server-side with a \`vk_\` key the` | `- **Decision:** this product reads vocky's **Project Feedback API** server-side with a \`vk_\` key the` |

This is the one line in the whole ledger where the rename and the record genuinely rub, so I am
classifying rather than deciding it silently. It is D-19's decision text, **dated 2026-08-22** — but
it is **not** a verbatim operator quote and **not** a supersession row, and it names the product as
the acting system, which is what changed. So: in scope, but **reword rather than substitute**.

Recommended `this product`, because it is name-neutral and stays true whatever the product is called —
and because the surrounding doc already prefers name-free phrasing for exactly this idea: D-19's own
heading at `:289` reads *"read-only is enforced **on our side**"*. The alternative, if the review wants
the name present, is `주주의관제탑 reads vocky's …` — grammatical, but it stamps the 2026-08-30 name onto
a 2026-08-22 decision.

**(f) HISTORY — verified in place, do NOT rename**

| line(s) | what it is | why it is untouchable |
|---|---|---|
| `594` | **verbatim operator quote** — `…This agent should be more like smart mijual` | Introduced at `:592` as *"Operator's framing, **verbatim** from the phase intent"*. The lowercase `mijual` is the operator's own word. Editing a quotation falsifies the record. |
| `649` | `## Reference — mijual domain fact sheet (verified 2026-08-19)` | A **dated verification** heading. The fact sheet is about domains carrying the old name. |
| `653–657` | the five rows `mijual.ai` · `mijual.kr` · `mijual.co.kr` · `mijual.io` · `mijual.com` | **Domain names plus a dated whois result.** Renaming them would assert availability facts about domains nobody ever checked. |
| `665` | `- \`mijual.com\` as a fallback domain, and any "watch it lapse" plan, is **withdrawn**.` | A `## Superseded Decisions` entry naming a **specific domain**, not the product. |
| `674–675` | `- **The MIJUAL + 한글 '미주알' 병기 lockup is superseded** by the operator's R1 revision: English` / `  wordmark alone.` | A supersession entry that records the retired lockup **by name** — the same content as `frontend.md:120`. |

**Additive, recommended (not a rename):** the fact sheet at `:649` is now a dated record about a
**retired** name, and nothing in the doc says so. One new `## Superseded Decisions` bullet closes both
that and the identity change without editing a single historical line, e.g.:

```
- **The whole latin identity is superseded by 주주의관제탑 (P10, operator).** The `MIJUAL` wordmark,
  the `MIJUAL OPS` bar mark and the name 미주알 are retired with **no romanized replacement**; the
  2026-08-19 `mijual` domain fact sheet above is preserved as a dated record of a name the product
  no longer uses.
```

Also out of scope in this document: `:350`, `:352`, `:353`, `:355` (`mijual.web`, `mijual.agent`,
`mijual.extract.client`) — module paths.

### 2.6 `security.md` — the third spelling, and 2 rewords

**(d) The third spelling** — this is the hit a `미주알` grep cannot see.

| line | current | recommended |
|---|---|---|
| `307` | `미주얼 has **two of three legs absent**: the corpus is public DART filings and the reader is` | `주주의관제탑 has **two of three legs absent**: the corpus is public DART filings and the reader is` |

Subject position, no possessive — a straight swap. **Re-swept and confirmed: `security.md:307` is
still the only `미주얼` anywhere in `docs/current/`** (the other 미주얼 sites in the tree are two code
comments, `src/mijual/agent/citations.py:19` and `instructions.py:130` — out of scope).

**(b) The latin mark as an English grammatical subject**

| line | current | recommended |
|---|---|---|
| `151` | `  can write), so read-only is enforced Mijual-side by issuing \`GET\` and nothing else *and* by a test` | `  can write), so read-only is enforced on this side by issuing \`GET\` and nothing else *and* by a test` |
| `396` | `  offers **no read-scoped credential**, so the key Mijual holds *could* write and read-only is` | `  offers **no read-scoped credential**, so the key this product holds *could* write and read-only is` |

`Mijual-side` is the clearest case in the phase: `주주의관제탑-side` is not writable English, so this
**must** be reworded. The replacement is not invented — the same document already says it twice:
`:397` ends *"read-only is enforced **on this side**"*, and `decisions.md:289` heads D-19 with
*"read-only is enforced **on our side**"*. Using `on this side` at `:151` makes the doc internally
consistent instead of introducing a fourth phrasing.

Out of scope here: `MIJUAL_SESSION_SECRET`, `MIJUAL_VOCKY_API_KEY` (`:145–146`), and the module paths
at `:27`, `:182`, `:189`, `:190`. Also note `src/mijual/web/vocky.py:32` carries the *same*
`Mijual-side` phrase in a docstring — classified out (code comment), not missed.

---

## 3. Out-of-scope inventory (§g of the plan) — classified, not missed

Every remaining hit in the tracked tree, by class:

| class | where | count / examples |
|---|---|---|
| `MIJUAL_*` env vars | `operations.md`, `security.md`, `frontend/README.md:83,88`, code | `MIJUAL_API_ORIGIN`, `MIJUAL_DEV_ORIGINS`, `MIJUAL_VOCKY_API_BASE`/`_KEY`, `MIJUAL_SESSION_SECRET`, `MIJUAL_OPS_ID`/`_PASSWORD` |
| `X-Mijual-CSRF` | api/security docs, `web/csrf.py` | header name — `intent.md` excludes it by name |
| `mijual.<module>` dotted paths | all 11 docs + all of `src/` + `tests/` | ~90 doc hits, e.g. `mijual.agent`, `mijual.estimate.won`, `mijual.web.app:app` |
| `src/mijual`, `mijual/web/` | `architecture.md:43,196,200`, `operations.md:214`, `api.md:322` | package paths |
| `mijual:lock:pipeline` | `operations.md:93,413` | Redis lock key |
| `/mijual` DB name | `DATABASE_URL` sites | local DB credential |
| both `name` fields | `frontend/package.json:2` `mijual-frontend`, `pyproject.toml:6` `mijual` | excluded by `intent.md` and by this plan |
| `"Mijual Design System"` | `frontend.md:107`, `frontend/public/assets/README.md:9` | the design project's own name — excluded by `intent.md` |
| retired asset **filenames** | `frontend.md:119` (history), `chrome/copy.ts:25` (comment), assets README | `mijual-logo-ring-*.png`, `mijual-*.png` — filenames, not the name |
| test fixture emails | `tests/test_web_auth.py:28`, `tests/test_web_portfolio.py:268` | `Reader@Mijual.KR`, `New@Mijual.KR` |
| absolute path in data | `evalset/labels.json:354` | `/Users/sugang/projects/personal/Mijual/evalset/sheet.csv` |
| dev-tooling banners | `Makefile:1`, `Makefile:110`, `compose.yaml:1` | out **per this plan**; routed as an operator question (see §1) |
| code comments & docstrings | 28 sites in `frontend/` and `src/mijual/` | out per S3's boundary; already flagged to the review by S2's standing note |
| brand-lookalike "ring" | `frontend.md:203–207,357,507–529` | the launcher's Saturn ring, the hero clip, `--focus-ring` — none is the brand |

---

## 4. Deviations from `plan.md`

1. **`Makefile:1` — plan vs. `DECOMP`.** `DECOMP`'s note in `phase.md` listed `Makefile:1` as
   in-scope repo prose; this slice's `plan.md` §1 lists it as out. I followed **the plan** and left it,
   but the plan's own reason ("merely mentions the name in passing") is weakened by `make stack-status`
   echoing `── mijual dev stack ───` to the operator's terminal. Recorded in §1 and routed to
   `## Operator Questions` so the review must dispose of it rather than inherit a silent choice.
2. **The ledger covers more sites than the plan predicted.** The plan warned its grep had proved
   incomplete; it had. Beyond the expected list I found and classified: **`frontend.md:675`**
   (`© 미주알`, a build-composed label S2 actually changed), **`experience.md:28` and `:102`**
   (two more "ring wordmark" descriptions), **`frontend.md:301`** ("five binary assets" — now four)
   and **`frontend.md:659`**'s asset-count/dimension claims. No predicted site turned out to be absent:
   every line number in the plan verified exactly.

Not a deviation, but worth stating: the plan's premise was verified **beyond** `product.md` —
all **11** `docs/current/*.md` are byte-identical to their newest `docs/versions/` file, so no
`docs/current` edit could have survived `rebuild-docs`.

---

## 5. What the review still has to decide (nothing here is decided silently)

1. **`frontend.md:119` — correct the row or add a superseding one.** I recommend adding (2.2).
2. **The possessive form, decided once** for `product.md:267`, `frontend.md:49`, `experience.md:34`.
   I recommend `the product's own`; the alternative is `주주의관제탑's own`.
3. **`decisions.md:292`** — `this product` (recommended) vs. `주주의관제탑` on a dated decision.
4. **`experience.md:102`** — minimal `ring` deletion (recommended) vs. restating R2's asset as history.
5. **The dev-tooling banners** (`Makefile`, `compose.yaml`) — operator question, on the list.
6. **Additive entries** the review may want: the P10 identity supersession bullet in `decisions.md`
   (draft in 2.5) and the re-opened favicon gap (S1's standing note; `product.md` has no such claim
   today, so it is an addition, not a correction).
