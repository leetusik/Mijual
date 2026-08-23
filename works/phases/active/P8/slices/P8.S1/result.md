# Result — P8.S1: AskWidget `t1` 중복 키 — collision-free turn ids

**Outcome: fixed, and verified in a real browser in the operator's own runtime — both origins, dev and
a production build.** One source file changed plus one test case. The old and the new scheme were both
measured with the same harness, so the "before" is a number, not a claim.

---

## 1. What changed

**`frontend/lib/ask.ts`** — `nextId()` only. A module-scope `SESSION_TAG` is computed once per module
evaluation (i.e. **once per page load**) and prefixes the counter:

```ts
const SESSION_TAG = sessionTag();          // 8 hex/uuid chars, per page load
function nextId(): string {
  counter += 1;
  return `t${SESSION_TAG}-${counter}`;     // e.g. t25c41408-1
}
```

`sessionTag()` takes `crypto.randomUUID().slice(0, 8)` when it exists, else 4 bytes of
`crypto.getRandomValues`, else `Date.now()`+`Math.random()`. Nothing else in the store moved:
`Persisted`, `readThread`, `writeThread`, `settle`, `hydrate` are byte-identical, `Persisted.v` stays
`1`, and no component was touched (the id is opaque everywhere — `turn.id` is only a React key and a
`retry()` argument; grep in §4).

### Why a session tag rather than the bare `crypto.randomUUID()` the plan sketched

A small, deliberate deviation, and the browser measurement is the reason (§3, "secure context"):
**`crypto.randomUUID` is secure-context only, and the operator's second access path — the tailnet URL
over plain http — is not a secure context.** Measured, not assumed:

| origin | `isSecureContext` | `crypto.randomUUID` | `crypto.getRandomValues` |
|---|---|---|---|
| `http://127.0.0.1:3000` | `true` | `function` | `function` |
| `http://100.77.164.42:3000` (tailnet) | **`false`** | **`undefined`** | `function` |

So the plan's "uuid when available, prefix+counter otherwise" would have shipped **two different id
shapes across the operator's two access paths**, with the fallback — the less-exercised branch — live
on exactly the path that gets tested least. Wrapping the entropy source instead keeps **one id shape
everywhere**; only the randomness source varies, and every branch produces `t<tag>-<n>`. It also keeps
ids short and ordered within a load, which is what makes a thread readable in the sessionStorage
inspector.

Collision-freedom, both directions: a legacy `t1`/`t2` can never equal `t<tag>-<n>` (the shapes
differ), and two loads collide only if their 32-bit tags collide — and a collision would additionally
have to be with a thread the *same tab* persisted, since this is `sessionStorage`.

**`frontend/lib/ask.test.ts`** — one case appended (five total in the file, 16 in the suite), plus the
header's "four cases" → "five cases". It seeds a `v: 1` thread with legacy `t1`/`t2` behind a
four-line `window.sessionStorage` shim (installed in the test, `delete`d in a `finally`, so no other
case sees a `window`), hydrates, asks, settles the turn on a stubbed 429, and asserts the restored ids
survive unchanged **and** that the three ids are distinct.

**Not vacuous — proven:** with `nextId()` temporarily put back to `` `t${counter}` `` the new case fails
`AssertionError: 2 !== 3` at `lib/ask.test.ts:209` and passes again the moment the fix is restored.

## 2. Validation

| command | result |
|---|---|
| `cd frontend && npm run typecheck` | **pass** (clean `tsc --noEmit`) |
| `cd frontend && npm run smoke` | **pass — 16/16** (was 15/15; `a turn minted after a restored thread never reuses a stored id` is the new one) |
| `cd frontend && npm run build` | **pass** — 16 routes, run twice (once after the edit, once after the temporary revert cycle, with `MIJUAL_API_ORIGIN=http://127.0.0.1:8000`) |
| `python3 scripts/workflow.py validate` | **pass** — `Workflow validation passed.` |

`pytest` was **not** run: this slice touches no Python. (The phase's 139-test floor belongs to the
apply slices.)

## 3. The restored-session repro — driven in a real browser

**Runtime: the operator's own, unchanged** (`## Operator Runtime`, `docs/current/operations.md`). The
stack was already up and was left up — `make stack-status`: postgres healthy, api pid 25177 on
`127.0.0.1:8000`, web pid 13009, `next dev` on `0.0.0.0:3000`. Driver: headless Chrome over raw CDP
from Node 24 with a fresh profile per run, reusing `P7.S9`'s `cdp.mjs` verbatim. 1440×900. The agent
answered for real (live corpus, 계양전기 · 20260724000546), so these are real streamed turns, not stubs.

Script, every run: clear `sessionStorage` → open the 런처 → ask 「계양전기 유상증자 청약일 언제예요?」
→ wait for `done` → **reload** → reopen → ask 「무상증자도 있나요?」 → read the thread out of
`sessionStorage` and the DOM, with `Runtime.consoleAPICalled` + `Log.entryAdded` captured throughout.

| run | origin / mode | turn ids after the reload | rendered turns | duplicate-key messages | page exceptions |
|---|---|---|---|---|---|
| **before** (old `nextId`, same harness) | `127.0.0.1:3000` · dev | **`["t1","t1"]` — 1 distinct of 2** | 2 | **9** | 0 |
| after | `127.0.0.1:3000` · dev | `["t25c41408-1","t7ea10e05-1"]` — 2 of 2 | 2, each with its own question and answer | **0** | 0 |
| after | `100.77.164.42:3000` (tailnet) · dev | `["t3abb0763-1","td4ca1c6d-1"]` — 2 of 2 | 2 | **0** | 0 |
| after | `127.0.0.1:3100` · **production build** | `["tb3b19550-1","t032dbdf7-1"]` — 2 of 2 | 2 | **0** | 0 |

The "before" row is the bug exactly as reported: `t1` twice and nine copies of *「Encountered two
children with the same key」*. The tailnet row is the fallback branch (no `randomUUID` there) behaving
identically to the secure-context one. The production run matters because React ships **no** key
warning in production — there the only visible evidence would have been turns quietly duplicated or
omitted, which is why it was checked rather than assumed.

**재시도 hits the right turn only** (its own run, dev and production): ask → reload → ask again →
**중지** mid-stream so the second turn ends 중단 with a 재시도 row → click 재시도 on that newer turn.

- exactly **1** 재시도 row on screen; after the click turn 2 goes `aborted → pending → done` with a
  fresh answer, and **turn 1's answer is byte-identical before and after** (`true` in both runs);
- still 2 turns, the same 2 ids, **0** duplicate-key messages.

Under the old scheme this is the destructive half of the bug: `patchTurn` rewrites *every* match and
`retry` takes the *first*, so a 재시도 on the newer turn cleared and re-streamed the older one.

Screenshots + raw logs (session scratch, nothing written into the repo):
`/private/tmp/claude-502/-Users-sugang-projects-personal-Mijual/b668d726-e759-4d34-b8d6-6026b833f3c2/scratchpad/p8s1/`
(`repro.mjs`, `retry.mjs`, `ctx.mjs`, `shots/*.png`).

**The only console noise in every run, before and after, is one `404` — `GET /favicon.ico`**
(confirmed by curl: the repo ships no favicon). Pre-existing and unrelated; noted for R8's chrome walk.

## 4. Notes for whoever touches this next (R14 / `P8.S15`)

- Grepped before changing anything: `turn.id` / `turnId` appear only at `lib/ask.ts:289,298,471,482,486,492,501`
  and `components/ask/{AskWidget.tsx:96,104, AskPage.tsx:99,104}` — all as an opaque key or a `retry()`
  argument. **No parser, no sort, no test depends on the id format**, so the shape stays free to change.
- Threads persisted by the shipping build (`t1`, `t2`, …) still hydrate: `readThread` never inspects
  the id, and `Persisted.v` was deliberately left at `1`. Verified in the new test and in the "before"
  browser run, whose `t1` thread the fixed build restored without complaint.
- The id is a **lookup key**, not just a React key. Anything future that mints, rewrites or dedupes
  turns has to keep `patchTurn` / `history(exceptId)` / `retry` pointing at exactly one turn.

## 5. Deviations from `plan.md`

1. **Id shape** — session tag + counter (`t<tag>-<n>`) rather than a bare `crypto.randomUUID()` id.
   Reason and measurement in §1; the plan explicitly left the `t` prefix and the fallback shape to this
   slice, and both branches now produce one shape. Everything else in the plan's fix — one file, no
   `Persisted`/`readThread`/`writeThread`/`settle` change, no version bump, no component touched — held.
2. **`frontend/next-env.d.ts`** — `npm run build` rewrites this tracked file in place
   (`.next/dev/types/*` → `.next/types/*`; `next dev` writes it back). It was restored with
   `git checkout --` after each build, so the slice's diff is the two intended files only. Worth
   knowing for the next slice that builds in the repo instead of a copy (`P7.S9` used an rsync copy to
   avoid exactly this).
3. Nothing else. No copy, no styles, no other files, no commits, no status transitions, no
   `doc-new-version`.
