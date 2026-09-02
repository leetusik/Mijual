# P4.F4 — relax the extract call ceiling in production: a `MIJUAL_EXTRACT_MAX_CALLS` knob, set to 300 on the box, deployed before the freeze

Operator instruction, 2026-09-02 ~21:55 KST, verbatim: **「give relaxed extract max call to the prod
I don't want to miss a thing.」** Tier `slice-executor-high`. **Two dispatches with a push stop
between them** (the box deploys `origin/main`, and the orchestrator never pushes).

## Why this is a code change and not an env edit

The evening run on the box (2026-09-02 19:30 KST) ended its extract stage at **60 of 60 calls,
`BUDGET EXHAUSTED`** ($0.61, 466,729 tokens): the seeded corpus carries a 정정 backlog larger than
one run's ceiling, so rows wait for the next run. The ceiling is `PipelineConfig.extract_max_calls
= 60` in `src/mijual/scheduler/config.py:113` — a dataclass default; the beat entries in
`src/mijual/beat.py` (`daily-pipeline-morning` 07:30, `daily-pipeline-evening` 19:30,
`weekly-resync` 04:30 Sun) pass no `extract_max_calls`, the Celery task builds
`PipelineConfig.from_kwargs(**kwargs)` (`src/mijual/scheduler/app.py:120`), and the `once` CLI's
`--max-calls` default is a literal `60` (`src/mijual/scheduler/__main__.py:66`). **No env var
reaches it.** `Settings` (`src/mijual/config.py`, `load_settings()` → `pick()`: environment first,
then the repo-root `.env`) is the project's one env-reading place; `.env.prod` on the box is the
compose `env_file` of api/worker/beat/schema.

## Dispatch 1 — the knob, its docs, the box value; stop for the push

1. **`MIJUAL_EXTRACT_MAX_CALLS`** — one integer env var (≥ 1). When set, it is the extract ceiling
   of **every** scheduled run (all three `daily_pipeline` beat entries) and of `once` **unless**
   `--max-calls` is given explicitly. When unset, everything behaves exactly as today (60).
   Placement, smallest coherent diff: read it in `Settings` (`extract_max_calls: int | None = None`
   via `pick`, parsed `int`, invalid → raise with the key name and no value echoed — the same
   register as the other keys); apply it in `PipelineConfig.from_kwargs()` when the kwargs carry no
   `extract_max_calls` (beat path), and make the CLI's `--max-calls` default `None` → env → 60 in
   `_config()`. Keep the dataclass default `60` so offline tests stay deterministic. The run-log
   line `describe()` already prints `extract<=N calls`, which is how dispatch 2 verifies it on the
   box; the ops panel's beat kwargs need no change.
2. **Test — one small case** in `tests/test_scheduler.py` (this is a cost ceiling, the one kind of
   behaviour the product cannot afford to get wrong silently): with `MIJUAL_EXTRACT_MAX_CALLS=300`
   monkeypatched into the environment, `PipelineConfig.from_kwargs(window_days=14)` has
   `extract_max_calls == 300`, and `from_kwargs(extract_max_calls=5)` keeps `5`. Nothing more.
3. **`.env.prod.example`** — add the key to the *Optional* block with two lines of comment: default
   60 per run; the operator's production value is **300** (relaxed 2026-09-02, 「I don't want to
   miss a thing」), bounding one run at roughly $3 at today's prices; `once --max-calls` still
   overrides per run.
4. **The box value** — append exactly one line to `/home/opc/Mijual/.env.prod` over
   `ssh oracle-cloud`, preserving mode 600 and touching nothing else:
   `MIJUAL_EXTRACT_MAX_CALLS=300` (`printf '\n# extract ceiling per run (P4.F4, operator 2026-09-02)\nMIJUAL_EXTRACT_MAX_CALLS=300\n' >> …`; then `grep -c '^MIJUAL_EXTRACT_MAX_CALLS=' …` → 1 and
   `stat -c %a …` → 600). It is inert until the containers are recreated by dispatch 2's deploy.
   If the harness denies the ssh write, record it and hand the line to the operator in your return —
   do not work around it.
5. **`phase.md`**: `## Decisions` — the operator's instruction and the value 300 (the D-4 thinking
   *level* question stays open and is deferred job D40); `## Doc impact` — `operations`
   (Environment Variables: the new key, its default, the production value, the cost bound) and
   `backend` (Background Jobs: the extract ceiling is env-overridable, beat entries inherit it,
   `once --max-calls` wins per run); `## Now` — waiting on the operator's `git push origin main`,
   then dispatch 2 deploys (before **2026-09-07 11:00 KST**) and drains, then the re-review.
6. **Validate**: `uv run pytest -q` (167 expected), `python3 -m py_compile` on the touched
   modules, `python3 -m mijual.scheduler once --help` shows the new default wording,
   `MIJUAL_EXTRACT_MAX_CALLS=300 python3 -m mijual.scheduler once --offline --stages extract
   --window 14 --label f4-proof` prints `extract<=300 calls` in its `budgets` line (offline: 0
   calls), `python3 scripts/workflow.py validate`, `git diff --stat` → the two or three source
   files, the test file, `.env.prod.example`, `phase.md`, `result.md`.
7. Return **`needs_operator`**: 「push `main` to GitHub (`git push origin main`) — the box deploys
   `origin/main`; dispatch 2 then runs `deploy/deploy.sh` and a first drain run.」

## Dispatch 2 — deploy and drain (the orchestrator appends the push confirmation here)

- Preconditions: `git fetch origin && git rev-parse origin/main` equals the local `main` that carries
  this slice; no beat run in flight or due within 15 minutes (07:30 / 19:30 / Sun 04:30 KST — the
  box clock is GMT, KST = GMT+9); the four R7 no-harm assertions recorded **before**.
- Deploy: on the box, `nohup bash deploy/deploy.sh > var/deploy-$(date -u +%Y%m%dT%H%M%S).log 2>&1
  &` from `/home/opc/Mijual`, then poll the log until it reports the release or a rollback; both
  images rebuild (src/ changed) so api/worker/beat/web are recreated, postgres/redis are not.
  Afterwards the four assertions again, `docker compose -f compose.prod.yml ps` six up +
  `mijual-schema` exit 0, `curl https://jujutower.com/api/health` ok, `make smoke-prod` 17/17.
- Verify the knob: `docker compose -f compose.prod.yml exec mijual-worker printenv
  MIJUAL_EXTRACT_MAX_CALLS` → 300, and a first drain under the normal lock:
  `docker compose -f compose.prod.yml exec mijual-worker python -m mijual.scheduler once --stages
  extract --label f4-drain --trigger operator` (nohup + log + poll; it may run 20–30 min) — its
  `budgets` line must read `extract<=300 calls`; report calls, tokens, cost and whether the stage
  still says `BUDGET EXHAUSTED` (if it does at 300, say so — the operator decides the next value).
- `phase.md`: mark the decision applied, `## Doc impact` `operations` line for the deploy (log
  path, image ids, `:previous` now = the F2-era pair, no-harm assertions), `## Now` → the re-review.
- Deploy freeze: **must land before 2026-09-07 11:00 KST**; otherwise wait for 09-12.

## Hard rules

Production additive-only (never `edge-nginx`; `StartedAt 2026-07-02T19:22:12.325478595Z` unchanged);
no secret values in any file or transcript (the `.env.prod` append writes a number, not a secret,
but never `cat` the file); ssh only via `oracle-cloud`; long remote commands via nohup + log + poll;
no `git commit`/`push`; no workflow state commands; `uv run` without `--with`; the repo is public.
