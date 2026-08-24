# Result — P5.S18: vocky integration

The shape §6.3 delegated to this build is **decided against vocky's real product**,
written back into the landed record's own section, and implemented end to end: a
server-side read proxy, the 피드백 section rendering it, and a live pass through a
throwaway local vocky stack that captured real rows and rendered them in the
Mijual ops panel.

**0 new dependencies** (Python or npm). Python suite **114 → 118**; frontend smoke
unchanged at 11. The vocky repository was read only and is byte-identical.

---

## 1. The decided observation shape

Read from vocky's own repository (`README.md`, `docs/current/api.md`,
`src/vocky/project_feedback_api.py`, `src/vocky/tools/query_feedback_common.py`) and
then **measured against a running local stack**, not inferred.

| decision | value |
|---|---|
| endpoint | `GET {base}/api/project/feedback` — vocky's **Project Feedback API v2** |
| auth | `Authorization: Bearer vk_…`; scope is implicit in the key (no project parameter exists on that surface) |
| granularity | **one row per feedback event** — no aggregation, no roll-up |
| pagination | keyset, newest first: `limit` (default 50, **max 100 — vocky's own ceiling**) + opaque `cursor`; `next_cursor` passed through, **absent** (not null) at the end; **no total** — vocky returns none and none is invented |
| fields | `ingested_at · message · feedback_value · trigger_type · trigger_message · target_type · target_id · target_text · channel · recorded_by · source_product · source_integration · comment · tags · id · project_id`(org keys only) |
| field naming | **vocky's own English keys**, served in `payload.fields` — §6.1/§6.2 sign raw English identifiers on this surface, and the frontend therefore names not one vocky field |
| time | `ingested_at` converted server-side from vocky's UTC (`…Z`, µs) to absolute KST `+09:00` |
| states | `ok` · `unconfigured` (연결 전) · `unreachable` (`reason` = raw exception name, `status` = HTTP code when there was one) |

**Why that endpoint.** vocky's own contract names this use case: "an external
service's own admin panel / operator page … reading and managing its project's
feedback directly by API". The other three read surfaces were considered and
rejected on the record — `GET /api/feedback` is one product *user's* self-read
(needs a `user_id`), `/app/feedback` wants a human session token, and
`/api/project/usage` returns the org's **credentials**, which is key metadata a
different product's panel has no business rendering (최소 열람).

**Why an allowlist and not a pass-through.** vocky's record carries 25 keys. The
nine excluded ones are correlation handles (`user_id`, `session_id`,
`conversation_id`) or free-form blobs (`source_metadata`, `attributes`, `messages`,
`used_context`, `trigger_metadata`) plus two caller-arbitrary values (`target_role`,
`event_at`). Forwarding them would move another product's user identifiers onto this
panel for no observational gain, against 사용자 추적 용도 금지 and 최소 열람. The set
is served in `fields`, so widening it later is a one-line backend change with **no
frontend change at all**.

Recorded in the landed record at
`docs/reference/design/rounds/07-admin/output/build-prompt.md` §vocky 관찰 뷰, as a
new dated subsection — **59 lines added, 0 lines changed** (`git diff` shows no `-`
line in that file). Nothing outside that section was touched.

## 2. Placement: the vocky view **is** the 피드백 section

The plan asked for the placement to be decided from R7's own structure. It is
unambiguous, and it means `P5.S17`'s placement was inverted:

- `output/result.md` line 83: "**Feedback** — vocky 관찰 뷰 프레임 (§6.3)".
- `output/result.md` line 80: the **Conversations** card carries "save_feedback
  대기열 — 대기 0건 (미배포 실제값)".
- `handoff.md` §5 says the same: `admin/Feedback.html` = "the vocky observation
  view"; `admin/Conversations.html` = "the anonymous 해설 log viewer **+ agent
  feedback queue**".
- The seven cards map 1:1 onto the six signed tabs **in order** (Overview 개요 ·
  GateQueue 게이트 대기열 · Accuracy 정확도·비용 · Conversations 대화 로그 · Users
  사용자 · Feedback 피드백; Access is the pre-auth door and has no tab).

So a seventh tab was rejected — it would break the signed 6-tab nav — and the
`save_feedback` queue **moved to the 대화 로그 tab**, below the log. That is also
what the round's own reasoning asks for: "vocky 뷰와 agent 대기열은 **분리** … 병합하면
'익명 대화 로그'와 '자발 이메일 동반 의견'의 서로 다른 프라이버시 계약이 섞임" — the
queue's rows come out of the anonymous conversations, vocky's come from a different
collection path. Both sections keep the 상호 링크 the no-merge line allows
(vocky → 「대화 로그 →」, queue → 「피드백」), and **no row of one is read by the other**.

## 3. What was built

**Backend** — `src/mijual/web/vocky.py` (new), `GET /ops/vocky` in
`routers/ops.py` (`/ops` is now **thirteen** routes, all read-only), and two
`Settings` fields.

- HTTP by **`urllib.request` (stdlib)**, the runtime-legal route: `httpx` is a dev
  extra only and no dependency was added. The endpoint is sync, so FastAPI runs it
  in the threadpool and blocking I/O is correct there.
- **3 s timeout, no retries, redirects refused.** Refusing redirects is a
  credential decision, not a nicety: `urllib` re-sends `Authorization` to the
  redirect target, so a redirected base URL would hand vocky's `vk_` key to whatever
  answered. A non-`http(s)` scheme is refused for the same class of reason.
- **Read-only is structural.** vocky has **no read-scoped credential today** — the
  same `vk_` key can `PATCH`/`DELETE` on that surface — so the proxy issues `GET`
  and there is no code path that could issue another method.
- **The key is a secret**: masked `repr`, `require_vocky_api_key()` raises only on
  use, travels in a header, and neither it nor the response body nor the exception
  text is ever logged. vocky's error body is not echoed onto the panel.
- Degradation follows `P5.S9`'s Redis precedent exactly: a state and a raw English
  reason, never a 500 and **never a fabricated row**.

**Frontend** — `components/ops/Vocky.tsx` (new), `lib/types.ts` `OpsVocky`,
`lib/api.ts` `getOpsVocky`, four `copy.ts` entries (all transcribed, sources in the
file), one `Ops.module.css` rule (`.skeleton`), `app/ops/feedback/page.tsx`
rewritten to the vocky view, `app/ops/conversations/page.tsx` gaining the queue,
`Feedback.tsx` re-homed with its own `?feedback_cursor=`.

- The table's **column headers are the served `fields`** — raw English mono, so the
  card's `?` headers are replaced by real names and the client invents none.
- Only the ops atoms are used (`Panel`, `Code`, `Stamp`) and `log.ts`'s
  `cellText`/`extraKeys`; the one new CSS rule is the 스켈레톤 the round names, and
  it is static (a pulsing bar would be the only moving ornament on the surface).
- The browser never sees the `vk_` key: the read goes through the service.

## 4. Validation

| command | outcome |
|---|---|
| `.venv/bin/python -m pytest` | **118 passed, 2.56 s** (114 → 118; 4 new in `tests/test_web_vocky.py`) |
| `cd frontend && npm run typecheck` | pass |
| `cd frontend && npm run smoke` | **11/11** (unchanged) |
| `cd frontend && npm run build` | pass — 16 routes, compiled successfully |
| `python3 scripts/workflow.py validate` | **Workflow validation passed** |

**Live end-to-end pass (2026-08-22, local only).** A throwaway vocky stack was
built and run from `~/projects/personal/vocky` under its **own compose project**
(`-p mijual-s18-vocky`, ports 8010/55433/56380 — no collision with Mijual's 5433/6380
or the operator's other stacks), migrated **inside the container** so the local
`uv.lock` was never touched, and driven entirely over REST (no CLI install):

- throwaway account + `"default"` project + a project-scoped `vk_` key minted;
- **3 feedback rows captured** through `POST /api/feedback` with Mijual-shaped
  context (`source_product: mijual`, `trigger_message: [의견] / 의견 보내기`,
  `target_type: surface`, `target_id: / · /stocks · /events/…`);
- `GET /ops/vocky` returned all three, KST-stamped, allowlisted, with the cursor —
  **and the ops panel rendered them**: `vocky 관찰 뷰` title, the three contract
  lines, `state ok`, the real column headers, `2026-08-22 16:33 KST`, the Korean
  feedback text, `3건`, and the 「대화 로그 →」 cross-link. Page 2 via the cursor
  link renders the second row.
- 대화 로그 tab re-checked: the queue's signed empty state 「대기 0건 —
  save_feedback 호출이 아직 없습니다」, its no-merge note, the 「피드백」 cross-link,
  and **no vocky row or column anywhere on it**.
- **Degraded paths measured live**: unset credential → `unconfigured` and the
  surface renders 「API shape 확정 대기」 + 48 skeleton cells with the decided column
  names and **zero fabricated rows**; dead port → `unreachable` / `URLError` in
  12 ms; wrong key against the live stack → `unreachable` / `HTTPError` + `status
  401` in 33 ms; blackholed host → `unreachable` in **3.03 s**, i.e. the timeout
  bound holds and the tab cannot hang the panel.

**Teardown.** Every process stopped (uvicorn ×4, `next start`), the compose project
brought down with `-v` (its three volumes removed), both throwaway images deleted.
`git -C ~/projects/personal/vocky status` is **clean before and after**; nothing in
that repository was written, and `vocky.hi2vi.com` was never contacted at all — no
account was created on the hosted service and no request, read or write, was sent
to it.

## 5. Findings recorded (detail in `phase.md`)

1. **vocky ships no embeddable widget script.** R2/S11 assumed one. Evidence:
   `data-vocky-trigger` / `embed.js` / `widget.js` appear nowhere in the repository;
   `web/public/` holds only `install.sh` and `SKILL.md`; and vocky's README lists
   "Browser-direct unauthenticated ingestion" under **What The First MVP Will Not
   Do**. Every "widget" mention is an example of a *kind of surface* whose feedback
   you capture. So `NEXT_PUBLIC_VOCKY_SRC` has no real value to set — the triggers
   and the seam stay as they are (unset ⇒ no script tag, triggers still render).
2. **vocky's `limit` ceiling is 100**, not this panel's usual 200.
3. **No read-only key scope exists in vocky** — the key Mijual will hold can also
   write, which is why the read-only guarantee is Mijual-side and structural.
4. **The 연결 전 literal is now half a step stale**: the shape is confirmed, so what
   the view waits for is the credential. It renders **as signed** and the raw English
   `state` code says which cause it is. Replacing the line is a new signoff item —
   flagged for `P5.REVIEW`.
5. **P4 wiring list**: `MIJUAL_VOCKY_API_BASE=https://vocky.hi2vi.com` +
   `MIJUAL_VOCKY_API_KEY=vk_…` (minted by the operator in their own vocky org; org-
   or project-scoped, both work) — over **https**, because the key travels in a
   header. `NEXT_PUBLIC_VOCKY_SRC` stays unset until a widget script exists.

## 6. Deviations from `plan.md`

- **The `save_feedback` queue moved** from the 피드백 tab (where `P5.S17` put it) to
  the 대화 로그 tab. The plan asked for placement to be decided from R7's own
  structure; this is that decision, and it corrects an earlier inversion rather than
  departing from the plan. §2 above has the evidence.
- **One new CSS rule** (`.skeleton`) despite `P5.S17` note 1's "write no new CSS
  idiom". The skeleton is a signed element with no existing atom; the rule uses only
  existing tokens, adds no second visual language, and is static.
- **One landed test assertion was inverted, deliberately**:
  `test_web_ops.py`'s "no vocky route is pre-implemented" was `P5.S9`'s guard for
  the pre-decision period. Its precondition is closed, so it now asserts the route
  exists **and** reports 연결 전 when unwired.
- The plan floated a possible AST-scan change. None was needed — the existing scan
  is about OpenDART/LLM modules and `urllib` is neither. A **new** structural test
  was added instead: only `web/vocky.py` may import an HTTP client, so a later slice
  cannot quietly put a second external dependency on a request path.
