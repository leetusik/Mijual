# Labelling the evalset (P2.S9) — operator instructions

**The job.** Open `evalset/sheet.csv`, read each row's `extracted_value` against its
`quote` + `context`, and type one word in column **A (`label`)**. 344 rows over 99 filings.
Column **B (`corrected_value`)** is optional and free text — fill it only when you know what
the value *should* have been.

**The four labels** (type any of the forms, case does not matter):

| type | means | also accepted |
|---|---|---|
| `correct` | the value faithfully states what the cited text says | `c` `o` `맞음` |
| `wrong` | the value misreads the text, or names something that is not there | `w` `x` `틀림` |
| `partial` | partly right — one entry of several wrong, right date + wrong 취급처, a unit slip | `p` `부분` |
| `skip` | you cannot judge this row | `s` `?` `모름` |

**`partial` vs `wrong`:** if a user acting on the value would be *misled*, it is `wrong`;
if they would be *correct but under-informed*, it is `partial`. `skip` is not a failure —
please use it rather than guessing, because a guess enters the measurement as a judgement.

**What you are judging against.** The `quote` is what the model claims the document says,
and `context` is that quote back in place (`【…】`) with ±120 characters around it, taken
from the stored filing. So the *document* is the ground truth, not our database. Where a
row has no citation the `context` cell says so and shows the field's likely location
instead — those rows need the original: every row carries a `dart_url`.

**Rows the gate already blocked are in the sheet on purpose** (`gate` = `failed` /
`not_evaluable`). Judge them exactly like the rest: we need to know how often the gate
throws away a reading that was right — that is what the report calls over-blocking.
`gate` = `deterministic` marks the 증권발행실적보고서 figures, which no model read.

**Time.** ▷ 75–95 minutes. The sheet is ordered ①(유상증자) → ②(CB) → ③(매수청구) →
실적보고서, and one filing's rows sit together, so stopping at the end of a block still
gives a complete measurement for the rights types above it. Check progress any time with
`.venv/bin/python -m mijual.evalset status`.

**When you are done** (or want to save partway — it is safe to re-run):

```
.venv/bin/python -m mijual.evalset import      # validates; refuses unknown labels
.venv/bin/python -m mijual.evalset report      # per-field precision + gate-block rate
```

Save the file as **CSV, UTF-8**. Only `row_id`, `label` and `corrected_value` are ever read
back, so a spreadsheet reformatting the other columns costs nothing.
