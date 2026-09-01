#!/usr/bin/env bash
#
# restore.sh — restore a `deploy/db/backup.sh` dump into the RUNNING database.
#
# ⚠ THIS IS DESTRUCTIVE AND IT IS NOT A ROLLBACK. It drops and recreates every
# object the dump contains (`pg_restore --clean --if-exists`), so everything a
# reader did since that dump was taken is gone: accounts created, portfolios
# edited, notification rows written, conversation turns logged. There is no undo
# beyond a newer dump — so TAKE ONE FIRST (`deploy/db/backup.sh`) even when the
# database looks broken. A code rollback is `deploy/rollback.sh` and touches no
# data at all; reach for this only when the DATA is what is wrong.
#
# ⚠ THE DUMP HOLDS PERSONAL DATA — reader email addresses and password hashes.
# See the header of backup.sh: it stays on the box, 600, never committed, never
# copied off.
#
#     deploy/db/restore.sh deploy/backups/mijual-20260902T041500Z.dump --yes
#
# `--yes` is required. Without it the script prints what it WOULD do and exits
# non-zero, which makes a fat-fingered command harmless.
#
# WHAT IT DOES, in order:
#   1. verify the file is a readable custom-format archive (`pg_restore --list`);
#   2. `pg_restore --clean --if-exists --no-owner` over `exec -T` stdin into the
#      running database (`--no-owner` because the dump's role names need not
#      exist here; everything lands owned by POSTGRES_USER);
#   3. run the schema bootstrap — `python -m mijual.db ensure` — so a dump older
#      than the code still gets the tables and columns the current build expects.
#      This is exactly what `mijual-schema` does on every `up`, and it is
#      additive and idempotent;
#   4. restart the API/worker/beat so nothing is holding a stale connection or a
#      cached mapping, then health-gate.
#
# Knobs: APP_DIR / COMPOSE_FILE / ENV_FILE / PROJECT (as deploy.sh — UNSET on
# the box), DB_SERVICE (default mijual-postgres), HEALTH_TRIES / HEALTH_INTERVAL.

set -euo pipefail

APP_DIR="${APP_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
COMPOSE_FILE="${COMPOSE_FILE:-compose.prod.yml}"
ENV_FILE="${ENV_FILE:-.env.prod}"
PROJECT="${PROJECT:-}"
DB_SERVICE="${DB_SERVICE:-mijual-postgres}"
HEALTH_TRIES="${HEALTH_TRIES:-40}"
HEALTH_INTERVAL="${HEALTH_INTERVAL:-5}"

log() { printf '[restore] %s\n' "$*"; }
die() { printf '[restore] ERROR: %s\n' "$*" >&2; exit 1; }

dc() {
    if [[ -n "$PROJECT" ]]; then
        docker compose -p "$PROJECT" -f "$COMPOSE_FILE" "$@"
    else
        docker compose -f "$COMPOSE_FILE" "$@"
    fi
}

env_value() {
    local key="$1" line
    line="$(grep -E "^${key}=" "$ENV_FILE" | tail -n 1 || true)"
    [[ -n "$line" ]] || return 1
    line="${line#*=}"
    line="${line%\"}"; line="${line#\"}"
    line="${line%\'}"; line="${line#\'}"
    printf '%s' "$line"
}

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

# --- arguments ----------------------------------------------------------------
DUMP=""
CONFIRMED=0
for arg in "$@"; do
    case "$arg" in
        --yes) CONFIRMED=1 ;;
        -*)    die "unknown option: $arg (usage: deploy/db/restore.sh <dump> --yes)" ;;
        *)     [[ -z "$DUMP" ]] || die "more than one dump given"; DUMP="$arg" ;;
    esac
done
[[ -n "$DUMP" ]] || die "usage: deploy/db/restore.sh <dump-file> --yes"
[[ -f "$DUMP" ]] || die "no such dump: $DUMP"
DUMP="$(cd "$(dirname "$DUMP")" && pwd)/$(basename "$DUMP")"

# --- preflight ----------------------------------------------------------------
command -v docker >/dev/null || die "docker not found"
docker compose version >/dev/null 2>&1 || die "'docker compose' (v2 plugin) not found"

cd "$APP_DIR"
[[ -f "$COMPOSE_FILE" ]] || die "compose file not found: $APP_DIR/$COMPOSE_FILE"
[[ -f "$ENV_FILE" ]] || die "env file not found: $APP_DIR/$ENV_FILE"

PG_USER="$(env_value POSTGRES_USER || true)"
PG_DB="$(env_value POSTGRES_DB || true)"
[[ -n "$PG_USER" ]] || die "POSTGRES_USER not found in $ENV_FILE"
[[ -n "$PG_DB" ]] || die "POSTGRES_DB not found in $ENV_FILE"

cid="$(dc ps -q "$DB_SERVICE" 2>/dev/null || true)"
[[ -n "$cid" ]] || die "$DB_SERVICE is not running — start the stack first (deploy/deploy.sh)"

# --- 1. verify the archive BEFORE destroying anything --------------------------
TOC="$(mktemp)"
trap 'rm -f "$TOC"' EXIT
docker exec -i "$cid" pg_restore --list < "$DUMP" > "$TOC" 2>/dev/null \
    || die "not a readable custom-format archive: $DUMP"
TABLES="$(grep -c 'TABLE DATA' "$TOC" || true)"
log "archive OK: $DUMP ($(du -h "$DUMP" | awk '{print $1}'), $TABLES tables with data)"

if (( ! CONFIRMED )); then
    cat >&2 <<EOF
[restore] REFUSING — this would DROP AND RECREATE every object in $PG_DB
[restore] and replace it with the contents of:
[restore]     $DUMP
[restore] Everything written since that dump was taken would be lost.
[restore] Take a fresh backup first (deploy/db/backup.sh), then re-run with --yes.
EOF
    exit 2
fi

# --- 2. restore ---------------------------------------------------------------
# `--clean --if-exists` so a re-restore is not blocked by existing objects, and
# so a first restore into an empty database does not fail on the DROPs.
# `--no-owner` because role names in the dump need not exist here.
# NOT `--exit-on-error`: --clean's DROPs against a partially-populated database
# emit harmless NOTICEs and the odd error, and aborting on the first one would
# leave the database in a worse state than finishing. The proof of the restore
# is the table count and the health gate below, not a zero exit from pg_restore.
log "restoring into $PG_DB as $PG_USER (this drops and recreates the dumped objects)"
if ! docker exec -i "$cid" pg_restore --clean --if-exists --no-owner \
        -U "$PG_USER" -d "$PG_DB" < "$DUMP"; then
    log "pg_restore exited non-zero — that is common with --clean (DROP of an absent object)."
    log "Continuing to the schema bootstrap and the health gate, which are the real proof."
fi

# --- 3. schema bootstrap ------------------------------------------------------
# A dump older than the code is missing whatever tables/columns landed since.
# `mijual.db ensure` is create_all + ensure_columns: additive, idempotent, and
# exactly what the mijual-schema one-shot runs on every `up`.
log "running the schema bootstrap (python -m mijual.db ensure) over the restored database"
dc run --rm --no-deps mijual-schema

# --- 4. restart the app processes and gate ------------------------------------
# They hold pooled connections to objects that were just dropped and recreated.
log "restarting mijual-api / mijual-worker / mijual-beat"
dc restart mijual-api mijual-worker mijual-beat

for svc in mijual-api mijual-web; do
    wait_healthy "$svc" || {
        log "--- $svc logs ---"; dc logs --no-color --tail 60 "$svc" 2>&1 || true
        die "restore completed but $svc is NOT healthy — manual intervention required."
    }
done

log "--- ps ---"
dc ps
log "DONE — restored from $DUMP, schema ensured, api + web healthy."
log "REMINDER: the dump holds reader emails and password hashes. It stays on this box."
