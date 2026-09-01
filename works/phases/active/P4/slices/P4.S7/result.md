# P4.S7 — 첨부1 공모전 기획서 · result

- **status:** `done`
- **summary:** Wrote 첨부1 (공모전 기획서) as a 14-page document — all seven 양식 headings Korean-verbatim, English body, every measured number carrying its caveat — plus `scripts/render_submission_pdf.py`, the stdlib-only Markdown → PDF path `P4.S8` reuses unchanged. Nothing was submitted.
- **files_changed:**
  - `docs/reference/challenge/submission/drafts/01_공모전기획서.md` (new)
  - `docs/reference/challenge/submission/drafts/01_공모전기획서.pdf` (new, 14 A4 pages)
  - `scripts/render_submission_pdf.py` (new)
  - `works/phases/active/P4/phase.md` (edited)
  - `works/phases/active/P4/slices/P4.S7/result.md` (this file)
- **validation:**
  - seven 양식 headings present, in order, byte-identical to `submission/README.md`'s extraction, and no eighth `##` section — **pass**
  - `grep -ci` for the retired name (`미주알`, `mijual`) and for fine-tuning vocabulary (`파인튜닝`, `fine-tun`, `PyTorch`, `Hugging Face`) → **0 hits each** — **pass**
  - both occurrences of the accuracy figure carry the cross-model caveat inside the same sentence — **pass**
  - `python3 scripts/render_submission_pdf.py <in.md> <out.pdf>` → 14-page PDF in ~3.6 s; pages 1–8 and 11–14 opened and read visually: Korean renders as Korean (no tofu), tables, the layer diagram and `▷` all render — **pass**
  - `python3 scripts/workflow.py validate` → `Workflow validation passed.` (one advisory `phase.md` budget warning, see *Deviations*) — **pass**
- **deviations:** three, all small; see below.
- **doc_impact:** `architecture` — Repo Shape: `scripts/render_submission_pdf.py`, the permanent Markdown → PDF path for the 양식 drafts (stdlib + headless Chrome), reused by `P4.S8`.

---

## What was written, and why it is shaped this way

**§1 서비스 명칭** is short on purpose: the name, a one-line gloss, the three readings of 관제탑 /
주주 / 소멸주의보, and the project's own one-sentence definition. A judge reads this section in
five seconds and should leave it knowing what the thing is.

**§2 요약** is 개조식 as the 양식 demands, and is the only section that repeats: it is written to be
readable *instead of* the document. It leads with ▷ 718.1억원 because that number is the argument.

**§3 문제 정의** is a near-transcription of `01_문제정의.md` with its `[근거]` discipline intact —
the three-gap table, the five places money disappears, the 2026 peak argument. §3.5 (어떤 금융
고객, 어떤 채널) is new: the 양식 asks it explicitly and the source documents answer it only by
implication, so it is stated as a table, including *why the channel is a web service* (a rights
event is a few-times-a-year event, which is the wrong rhythm for an app that wants daily residence).

**§4 차별성** carries the honest framing rather than the flattering one — the gap is in the second
half, not "nothing exists". The 분쟁조정 finding is load-bearing here and is stated as the logical
pivot: notification exists, has no legal duty to improve, and therefore the management layer can
only arrive as product competition. "미발견 ≠ 부존재" is disclosed in the same section that claims
differentiation, not hidden in §7.

**§5 is the long one, and deliberately so.** It is the registered #1 expected Q&A ("what does the
AI actually do? I see a scraper and a website"), so the objection is quoted in the section's own
epigraph and then answered structurally:

- §5.1 lists the data and then the **three tiers** (`API` / `본문-label` / `본문-prose`). This table
  is the section's honesty device: ② and ③ need **zero** LLM for their countdowns, so the reader can
  see exactly where AI is and is not, and that the boundary is enforced in code.
- §5.2 is §3.6 of the handoff, rendered as a plain-text pipeline diagram plus three sub-sections.
  Layer 1 carries the full 10-field extraction table **with each field's gate in the same row** —
  the point being that reading and verification are declared together. It also states the two
  engineering judgments a judge would otherwise doubt (slicing 증권신고서 by `<TITLE>` rather than
  feeding whole documents; 정정 diff as the standing AI job).
- Layer 2 states the four verdicts and the rule that a skipped check is never a pass — one line that
  is where most "AI reliability" claims quietly fail.
- Layer 3 describes the agent as an agent (seven server-side tools, the model chooses), and then the
  mechanical checks at the generation boundary, with the measured 27/27 and 0-unaccounted-numerals.
- A **"what the AI never does"** sub-section carries equal weight: LLM-free arithmetic, plus the
  deterministic detections that look like AI (철회 by row shape, not keyword — with the measured
  71 % keyword false-positive rate as proof the shortcut was rejected).
- §5.3 closes with the ▷ 49.2억원 the gates cost. Put here rather than only in §7 because it is the
  *evidence* for the section's claim, not an appendix note.

**§6** maps utility onto the sponsors that the record actually supports (KB증권·카카오뱅크;
금융보안원·금융위원회), and marks the bank/insurance row explicitly as a ▷ judgement with no
measurement behind it rather than padding the table. The five-line 「숫자는 AI가 만들지 않는다」
principle is stated as the transferable part, and the expansion axes are given as a staged table
with each row's real status (구현됨 / 현재 단계 / 로드맵).

**§7 was kept as one free section with five sub-sections** rather than split. The 양식 allows one
free section; inventing an eighth top-level section would break the structure the rules require to
be preserved, and everything here is one argument anyway — *here is what we measured, including
what we measured badly.* 7.1 accuracy + provenance, 7.2 the gate's cost in both directions, 7.3 the
honest-limitations list (nine items, including "there are no users"), 7.4 reproduction, 7.5 the
source list.

**시각자료.** Six tables earn their place (three gaps · competitors · data tiers · the 10 extraction
targets · sponsor mapping · the measurement summary), plus one plain-text three-layer pipeline
diagram in §5.2 and two staged tables in §6.4. No decorative figure was added; the extraction-target
table is the one a skeptical judge will actually read.

## The accuracy figure

98.6 % appears exactly twice — §2 (요약) and §7.1 — and in both places the cross-model qualifier is
inside the same sentence, naming Claude judging Gemini and stating that these are not human ground
truth (§7.1 adds "0 of 344 labels verified by a person"). D-7's mechanised half is described too
(the `judged_by` stamp, the refusal to write an unstamped labels file, the non-inherited
`--judged-by`), because a caveat that lives only in prose is exactly the thing a judge should not
have to take on trust. The document also states that the human re-judging path is open and cheap.

## Deviations from `plan.md`

1. **팀명.** The plan said to write a placeholder and raise an operator question. The operator
   answered mid-slice (relayed by the orchestrator): 팀명 is **주주의관제탑**, solo entrant, and
   `구성원 성명` stays a marked placeholder (`〈제출자 직접 기재〉`) they fill themselves. No 팀명
   question was filed; one line about `구성원 성명` was appended to `## Operator Questions` instead.
2. **`[근거]` links render as links, not raw URLs, and §7.5 was added.** The record's own convention
   is a backticked `` `[근거: X](url)` ``, which in PDF prints the whole URL inline — measured on the
   first render, it made §3 nearly unreadable and broke long URLs across lines. The tags are now real
   links (label only) and every URL is listed in full in **§7.5 인용 출처 목록**, inside the free
   section, so a *printed* copy loses nothing. No source was dropped; 21 distinct URLs are listed.
3. **`phase.md` is over its byte budget (16,816 vs 16,384).** It arrived over budget (16,497 bytes at
   `HEAD`), and this slice's required additions — one Doc impact line, one Operator Question, the
   S8 note — outweigh the block it consumed by 319 bytes. The bulk of the file is DECOMP's
   unconsumed note blocks for S1–S6, which shrink as those slices run; compressing another slice's
   outage-grade deploy notes to buy bytes looked like the worse trade. `validate` warns, not errors.

## The renderer

`scripts/render_submission_pdf.py <input.md> <output.pdf>` — stdlib only, ~370 lines, two halves:

- a **document-grade Markdown subset** (ATX headings, ordered/unordered lists with one nesting level,
  GFM pipe tables, fenced code, blockquotes, rules, paragraphs, and inline code/bold/italic/link) —
  explicitly not a Markdown implementation;
- an A4 print stylesheet + `--headless --print-to-pdf` through `/Applications/Google Chrome.app`.

**One measured finding worth carrying:** Chrome 152 writes the PDF and then **never exits** on this
machine. Measured across `--headless`, `--headless=old`, `--headless=new`, with and without
`--virtual-time-budget` and `--timeout`: every variant produced a correct PDF and then hung until
killed (the first run of this slice hung at 120 s in exactly that way). So the script launches Chrome
with `Popen`, polls until the output file exists and its size is stable across two 0.5 s samples,
then terminates the browser itself. A plain `subprocess.run(...)` hangs forever; do not "simplify" it
back. End-to-end run time is ~3.6 s.

Two print-layout fixes came out of reading the rendered pages rather than trusting the file:
`overflow-wrap: anywhere` was shrinking table columns to one character per line (it feeds intrinsic
min-width; `break-word` does not), and `break-inside: avoid` on `table` pushed the 18-row source
table whole onto the next page and left half a page blank — the rule now lives on `tr`, with
`thead { display: table-header-group }` so a split table repeats its header.

## Where the sources disagreed

- **409 vs 418 renderable field instances.** `product.md` ("The Live Board") says **409**, verified
  read-only at the P2 review; `qa.md`'s Test Commands table says the `gates summary` command reports
  **418** — the difference is P5's `appraisal_price` rows landing after that verification. The plan
  names 409, so the document uses 409. `P4.S8` will quote counts too and should name the command it
  is quoting; the note is in `phase.md`.
- **Agent tool count.** `product.md` (P6) says five tools; `architecture.md` records P9 widening it to
  seven, and `TOOL_NAMES` in `src/mijual/agent/tools.py` has seven entries. The document says seven.
- **"57 events" vs "33 within 30 days"** for ② urgency in `product.md` are two different measurements
  of the same corpus; neither was used, because §5 did not need them and adding both would invite a
  question the document does not answer.

## What a judge would ask that the document does not answer

1. **"Is it live, and can I click it?"** — the document says the service is implemented and running
   on real filings, and that public deployment is the current phase's work. Until `P4.S4` lands there
   is no URL in it. 첨부2 §5 is where the judge-executable script belongs, and it is blocked on the
   same deploy.
2. **"Does any 증권사 MTS already do this?"** — answered only to the depth of the 2026-08-19 first
   pass. The coverage matrix is named as unwritten in both §4.3 and §7.3. It remains the single
   biggest evidentiary hole in the differentiation claim, and it is *not* this slice's to close.
3. **"Who validated the 98.6 %?"** — a model did, and the document says so twice. A judge who wants
   human ground truth will have to accept the disclosed path to it rather than a number.
4. **"How much does it cost to run at scale?"** — only ▷ $0.0093 per agent turn is in the record.
   There is no per-day pipeline cost figure to quote, so none is claimed.
5. **"What happens when DART changes a form?"** — the document describes 정정 handling, not upstream
   schema drift. Nothing in the record measures that, so it was not asserted.
