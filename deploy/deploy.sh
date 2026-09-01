#!/usr/bin/env bash
#
# deploy.sh — build + release 주주의관제탑 on the shared OCI box.
#
# THE MODEL. This stack is `compose.prod.yml` (P4.S1): two built images
# (`mijual-api` + `mijual-web`), six long-running services and one one-shot.
# There is no systemd, no release symlink and no registry — a release is a
# rebuilt image pair, and **rollback is a tag flip**.
#
# WHY TWO IMAGES MATTER. `mijual-schema`, `mijual-worker` and `mijual-beat` all
# run `mijual-api:latest` with NO `build:` of their own, so the api image must
# exist before `up`. `dc build` builds both; `dc up -d` then runs the schema
# one-shot (`python -m mijual.db ensure`, additive and idempotent), which must
# exit 0 before the API is allowed to start.
#
# WHAT IT GATES ON. `mijual-web`'s own healthcheck, which fetches
# `http://127.0.0.1:3010/api/health` — THROUGH Next's rewrite to FastAPI. That
# is the honest rollback trigger: a web container that cannot reach its API is
# not a release. `mijual-api` is gated too (it probes `/health`, no DB touch).
# `mijual-beat` and `mijual-schema` have healthchecks disabled on purpose and
# are never polled; `mijual-worker` answers `celery inspect ping` and is
# reported but not gated (a worker outage leaves a stale board, not a dead one).
#
# WHAT IT NEVER TOUCHES. The edge. `edge-nginx` owns :80/:443 for every
# co-tenant on this box and is a different compose project; a Mijual deploy
# reloads nothing there. This script asserts it never names it.
#
# RUN IT ON THE BOX from /home/opc/Mijual:
#
#     deploy/deploy.sh                  # release origin/main
#     REF=<sha> deploy/deploy.sh        # release a specific ref
#     REF= deploy/deploy.sh             # skip fetch/checkout entirely
#
# KNOBS (env, all optional):
#   APP_DIR          repo root (default: this script's parent)
#   COMPOSE_FILE     default compose.prod.yml
#   ENV_FILE         default .env.prod  (operator-created on the box, gitignored)
#   PROJECT          compose -p project name. **UNSET ON THE BOX** — the compose
#                    file's own `name: mijual` is correct there. It exists only
#                    so a rehearsal on the operator's Mac can avoid colliding
#                    with the DEV stack, which is also compose project `mijual`
#                    and whose `mijual_mijual-pgdata` volume is the dev database.
#   REF              git ref (default origin/main). **EMPTY = skip fetch+checkout**
#                    — for a first deploy on a fresh clone, or any rehearsal.
#   HEALTH_TRIES     poll count (default 40)
#   HEALTH_INTERVAL  seconds between polls (default 5) → up to 200 s, which a
#                    cold start needs: postgres init + schema one-shot + the API
#                    + standalone Next, in that order, with real dependencies.
#   MIJUAL_EDGE_NETWORK  passed through to compose (external network selector).
#                    UNSET ON THE BOX = `changple_shared_network`.
#
# Authored and rehearsed OFF the box (P4.S3) against a throwaway compose project
# on the operator's Mac; it first runs for real on the box at P4.S4.

set -euo pipefail

# --- config knobs -------------------------------------------------------------
APP_DIR="${APP_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
COMPOSE_FILE="${COMPOSE_FILE:-compose.prod.yml}"
ENV_FILE="${ENV_FILE:-.env.prod}"
PROJECT="${PROJECT:-}"
# Deliberately `${REF-...}` and not `${REF:-...}`: an explicitly EMPTY REF must
# stay empty (skip the checkout), while an UNSET REF gets the default.
REF="${REF-origin/main}"
HEALTH_TRIES="${HEALTH_TRIES:-40}"
HEALTH_INTERVAL="${HEALTH_INTERVAL:-5}"

# The two built images, in the order they must exist.
API_IMAGE="${API_IMAGE:-mijual-api}"
WEB_IMAGE="${WEB_IMAGE:-mijual-web}"
IMAGES=("$API_IMAGE" "$WEB_IMAGE")

# The services the gate polls, and the one it only reports.
GATE_SERVICES=(mijual-web mijual-api)
REPORT_SERVICES=(mijual-worker)

# COMPOSE_BAKE=false avoids the `docker compose build` bake-path panic on this
# Compose line (a CLI bug: compose/build_bake.go slice-bounds). Exported so the
# docker subprocess inherits it.
export COMPOSE_BAKE=false

log() { printf '[deploy] %s\n' "$*"; }
die() { printf '[deploy] ERROR: %s\n' "$*" >&2; exit 1; }

# `docker compose` wrapper. `-p` is added ONLY when PROJECT is set, so on the box
# the compose file's own `name: mijual` is what applies.
dc() {
    if [[ -n "$PROJECT" ]]; then
        docker compose -p "$PROJECT" -f "$COMPOSE_FILE" "$@"
    else
        docker compose -f "$COMPOSE_FILE" "$@"
    fi
}

# --- health gate --------------------------------------------------------------
# Polls one service's container until `.State.Health.Status` is `healthy`.
# 0 = healthy; 1 = timeout, `unhealthy`, or no healthcheck at all (a service we
# meant to gate but cannot is a failure, not a pass).
wait_healthy() {
    local service="$1" cid status i
    for ((i = 1; i <= HEALTH_TRIES; i++)); do
        cid="$(dc ps -q "$service" 2>/dev/null || true)"
        if [[ -z "$cid" ]]; then
            log "poll $i/$HEALTH_TRIES: $service has no container yet — waiting ${HEALTH_INTERVAL}s"
            sleep "$HEALTH_INTERVAL"
            continue
        fi
        status="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' "$cid" 2>/dev/null || true)"
        # The container's own lifecycle state, reported alongside health: a
        # crash-looping container (`restarting`) reports health `none` or a
        # stale `starting` forever, and "no healthcheck" would be the wrong
        # thing to tell someone staring at a broken deploy. (Found in the P4.S3
        # rehearsal, by shipping a deliberately broken image.)
        state="$(docker inspect --format '{{.State.Status}}' "$cid" 2>/dev/null || true)"
        case "$status" in
            healthy)
                log "$service healthy on poll $i"
                return 0
                ;;
            unhealthy)
                log "$service reported UNHEALTHY on poll $i (its healthcheck retries are exhausted)"
                return 1
                ;;
            none)
                if [[ "$state" == running ]]; then
                    log "$service is running but has NO healthcheck — cannot gate on it (check compose.prod.yml)"
                    return 1
                fi
                log "poll $i/$HEALTH_TRIES: $service is '$state', not running — waiting ${HEALTH_INTERVAL}s"
                ;;
            *)
                log "poll $i/$HEALTH_TRIES: $service=${status:-<none>} (container $state) — waiting ${HEALTH_INTERVAL}s"
                ;;
        esac
        sleep "$HEALTH_INTERVAL"
    done
    log "health-gate TIMED OUT on $service after $((HEALTH_TRIES * HEALTH_INTERVAL))s"
    return 1
}

gate_all() {
    local svc
    for svc in "${GATE_SERVICES[@]}"; do
        wait_healthy "$svc" || return 1
    done
    return 0
}

# --- preflight ----------------------------------------------------------------
command -v git >/dev/null || die "git not found"
command -v docker >/dev/null || die "docker not found"
docker compose version >/dev/null 2>&1 || die "'docker compose' (v2 plugin) not found"

cd "$APP_DIR"
[[ -f "$COMPOSE_FILE" ]] || die "compose file not found: $APP_DIR/$COMPOSE_FILE"
[[ -f "$ENV_FILE" ]] || die "env file not found: $APP_DIR/$ENV_FILE — create it from .env.prod.example (deploy/runbook.md R2)"
if [[ -n "$REF" ]]; then
    [[ -d .git ]] || die "not a git checkout: $APP_DIR — clone the repo first, or run with REF= to skip the checkout"
fi

# The external network must already exist: compose declares it `external: true`
# so that `down` can never delete a network the edge and every co-tenant share.
# A missing one fails at `up` with a less obvious message than this.
EDGE_NETWORK="${MIJUAL_EDGE_NETWORK:-changple_shared_network}"
docker network inspect "$EDGE_NETWORK" >/dev/null 2>&1 \
    || die "external network '$EDGE_NETWORK' does not exist. On the box it is changple_shared_network (the one edge-nginx is attached to) and MIJUAL_EDGE_NETWORK must stay UNSET; in a rehearsal, create the throwaway one first."

# THE NO-HARM ASSERTION, measured rather than asserted. `edge-nginx` owns
# :80/:443 for every co-tenant on this box and belongs to a different compose
# project; recreating or restarting it drops the shared-network attachment and
# cascades into every other site. This script issues no command that names it —
# so record its StartedAt now and PROVE at the end that it did not move.
# (Absent = a rehearsal on a machine with no edge; then there is nothing to
# protect and the check reports that instead of failing.)
# `docker inspect` on a missing container writes an empty LINE to stdout before
# failing, so `|| echo absent` alone yields "\nabsent". Strip and default instead.
EDGE_STARTED_BEFORE="$(docker inspect -f '{{.State.StartedAt}}' edge-nginx 2>/dev/null | tr -d '\n' || true)"
[[ -n "$EDGE_STARTED_BEFORE" ]] || EDGE_STARTED_BEFORE=absent
if [[ "$EDGE_STARTED_BEFORE" == absent ]]; then
    log "edge-nginx not present here — no co-tenant edge to protect (rehearsal)"
else
    log "edge-nginx StartedAt before: $EDGE_STARTED_BEFORE (asserted unchanged at the end)"
fi

# Second half of the same guard: whatever compose project we are about to act on
# must not contain the edge. If it ever did, `up -d` would recreate it.
if dc ps --all --format '{{.Name}}' 2>/dev/null | grep -qx 'edge-nginx'; then
    die "refusing to continue: 'edge-nginx' is a container of compose project '${PROJECT:-mijual}'. The edge must be its own project — an 'up -d' here would recreate it and take every co-tenant site down."
fi

log "repo=$APP_DIR compose=$COMPOSE_FILE env=$ENV_FILE project=${PROJECT:-<compose default: mijual>} ref=${REF:-<skip checkout>} edge-network=$EDGE_NETWORK"

# --- 1. update the checkout ---------------------------------------------------
# .env.prod is gitignored so it survives; a dirty TRACKED tree makes `git
# checkout` fail loudly under `set -e`, which is correct — the box carries no
# local edits.
if [[ -n "$REF" ]]; then
    log "fetching + checking out $REF"
    git fetch --prune
    git checkout "$REF"
else
    log "REF is empty — skipping fetch/checkout (fresh clone or rehearsal); releasing the working tree as it stands"
fi

# --- 2. tag the live images as the rollback point -----------------------------
# BOTH images, before the build. A first deploy has neither, and that case must
# fail loudly rather than roll back to nothing.
have_previous=0
tagged=()
for img in "${IMAGES[@]}"; do
    if docker image inspect "$img:latest" >/dev/null 2>&1; then
        log "tagging $img:latest -> $img:previous (rollback point)"
        docker tag "$img:latest" "$img:previous"
        tagged+=("$img")
    else
        log "no existing $img:latest — nothing to tag"
    fi
done
if (( ${#tagged[@]} == ${#IMAGES[@]} )); then
    have_previous=1
elif (( ${#tagged[@]} > 0 )); then
    # One of two. Rolling back half the stack would pair a new web with an old
    # api (or worse, an old schema one-shot); refuse to treat that as a rollback
    # point and say so now rather than in the failure path.
    log "WARNING: only ${#tagged[@]}/${#IMAGES[@]} images had a :latest to tag — treating this as a FIRST deploy (no rollback point)"
else
    log "first deploy: neither image exists yet, so there is no rollback point"
fi

# --- 3. build -----------------------------------------------------------------
# Builds mijual-api AND mijual-web. The api must exist before `up`, because the
# schema one-shot, the worker and beat all run it with no `build:` of their own.
log "building $API_IMAGE:latest + $WEB_IMAGE:latest (COMPOSE_BAKE=false)"
dc build

# --- 4. up --------------------------------------------------------------------
# This is where `mijual-schema` runs. Its exit code gates the API
# (`service_completed_successfully`), so a schema failure stops the deploy here.
#
# ⚠ MEASURED IN THE P4.S3 REHEARSAL, and the reason `up` and the health gate
# share ONE failure path below: because `mijual-web` declares
# `depends_on: mijual-api: condition: service_healthy`, **compose itself waits
# for the API and `up -d` EXITS NON-ZERO** with "dependency failed to start:
# container … is unhealthy" — so a bad release usually never reaches this
# script's own gate at all. It leaves the api crash-looping and `mijual-web` in
# `Created`, i.e. the site down. An `up` failure is therefore a RELEASE FAILURE
# and must roll back exactly like a failed gate; treating it as a hard exit (the
# first version of this script did) left the stack broken and the previous good
# images sitting unused on disk.
release_ok=1
log "starting the stack (up -d) — this runs the mijual-schema one-shot first"
if ! dc up -d; then
    log "up FAILED — compose could not bring the stack to a healthy state."
    log "Two faults account for almost all of these:"
    log "  (a) mijual-schema exited non-zero — usually the POSTGRES_PASSWORD / DATABASE_URL"
    log "      mismatch: they are ONE secret written twice in $ENV_FILE, and POSTGRES_* are"
    log "      read only on FIRST init, so editing them later changes nothing in the volume;"
    log "  (b) mijual-api never became healthy, so compose refused to start mijual-web"
    log "      (that is the 'dependency failed to start … is unhealthy' message above)."
    log "--- mijual-schema logs ---"
    dc logs --no-color --tail 80 mijual-schema 2>&1 || true
    log "--- mijual-postgres logs (tail) ---"
    dc logs --no-color --tail 30 mijual-postgres 2>&1 || true
    release_ok=0
fi

# --- 5/6. health-gate; roll back on failure -----------------------------------
if (( release_ok )) && gate_all; then
    log "deploy healthy — $API_IMAGE:latest + $WEB_IMAGE:latest are live"
else
    if (( release_ok )); then
        log "HEALTH-GATE FAILED for the new build"
    else
        log "RELEASE FAILED at 'up' — treating it exactly like a failed health gate"
    fi
    log "--- mijual-web logs ---";    dc logs --no-color --tail 60 mijual-web 2>&1 || true
    log "--- mijual-api logs ---";    dc logs --no-color --tail 60 mijual-api 2>&1 || true
    log "--- mijual-schema logs ---"; dc logs --no-color --tail 40 mijual-schema 2>&1 || true
    if (( have_previous )); then
        log "rolling back: retagging both :previous -> :latest and re-upping WITHOUT a rebuild"
        for img in "${IMAGES[@]}"; do docker tag "$img:previous" "$img:latest"; done
        # `|| true`: this `up` can fail for exactly the reason the release did
        # (compose enforces mijual-web's `depends_on: mijual-api: service_healthy`
        # and exits non-zero), and under `set -e` that would abort the script
        # before it could say WHY — leaving the operator with a bare compose
        # error instead of "the rollback is also unhealthy". Measured in the
        # P4.S3 rehearsal. The verdict is `gate_all`'s to give, not `up`'s.
        dc up -d --no-build || log "the rollback's 'up' also reported a failure — gating anyway to see how bad it is"
        if gate_all; then
            die "the new build was unhealthy — ROLLED BACK to :previous (now healthy). Inspect the logs above."
        fi
        die "the new build was unhealthy AND the rollback to :previous is ALSO unhealthy — manual intervention required."
    else
        # First deploy: there is nothing to roll back to, and silently leaving a
        # half-broken stack up while exiting 0 would be the worse failure.
        die "the first deploy failed and there is no :previous to roll back to. Left as-is for inspection — check the logs above and $ENV_FILE."
    fi
fi

# --- 7. report ----------------------------------------------------------------
for svc in "${REPORT_SERVICES[@]}"; do
    cid="$(dc ps -q "$svc" 2>/dev/null || true)"
    if [[ -n "$cid" ]]; then
        status="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' "$cid" 2>/dev/null || true)"
        log "not gated, reported: $svc = ${status:-<none>}"
    fi
done

log "--- $(basename "$COMPOSE_FILE") ps ---"
dc ps

cat <<'NEXT'
[deploy] --- check these two things by hand, now ---
[deploy] 1. MAIL TRANSPORT. Run:
[deploy]        docker compose -f compose.prod.yml logs mijual-api | grep 'mail transport:'
[deploy]    `mail transport: smtp …` = SMTP_PASS is filled and mail will send.
[deploy]    `mail transport: console (SMTP_HOST unset …)` = the product serves
[deploy]    perfectly and mails NOBODY. That is a supported state, and on the box
[deploy]    it means someone forgot the password.
[deploy] 2. BEAT IS ALIVE AND CARRIES FOUR ENTRIES. Celery's startup banner does
[deploy]    NOT print the schedule (measured), so ask the app directly:
[deploy]        docker compose -f compose.prod.yml exec -T mijual-beat python -c \
[deploy]          "from mijual.scheduler.app import app; [print(k, v['task'], v['schedule']) for k, v in sorted(app.conf.beat_schedule.items())]"
[deploy]    Expect four: daily-pipeline-morning 07:30, daily-pipeline-evening 19:30,
[deploy]    weekly-resync Sun 04:30, and notify-deadlines 08:30 (the D-day mail).
[deploy]    `docker compose -f compose.prod.yml logs mijual-beat` should end in
[deploy]    "beat: Starting...".
NEXT

# The other half of the no-harm assertion (see the preflight).
EDGE_STARTED_AFTER="$(docker inspect -f '{{.State.StartedAt}}' edge-nginx 2>/dev/null | tr -d '\n' || true)"
[[ -n "$EDGE_STARTED_AFTER" ]] || EDGE_STARTED_AFTER=absent
if [[ "$EDGE_STARTED_AFTER" != "$EDGE_STARTED_BEFORE" ]]; then
    die "edge-nginx StartedAt CHANGED during this deploy ($EDGE_STARTED_BEFORE -> $EDGE_STARTED_AFTER). Something here touched the shared edge — investigate before deploying again; every co-tenant site is affected."
fi
[[ "$EDGE_STARTED_BEFORE" == absent ]] || log "ok — edge-nginx StartedAt unchanged ($EDGE_STARTED_AFTER)"

log "DONE — released at ref ${REF:-<working tree>}; the edge proxies jujutower.com to mijual-web:3010."
