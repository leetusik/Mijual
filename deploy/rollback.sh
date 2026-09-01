#!/usr/bin/env bash
#
# rollback.sh — roll 주주의관제탑 back to the previous image pair.
#
# The manual counterpart to `deploy.sh`'s automatic rollback. Use it for a
# release that PASSED its health gate but misbehaves later.
#
# `deploy.sh` tags BOTH `mijual-api:latest` and `mijual-web:latest` as
# `:previous` at the START of every deploy, so this reverts to exactly the pair
# that was live before the last release. It requires BOTH: rolling back half the
# stack would pair a new web with an old api — or, worse, an old `mijual-schema`
# one-shot against a schema the new code already migrated — and neither is a
# state anyone can reason about at 3am.
#
# NO REBUILD. `up -d --no-build` recreates the containers from the retagged
# images. That is the whole point: a rollback must not depend on a build
# succeeding.
#
# NOT A DATA ROLLBACK. `python -m mijual.db ensure` is additive and idempotent
# and there are no migrations, so an older image runs fine against a newer
# schema — extra columns are simply unread. What this does NOT undo is DATA. For
# that see deploy/db/restore.sh, which is a separate, deliberate act.
#
# If `:previous` is gone (pruned, or you must go back more than one release),
# use a git-ref rebuild instead:  REF=<prior-good-sha> deploy/deploy.sh
#
#     deploy/rollback.sh
#
# Knobs: the same as deploy.sh (APP_DIR / COMPOSE_FILE / ENV_FILE / PROJECT /
# HEALTH_TRIES / HEALTH_INTERVAL / MIJUAL_EDGE_NETWORK). PROJECT stays UNSET on
# the box.

set -euo pipefail

APP_DIR="${APP_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
COMPOSE_FILE="${COMPOSE_FILE:-compose.prod.yml}"
ENV_FILE="${ENV_FILE:-.env.prod}"
PROJECT="${PROJECT:-}"
HEALTH_TRIES="${HEALTH_TRIES:-40}"
HEALTH_INTERVAL="${HEALTH_INTERVAL:-5}"

API_IMAGE="${API_IMAGE:-mijual-api}"
WEB_IMAGE="${WEB_IMAGE:-mijual-web}"
IMAGES=("$API_IMAGE" "$WEB_IMAGE")
GATE_SERVICES=(mijual-web mijual-api)

export COMPOSE_BAKE=false

log() { printf '[rollback] %s\n' "$*"; }
die() { printf '[rollback] ERROR: %s\n' "$*" >&2; exit 1; }

dc() {
    if [[ -n "$PROJECT" ]]; then
        docker compose -p "$PROJECT" -f "$COMPOSE_FILE" "$@"
    else
        docker compose -f "$COMPOSE_FILE" "$@"
    fi
}

# Same gate contract as deploy.sh — see its comments.
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
        state="$(docker inspect --format '{{.State.Status}}' "$cid" 2>/dev/null || true)"
        case "$status" in
            healthy)   log "$service healthy on poll $i"; return 0 ;;
            unhealthy) log "$service reported UNHEALTHY on poll $i"; return 1 ;;
            none)
                if [[ "$state" == running ]]; then
                    log "$service is running but has NO healthcheck — cannot gate on it"; return 1
                fi
                log "poll $i/$HEALTH_TRIES: $service is '$state', not running — waiting ${HEALTH_INTERVAL}s" ;;
            *)         log "poll $i/$HEALTH_TRIES: $service=${status:-<none>} (container $state) — waiting ${HEALTH_INTERVAL}s" ;;
        esac
        sleep "$HEALTH_INTERVAL"
    done
    log "health-gate TIMED OUT on $service after $((HEALTH_TRIES * HEALTH_INTERVAL))s"
    return 1
}

# --- preflight ----------------------------------------------------------------
command -v docker >/dev/null || die "docker not found"
docker compose version >/dev/null 2>&1 || die "'docker compose' (v2 plugin) not found"

cd "$APP_DIR"
[[ -f "$COMPOSE_FILE" ]] || die "compose file not found: $APP_DIR/$COMPOSE_FILE"
[[ -f "$ENV_FILE" ]] || die "env file not found: $APP_DIR/$ENV_FILE (compose needs it to recreate the containers)"

EDGE_NETWORK="${MIJUAL_EDGE_NETWORK:-changple_shared_network}"
docker network inspect "$EDGE_NETWORK" >/dev/null 2>&1 \
    || die "external network '$EDGE_NETWORK' does not exist"

missing=()
for img in "${IMAGES[@]}"; do
    docker image inspect "$img:previous" >/dev/null 2>&1 || missing+=("$img:previous")
done
if (( ${#missing[@]} )); then
    die "no rollback point: ${missing[*]} missing. Both images are required. Use a git-ref rebuild instead: REF=<prior-good-sha> deploy/deploy.sh"
fi

# The same measured no-harm assertion deploy.sh makes.
# `docker inspect` on a missing container writes an empty LINE to stdout before
# failing, so `|| echo absent` alone yields "\nabsent". Strip and default instead.
EDGE_STARTED_BEFORE="$(docker inspect -f '{{.State.StartedAt}}' edge-nginx 2>/dev/null | tr -d '\n' || true)"
[[ -n "$EDGE_STARTED_BEFORE" ]] || EDGE_STARTED_BEFORE=absent

# --- retag, recreate, gate ----------------------------------------------------
for img in "${IMAGES[@]}"; do
    log "retagging $img:previous -> $img:latest"
    docker tag "$img:previous" "$img:latest"
done

log "recreating the stack from the rolled-back images (up -d --no-build)"
# `|| true` for the same reason deploy.sh's rollback path carries it: compose
# enforces mijual-web's `depends_on: mijual-api: service_healthy` and exits
# non-zero when the image being rolled back to is ALSO broken. Under `set -e`
# that would abort before this script could say so. The gate below is the verdict.
dc up -d --no-build || log "'up' reported a failure — gating anyway to see how bad it is"

ok=1
for svc in "${GATE_SERVICES[@]}"; do
    wait_healthy "$svc" || { ok=0; break; }
done

EDGE_STARTED_AFTER="$(docker inspect -f '{{.State.StartedAt}}' edge-nginx 2>/dev/null | tr -d '\n' || true)"
[[ -n "$EDGE_STARTED_AFTER" ]] || EDGE_STARTED_AFTER=absent
[[ "$EDGE_STARTED_AFTER" == "$EDGE_STARTED_BEFORE" ]] \
    || die "edge-nginx StartedAt CHANGED during this rollback ($EDGE_STARTED_BEFORE -> $EDGE_STARTED_AFTER) — investigate; every co-tenant site is affected."

if (( ok )); then
    log "--- ps ---"
    dc ps
    log "DONE — rolled back to the :previous image pair, healthy. NOTE: :previous and :latest now point at the SAME images, so the next deploy.sh run will write a fresh rollback point over them."
else
    log "--- mijual-web logs ---"; dc logs --no-color --tail 60 mijual-web 2>&1 || true
    log "--- mijual-api logs ---"; dc logs --no-color --tail 60 mijual-api 2>&1 || true
    die "rolled back to :previous but the stack is NOT healthy — manual intervention required (logs above)."
fi
