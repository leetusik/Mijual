# Design record — 미주알

The durable design tree. It lives outside `works/` on purpose: the apply phase reads it long after
the design phase is archived.

```
docs/reference/design/
├── grounding/              # P3.S1 — the real content every round is designed against
└── rounds/<NN>-<slug>/     # one per design round (P3.S2–S8)
    ├── handoff.md          # OUT — what the round must cover, and the questions posed back
    └── output/             # IN  — returned by Claude Design; READ-ONLY once landed
        ├── result.md       #   what was designed; every departure logged
        └── build-prompt.md #   the implementation contract the apply phase builds from
└── SIGNOFF.md              # the operator's literal approvals, round by round
```

## Read this first

`grounding/` is the **anti-lorem pack**: real board counts, the real headline numbers, the real Korean
copy, and real edge-state samples exported from the live corpus. Every round is designed against it.
Start at [`grounding/README.md`](grounding/README.md).

## Rules that hold across every round

- **Claude Design + the operator make the visual decisions.** A `handoff.md` says what to cover and
  poses questions back; it never proposes a palette, a type scale or a layout.
- **The returned record is read-only.** Nits found later are apply-time to-dos, never edits.
- **RESPECT THE DESIGN.** Nothing approved is dropped, simplified, restyled or "improved" downstream.
- **Korean-only product surface**; the team's own language is English.
- **Copy is locked by default.** It comes from `grounding/copy-inventory.md`, which is generated from
  the code that will emit it at runtime. A round may propose a change — by naming the string and the
  reason in its handoff.
- **Approval must be literal.** A revision creates a new immutable round that supersedes the old one.
