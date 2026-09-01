#!/usr/bin/env bash
#
# backup.sh — a custom-format pg_dump of the production database.
#
# ⚠ A DUMP FROM THIS SCRIPT CONTAINS PERSONAL DATA. The `account` table holds
# READER EMAIL ADDRESSES and PASSWORD HASHES, and `notification_send` joins an
# address to what that person is watching. Consequences, all of them binding:
#   * the file stays ON THE BOX, under deploy/backups/, mode 700 on the
#     directory and 600 on every dump (this script enforces both);
#   * it is NEVER committed (.gitignore carries `deploy/backups/`);
#   * it is never copied to a laptop, a chat, a ticket or a bug report;
#   * if one must move, it moves encrypted and the copy is deleted afterwards.
#
# WHAT IT COVERS. `mijual-pgdata` — the ONLY non-regenerable volume in this
# stack. `mijual-redisdata` (broker state + the run lock) and `mijual-var` (the
# DART response cache, beat's shelve, the file-lock fallback) are deliberately
# NOT backed up: both regenerate, though re-collecting the DART cache costs
# OpenDART quota.
#
# HOW. `pg_dump -Fc` (custom format: compressed, and `pg_restore` can list and
# selectively restore from it) run INSIDE the postgres container over
# `compose exec -T`, so it needs no client on the host and no published port.
#
#     deploy/db/backup.sh
#     KEEP=30 deploy/db/backup.sh          # keep the newest 30 instead of 14
#     OUT_DIR=/some/where deploy/db/backup.sh
#
# Knobs: APP_DIR / COMPOSE_FILE / ENV_FILE / PROJECT (as deploy.sh — UNSET on
# the box), OUT_DIR (default $APP_DIR/deploy/backups), KEEP (default 14),
# DB_SERVICE (default mijual-postgres).
#
# Cron: see deploy/runbook.md R7 for the suggested nightly line. Installing it
# is an open decision for P4.S4, not something this script does.

set -euo pipefail

APP_DIR="${APP_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
COMPOSE_FILE="${COMPOSE_FILE:-compose.prod.yml}"
ENV_FILE="${ENV_FILE:-.env.prod}"
PROJECT="${PROJECT:-}"
DB_SERVICE="${DB_SERVICE:-mijual-postgres}"
KEEP="${KEEP:-14}"

log() { printf '[backup] %s\n' "$*"; }
die() { printf '[backup] ERROR: %s\n' "$*" >&2; exit 1; }

dc() {
    if [[ -n "$PROJECT" ]]; then
        docker compose -p "$PROJECT" -f "$COMPOSE_FILE" "$@"
    else
        docker compose -f "$COMPOSE_FILE" "$@"
    fi
}

# Read ONE key out of the env file. Deliberately NOT `source` and deliberately
# not a `grep` of the whole file into the log: this file holds every secret the
# product has, and the rule from P4.S2 stands — nothing here ever echoes it.
# (The same rule is why no deploy script may `print(load_settings())`:
# Settings.__repr__ masks the API keys but the URL password only since P4.S2.)
env_value() {
    local key="$1" line
    line="$(grep -E "^${key}=" "$ENV_FILE" | tail -n 1 || true)"
    [[ -n "$line" ]] || return 1
    line="${line#*=}"
    # strip one layer of surrounding quotes if present
    line="${line%\"}"; line="${line#\"}"
    line="${line%\'}"; line="${line#\'}"
    printf '%s' "$line"
}

# --- preflight ----------------------------------------------------------------
command -v docker >/dev/null || die "docker not found"
docker compose version >/dev/null 2>&1 || die "'docker compose' (v2 plugin) not found"

cd "$APP_DIR"
[[ -f "$COMPOSE_FILE" ]] || die "compose file not found: $APP_DIR/$COMPOSE_FILE"
[[ -f "$ENV_FILE" ]] || die "env file not found: $APP_DIR/$ENV_FILE"

OUT_DIR="${OUT_DIR:-$APP_DIR/deploy/backups}"

PG_USER="$(env_value POSTGRES_USER || true)"
PG_DB="$(env_value POSTGRES_DB || true)"
[[ -n "$PG_USER" ]] || die "POSTGRES_USER not found in $ENV_FILE"
[[ -n "$PG_DB" ]] || die "POSTGRES_DB not found in $ENV_FILE"

cid="$(dc ps -q "$DB_SERVICE" 2>/dev/null || true)"
[[ -n "$cid" ]] || die "$DB_SERVICE is not running — start the stack first (deploy/deploy.sh)"

# 700: the directory itself is the first line of defence for what is inside it.
mkdir -p "$OUT_DIR"
chmod 700 "$OUT_DIR"

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="$OUT_DIR/mijual-$STAMP.dump"
TMP="$OUT.partial"

log "dumping $PG_DB as $PG_USER from $DB_SERVICE -> $OUT"

# Write to .partial first and rename only on success: a truncated dump that
# looks like a backup is worse than no backup. `exec -T` = no TTY, so the binary
# stream is not mangled.
umask 077
if ! dc exec -T "$DB_SERVICE" pg_dump -U "$PG_USER" -Fc "$PG_DB" > "$TMP"; then
    rm -f "$TMP"
    die "pg_dump failed — nothing written."
fi
mv "$TMP" "$OUT"
chmod 600 "$OUT"

SIZE="$(du -h "$OUT" | awk '{print $1}')"
log "wrote $OUT ($SIZE, mode 600)"

# --- verify the dump is readable and count what is in it ----------------------
# `pg_restore --list` reads the archive's TOC. It proves the file is a valid
# custom-format archive without touching any database. The TABLE DATA entries
# are the table count the runbook checks against (19 as of P4.S2).
TOC="$(mktemp)"
trap 'rm -f "$TOC"' EXIT
if ! docker exec -i "$cid" pg_restore --list < "$OUT" > "$TOC" 2>/dev/null; then
    die "the dump was written but pg_restore --list could not read it — treat it as INVALID: $OUT"
fi
TABLES="$(grep -c 'TABLE DATA' "$TOC" || true)"
log "verified: valid custom-format archive, $TABLES tables with data (expect 19 as of P4.S2)"

# --- rotation -----------------------------------------------------------------
# Newest KEEP kept, the rest deleted. Sorted by NAME, which is a UTC timestamp in
# a fixed-width sortable format, so name order IS chronological order — no
# dependence on mtime, which a copy or a restore-from-tape would scramble.
# (A `while read` loop rather than `mapfile`: bash 3.2 is still what a macOS
# rehearsal runs, and this script must behave identically in both places.)
n=0
find "$OUT_DIR" -maxdepth 1 -name 'mijual-*.dump' -type f | sort -r | while IFS= read -r dump; do
    n=$((n + 1))
    if (( n > KEEP )); then
        log "rotating out $(basename "$dump")"
        rm -f "$dump"
    fi
done
log "retention: $(find "$OUT_DIR" -maxdepth 1 -name 'mijual-*.dump' -type f | wc -l | tr -d ' ') dump(s) kept (KEEP=$KEEP)"

log "DONE. Restore with: deploy/db/restore.sh $OUT --yes"
log "REMINDER: this file holds reader emails and password hashes. It stays on this box."
