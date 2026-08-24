# Plan — P3.S7: Design round R6 — grounded 해설 panel (co-work)

## Shape

`co-work` slice, inline, two legs like S2–S6: **handoff leg** — write
`docs/reference/design/rounds/06-explain/handoff.md`, commit, push (the slice's one push),
`set-slice-status P3.S7 pending`, STOP. **Read-back leg** — list_files → verify cards →
concreteness check → land under `rounds/06-explain/output/` → phase.md append → signoff →
SIGNOFF append → pure regroup (`⏳ P3.S7 · Explain`) → finish-slice → commit.

## Round scope (inventory item 9)

The citation-forced explanation layer (§3.6 layer 3) over verified data:

- Entry point — **not a chat UI as the default surface**; the nav's provisional "해설"
  slot is R2-signed as a link but what it opens is this round's decision.
- Question affordance (free input vs preset questions vs both).
- SSE streaming / complete / error states (stack locked: SSE is used only here).
- Inline citations back to the filing (Citation primitive exists — how citations appear
  inside streaming prose is the design question).
- **Refusal state** when the underlying data is not gate-passing — a product feature,
  not an error.

## Notes

- §3.6 frame is locked product truth: AI reads and speaks, only determinism calculates —
  the panel explains verified fields under 원문 인용 강제 and never generates numbers.
- No user-side Q&A history exists (Finding 8 applies) — any "recent questions" content
  must be labeled composition examples, or absent.
- Real grounding: pinned events (계양전기/한화솔루션/대동기어/세기상사), their
  citations/quotes in the samples, Korean state copy. A realistic 해설 answer in a card
  must be composed from those real fields, marked as composition where it's authored.
- Required cards under `⏳ P3.S7 · Explain`: entry placement(s), the panel with a
  streamed grounded answer + inline citations, streaming/error states, refusal state,
  mobile.
- Open questions posed to the session: what the nav "해설" link opens; question
  affordance shape; per-event vs cross-portfolio question scope; inline-citation
  rendering pattern during streaming; refusal copy; whether answers persist anywhere.
