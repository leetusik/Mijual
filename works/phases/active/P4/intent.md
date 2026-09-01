# Intent — P4

- Captured at: 2026-08-19T17:41:27+09:00
- Origin: operator

## Original Input (verbatim)

> ---
> - insepect the .zip file.
> - create phases for the 2026 ai challenge.
> - think, conversation with english, only the product will be have korean only surface.


## Revision — 2026-09-02 (operator, at `/do-whole-phase`)

> ---
> no submit, only prepare the document. not in Korean but English.
> gonna use cloudflare, orcle-cloud server nginx(edge) for the deploy.
> SEO setup required.

## Confirmed Intent (refined + clarified)

Final phase of the 주주의관제탑 challenge project. **Revised 2026-09-02**: the phase prepares the
submission documents, deploys the service publicly, and sets up SEO. **It does not submit.**

1. **Documents — both official 양식, filled, not submitted.** 첨부1 공모전 기획서 (7 sections,
   1–6 필수) and 첨부2 기능명세서 (5 sections, all 필수). Structure extracted verbatim in
   `docs/reference/challenge/submission/README.md`.
2. **Language: English body, Korean section headings preserved verbatim.** Product screenshots
   stay Korean — the surface is Korean.
3. **Production deploy** to the operator's **Oracle Cloud box**, nginx at the edge, **Cloudflare**
   in front, at the domain **`jujutower.com`**. Run over ssh by the agent, **additive only**:
   nothing already on that box is touched, restarted, rebound or dropped.
4. **SEO setup required.**
5. **Notifications**: the D-day alert email channel — the last unbuilt product feature. 카톡 stays
   roadmap (handoff §6 item 4). Sender is the existing `hi@hi2vi.com` transactional account.
6. **Production polish**: a smoke suite against the public origin, plus uptime monitoring alerting
   by email to `swangle2100@gmail.com` — the operator's "small scope, production-grade" standard.
7. **Meta/OG and mail Korean copy** is drafted by the phase and approved by the operator, literally,
   at the acceptance gate — not through a design round.

**Out of scope, explicitly:** the daker.ai submission, the demo video, and the 발표자료 deck.

**Shared working rules (all phases):** think/converse/document in English; product surface in
Korean. Honor handoff §7: evidence-tagged facts, no inflation, small scope/production polish,
AI reads & speaks / determinism calculates, no fine-tuning/PyTorch/HF framing. Context:
`docs/reference/challenge/00_HANDOFF.md`, `01_문제정의.md`.

## Clarifications Resolved

**2026-08-19 (phase creation):**

- Q: 4-phase structure (spike → pipeline → web → ship & submit)? — A: **Yes, 4 phases** (deploy/polish and submission share this phase rather than splitting into five).
- Q: Web service phase — one mixed design+build phase or two-phase split? — A: **One mixed phase (P3).**
- Q: MVP rights-type 3종 — confirm ① 유증 신주인수권 ② CB·EB 오버행 ③ 매수청구권 now? — A: **All 3 tentatively confirmed**, finalized after the P1 spike.

**2026-09-02 (revision):**

- Q: Which documents does the phase produce? — A: **Both official 양식**, filled, unsubmitted.
- Q: The 양식 carry Korean headings and the contest is Korean — what language? — A: **English body,
  Korean headings kept verbatim.**
- Q: Is a demo video required? — A: **No.** Verified: the MVP form is
  `linkConfig = {demo: enabled+required, github: disabled, youtube: disabled}` — a demo **URL**,
  never a video. The 발표자료 deck is deliverable ③, October 8, finalists only. Both dropped.
- Q: How far does the phase take the deploy? — A: **The agent runs it over ssh**, under an
  additive-only contract ("no harm for running apps").
- Q: What public hostname? — A: **`jujutower.com`**, wired through one env var so nothing hardcodes
  an origin.
- Q: Which hardening stays in scope? — A: production smoke **yes**, uptime monitoring **yes**
  (email alerts via the `hi2vi_web` credentials, `hi@hi2vi.com` → `swangle2100@gmail.com`);
  the deploy-hardening deferred jobs (D32, D35, D37, D19, D22) stay **deferred**.
- Q: SEO needs a Korean meta description, which the signed design deliberately does not contain.
  How? — A: **The phase drafts it; the operator approves the literal strings at the acceptance
  gate.** No design round.

## Notes

- The verbatim original above is immutable. The 2026-09-02 operator input is recorded verbatim as
  its own block rather than editing the first one.
- Operator schedule constraints (handoff §2): 창플 contract ended 8/31, job-application deadlines in
  parallel, 본선 발표 9–10월 — the work must not assume full-time availability.
- The contest closes 2026-09-07 10:00 KST. Since the phase does not submit, that deadline and the
  two 결격-grade constraints in `docs/current/operations.md` (the 09-07 11:00 → 09-11 23:59
  unattended-uptime window, and the URL freeze) are **design inputs, not gates**.
