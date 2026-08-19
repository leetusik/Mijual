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

---

## 이 저장소에 현재 들어 있는 라벨의 출처 (2026-08-20)

`evalset/sheet.csv`의 344개 라벨과 `evalset/labels.json`은 **사람이 매긴 것이 아닙니다.**
운영자 지시(2026-08-20, "you self evaluate and self validate. since the extraction done by
gemini and you are a claude fable. try by yourself.")에 따라 **P2.S9 슬라이스 실행자인 Claude
(Opus 5)가 직접 판정**했습니다. §7의 10개 항목은 **Gemini**가 추출했고 판정자는 다른 계열의
모델이므로 자기 채점은 아니지만(cross-model), **사람의 정답(ground truth)은 아니며 사람이
검증한 적도 없습니다.** 판정 근거는 각 행의 인용문과 Postgres에 저장된 본문 전문이며, 외부
호출은 0건입니다.

**사람이 다시 판정하려면** 이 문서의 원래 절차 그대로입니다: 확인하고 싶은 행의 A열을 덮어쓰고
`import` → `report`를 다시 실행하면 됩니다. 표본(`sample.json`)은 고정되어 있으므로 바뀐 라벨의
행만 수치에 반영됩니다. 측정 결과와 그 한계는
`works/phases/active/P2/slices/P2.S9/result.md`의 Phase B 절에 있습니다.
