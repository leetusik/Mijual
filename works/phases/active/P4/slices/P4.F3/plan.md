# P4.F3 — runbook R7: record the installed backup cron, its real firing time, and close open question 2

Fix slice cut by `P4.REVIEW` (finding 2). **Docs only**: one file, `deploy/runbook.md`, plus the
phase notebook. No code, no deploy, no box change, no commit. Tier: `slice-executor-mid`.

## What is wrong

`deploy/runbook.md` (read lines ~376–425 before editing) still says two things that were true on
2026-09-02 morning and are false now:

1. R7's paragraph **「Nightly backup — an open decision for `P4.S4`.」** presents the cron line as a
   suggestion ("a reasonable line is … **Ask; do not assume.**") and argues 「04:00 KST sits between
   the 19:30 evening pipeline and the 07:30 morning one」.
2. § *Open questions this runbook cannot answer*, item **2** 「The nightly backup cron — install it,
   or operator-run only? … the decision is the operator's」 is still open, and the closing sentence
   「Both are on the phase's `## Operator Questions` list」 assumes both are open.

The facts (measured by `P4.S4` dispatch 3 and re-measured by `P4.REVIEW` on 2026-09-02; do not
re-derive, and do not ssh to the box — nothing here needs it):

- The operator decided **install it** (2026-09-02). `opc`'s crontab carries exactly one Mijual line,
  the second line in the crontab after changple2's 03:00 certbot entry:
  `0 4 * * * cd /home/opc/Mijual && /home/opc/Mijual/deploy/db/backup.sh >> /home/opc/Mijual/var/backup.log 2>&1`
- **The box's system clock is GMT** (`timedatectl` → `Time zone: GMT (GMT, +0000)`), while the app
  containers log in KST. So `0 4 * * *` fires at **04:00 GMT = 13:00 KST**, not 04:00 KST. That is
  still between the 07:30 and 19:30 KST pipeline collections, so there is no operational harm — the
  runbook's rationale is simply wrong about which gap it sits in. If the operator wants the run at
  04:00 KST the line is `0 19 * * *` (19:00 GMT); record that as the alternative, do not apply it.
- It has run: `deploy/backups/` on the box holds `mijual-20260902T040001Z.dump` (the first cron run,
  04:00:01 GMT, 30,356,321 B, mode 600) beside the manual `mijual-20260902T023220Z.dump` and the
  seed `seed-20260902T013142Z.dump`; `KEEP=14` rotation; log `var/backup.log`. Dumps hold reader
  emails and password hashes and stay on the box.

## Do

1. Rewrite R7's nightly-backup paragraph so it **describes what is installed**: the exact cron line
   (keep the fenced `cron` block), that it fires at 04:00 GMT = **13:00 KST** because the box is
   GMT, that this sits between the 07:30 and 19:30 KST collections, the first dump it produced,
   `KEEP=14`, the log path, and the one-line alternative for a 04:00 KST run (`0 19 * * *`). Drop
   「an open decision」 and 「Ask; do not assume」. Keep the paragraph's register — the runbook is
   terse and imperative.
2. Strike open question 2 the way question 1 was struck (`~~…~~ **ANSWERED: install it** (operator,
   2026-09-02) …`), stating the installed line, the GMT/KST fact, and the first cron dump. Rewrite
   the closing sentence 「Both are on the phase's `## Operator Questions` list」 — both are now
   answered; say where the record is (`phase.md` `## Operator Questions`, both marked DONE).
3. `grep -rn '04:00\|0 4 \* \* \*' deploy/` — fix every other mention that says or implies "04:00
   KST" (the review found none outside R7, but check `deploy/README.md`, `deploy/db/backup.sh`'s
   header comment and `deploy/edge/README.md`). Do not touch anything else in those files.
4. `phase.md`: append one `## Doc impact` line — `operations` — correcting the earlier
   `P4.S4` line: the cron fires at 04:00 **GMT** = 13:00 KST (box clock GMT), first cron dump
   `mijual-20260902T040001Z.dump`; tag `(P4.F3)`. Rewrite `## Now` (≤ 15 lines): `P4.F3` done,
   `P4.F2` next (the Cloudflare Web Analytics fix, which stops for an operator dashboard action),
   then the re-review; keep the freeze date and the gate-shut line. Do not touch the `## Slices`
   block. Do not add an Operator Question — nothing here needs a decision.

## Validate

- `grep -n 'open decision\|Ask; do not assume' deploy/runbook.md` → nothing in R7.
- `grep -n '13:00 KST' deploy/runbook.md` → present in R7 and in the struck question 2.
- `grep -rn '04:00 KST' deploy/` → nothing (the only 04:00 left is 「04:00 GMT」).
- `python3 scripts/workflow.py validate` → passes (the `oversized_doc_sections` warning is
  pre-existing).
- `git diff --stat` → only `deploy/runbook.md` (plus any file step 3 genuinely needed), `phase.md`,
  and this slice's `result.md`.

## Return

`result.md` verdict-block-first (status, summary, files_changed, validation, deviations, doc_impact
= the one line, doc_versions n/a, review_verdict n/a, walkthrough none, explain n/a). If the edit
turns out to need more than the runbook and the notebook, return `escalate` with what you found
rather than widening.
