# P4.S7 — 첨부1 공모전 기획서

## What this slice is

Write the first of the two mandatory 양식 documents: **(첨부1) 2026 금융 AI Challenge 공모전 기획서**.
English body, Korean section headings preserved verbatim, as a Markdown source of truth in this
repo, plus a working Markdown → PDF path that `P4.S8` will reuse.

**Nothing is submitted.** This slice produces the document and stops.

This slice was moved to `--order 0.5` — ahead of the whole deploy chain — because 첨부1 has **no
dependency on the deploy** and the documents are the operator's headline deliverable ("no submit,
only prepare the document"). Do not wait for anything.

## Read first

- `works/phases/active/P4/phase.md` — the notebook, and specifically the block tagged
  **(from P4.DECOMP, for P4.S7/S8)**. Consume that block: this slice is one of its two addressees,
  so when you finish, drop the parts that were only for 첨부1 and leave what 첨부2 still needs. The
  notebook is at its byte ceiling, so this matters.
- `docs/reference/challenge/submission/README.md` — **the 양식's required structure, extracted
  verbatim.** Do not re-derive it, and do not invent sections.
- `docs/reference/challenge/01_문제정의.md` (100 lines) — the problem statement with `[근거]` source
  tags. This is near-verbatim raw material for §3 and for §4's alternatives gap.
- `docs/reference/challenge/00_HANDOFF.md` — §1 (contest facts), §3.5 (surface strategy), **§3.6
  (the AI-role architecture)**, §3.7 (naming), §4 (the sourced competitive recon), §7 (working
  rules).
- `docs/current/product.md` — the authoritative shipped feature set and the measured numbers.
- `docs/current/decisions.md` — for **D-7**, the caveat that must travel with the accuracy figure.

Read `docs/current/` **sections**, not whole documents, and do not read the archived phase folders.

## The 양식's required structure

Seven sections; **1–6 are 필수**, 7 is optional and free-titled. Both templates open with `팀명` and
`구성원 성명`. Keep these headings **in Korean, verbatim**; write every body paragraph in English.

1. `서비스 명칭`
2. `아이디어 기획 핵심내용(요약)` — an 개조식 (bulleted, telegraphic) summary of the whole plan
3. `문제 정의 및 제안 배경` — the concrete problem, plus which 금융 고객 and which 채널
4. `서비스 컨셉 및 차별성` — the core concept and its 독창성·차별성 against existing 금융 앱
5. `활용 데이터 및 생성형 AI 모델 적용 방안` — data types, the collection/use plan, and **how the
   생성형 AI 모델 is used inside the service and what role it performs**
6. `기대 효과 및 확장 가능성` — effects, concrete benefits, market/feature expansion, and
   applicability beyond finance
7. `(자유타이틀 기재)` — free section

There is **no page limit** as long as the 양식's structure is preserved, and 시각자료 may be added.

## What goes in each section

Guidance, not a script — you are writing the document, so exercise judgment on emphasis and length.

- **§1** — 주주의관제탑. (Renamed from 미주알 in P10; code identifiers still say `mijual`, which is
  irrelevant to this document. Do not use the retired name anywhere.)
- **§2** — 개조식. Lead with the measured opening number, then the one-line definition, the three
  rights types, the AI-role split, and the roadmap. This is the section a judge skims first.
- **§3** — from `01_문제정의.md`: rights are *disclosed* but not *delivered*; the five places money
  actually disappears; why 2026 is the peak year. Keep its `[근거]` discipline — a sourced fact and
  an estimate must not read alike.
- **§4** — the concept from §3.5 (a market-wide 관제 현황판, not "my account's alert app"), and the
  differentiation from §4's recon: existing services stop at **notification**; **management** is
  the gap. The honest framing is that the gap is in the second half, not that nothing exists.
- **§5** — **the load-bearing section.** This is where §3.6 goes, and it is the registered #1
  expected Q&A ("what does the AI actually do? I see a scraper and a website"). The three layers:
  AI **reads** (schema-driven extraction from prose the DART structured fields do not carry —
  증서 매매기간, 청약 취급 증권사, 실권주 처리, CB 리픽싱·콜풋·보호예수, 매수청구 반대의사 통지),
  deterministic **gates verify** (arithmetic, date ordering, citation-span existence; a field that
  fails is never shown), AI **speaks** (citation-forced generation). Money and D-day arithmetic is
  LLM-free. The pitch line is not "we used AI" but **"we used AI under control."** The form asks
  about *use*, never training — so this costs nothing, and **no fine-tuning / PyTorch / HF framing
  appears anywhere in the document**.
- **§6** — 주최사별 효용 매핑: KB증권·카카오뱅크 as a retail feature they do not ship; 금보원·금융위
  as investor protection plus the AI-trust principle 「숫자는 AI가 만들지 않는다」. Expansion:
  수동 등록 → 알림 → 마이데이터 자동 연결 → the 권리 데이터 **MCP 서버** reaching the AI-agent
  ecosystem. Beyond finance: the same read/verify/speak split fits any domain where a deadline is
  buried in prose.
- **§7** — use it for the evidence a judge would otherwise have to take on trust: the
  extraction-accuracy measurement and its method, and the honest-limitations list. Your call whether
  to split it differently.

## The numbers, and the caveats that travel with them

Every one of these is measured and already in the record. Use them; do not round them up, and do not
add any number that is not in the record.

- ▷ **718.1억원** — lapsed 신주인수권 value, 2026 YTD, across 32 주주배정 유상증자;
  51,253,956 / 365,527,824 증서 (14.02 %) neither subscribed nor sold. Conservative band edge
  ▷ **548.7억원**.
- **488 exposable events** (① 50, ② 422, ③ 16), 409 renderable field instances, every field carrying
  a citation span into the filing.
- **98.6 % strict extraction accuracy** (213/216, Wilson 96–100 %) — **this figure may never appear
  without its caveat (D-7): it is cross-model judgement (Claude judging Gemini), explicitly not
  human ground truth.** Any public use must say so.
- ▷ **49.2억원** (6.4 % of the headline) deliberately **excluded** because fields failed their gates.
  This is the trust claim with a price attached, and it belongs in §5 or §7 — it is the strongest
  evidence that the gates are real.

Keep the record's `▷` convention, which marks a derived or estimated figure as distinct from a
sourced one (see `docs/reference/design/grounding/headline-numbers.md`). §7 of the handoff is
binding: **facts carry sources, estimates are marked as estimates, and nothing is inflated —
especially user counts and results.** There are no users; do not imply any.

## Output

- **`docs/reference/challenge/submission/drafts/01_공모전기획서.md`** — the source of truth.
- **`scripts/render_submission_pdf.py`** — Markdown → HTML → PDF. There is no `pandoc`,
  `wkhtmltopdf` or `weasyprint` on this machine; **Chrome is at
  `/Applications/Google Chrome.app`** and `--headless --print-to-pdf` renders Korean correctly from
  system fonts. Keep it stdlib-only and small: a minimal Markdown subset renderer (headings, lists,
  tables, bold/code, paragraphs) plus a print stylesheet with A4 margins is enough — this is a
  document renderer, not a Markdown implementation. `P4.S8` reuses it unchanged, so give it a
  `<input.md> <output.pdf>` interface.
- **The rendered PDF**, committed beside the Markdown.

Do not touch `frontend/`, `src/`, or any `docs/current/` file. This slice writes no product code.

## 팀명 and 구성원 성명

The two header fields. The entrant is a solo entrant (이수강), but **the 팀명 registered on daker.ai
is not recorded anywhere in this workspace**. Do not guess it and do not stop for it: write a
clearly-marked placeholder (e.g. `팀명: 〈미확정 — 운영자 확인 필요〉`) and add one line to
`phase.md`'s `## Operator Questions`. It is a two-word fix at the acceptance gate.

## Validation

- The document has all seven sections, headings byte-identical to
  `docs/reference/challenge/submission/README.md`'s extraction.
- `grep` the draft for the retired product name and for fine-tuning vocabulary
  (`파인튜닝`, `fine-tun`, `PyTorch`, `Hugging Face`) — expect zero hits.
- Every occurrence of the accuracy figure is within a sentence carrying the cross-model caveat.
- `python3 scripts/render_submission_pdf.py <in> <out>` produces a PDF whose Korean headings render
  as Korean, not tofu. Open it and check — a PDF that exists is not a PDF that reads.
- `python3 scripts/workflow.py validate` clean.

## Return

A structured verdict. In `result.md`, record what you wrote and why you shaped it as you did, any
place the sources disagreed with each other, and anything a judge would ask that the document does
not yet answer. Append your doc-impact line to `phase.md` only if you changed durable truth — a new
draft document is not durable truth, so most likely this is `none`.

If a section cannot be written honestly from the record — a claim the evidence does not support —
say so in `result.md` rather than writing around it. That is exactly the §7 rule this document is
supposed to demonstrate.
