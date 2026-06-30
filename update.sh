#!/usr/bin/env bash
#
# AppStore Bot — safe self-update.
#
# Compares the local VERSION with upstream, backs up the database BEFORE any
# change, pulls from the repo, rebuilds, restarts and runs migrations. On any
# error it rolls back the database from the pre-update backup. Never touches
# .env or the database volume data directly.
#
set -euo pipefail

REPO_URL="https://github.com/Mhoseinshah1/digitalhub-2"
INSTALL_DIR="${INSTALL_DIR:-/opt/appstore-bot}"
BACKUP_DIR="$INSTALL_DIR/backups"
COMPOSE_ENV_FILE="$INSTALL_DIR/compose.env"

c_info() { printf '\033[1;34m[*]\033[0m %s\n' "$*"; }
c_ok()   { printf '\033[1;32m[+]\033[0m %s\n' "$*"; }
c_warn() { printf '\033[1;33m[!]\033[0m %s\n' "$*"; }
c_err()  { printf '\033[1;31m[x]\033[0m %s\n' "$*" >&2; }
die()    { c_err "$*"; exit 1; }

cd "$INSTALL_DIR" || die "Install dir $INSTALL_DIR not found."
[ -f .env ] || die ".env missing; run install.sh first."

# Ensure compose.env exists (older installs only had .env), then wrap compose.
ensure_compose_env() {
  [ -f "$COMPOSE_ENV_FILE" ] && return 0
  local pw
  pw="$(grep -E '^DB_PASSWORD=' .env | head -n1 | cut -d= -f2- || true)"
  [ -n "$pw" ] || die "No DB_PASSWORD= line in .env; cannot generate compose.env."
  ( umask 077; printf 'DB_PASSWORD=%s\n' "${pw//\$/\$\$}" > "$COMPOSE_ENV_FILE" )
  chmod 600 "$COMPOSE_ENV_FILE"
}
ensure_compose_env
dc() { docker compose --env-file "$COMPOSE_ENV_FILE" "$@"; }

backup_db() {
  mkdir -p "$BACKUP_DIR"
  BACKUP_FILE="$BACKUP_DIR/pre_update_$(date +%Y%m%d_%H%M%S).sql"
  c_info "Backing up database to $BACKUP_FILE…"
  dc exec -T db pg_dump -U appstore appstore > "$BACKUP_FILE" \
    || die "Database backup failed; aborting update."
  c_ok "Backup complete."
}

restore_db() {
  [ -n "${BACKUP_FILE:-}" ] && [ -f "$BACKUP_FILE" ] || { c_warn "No backup to restore."; return; }
  c_warn "Rolling back database from $BACKUP_FILE…"
  dc exec -T db psql -U appstore -d appstore < "$BACKUP_FILE" \
    && c_ok "Database restored." || c_err "Restore failed; backup kept at $BACKUP_FILE."
}

check_version() {
  c_info "Checking for updates…"
  git fetch origin main --quiet
  local_ver="$(cat VERSION 2>/dev/null || echo 0)"
  remote_ver="$(git show origin/main:VERSION 2>/dev/null || echo 0)"
  c_info "Local version: $local_ver | Remote version: $remote_ver"
  if [ "$local_ver" = "$remote_ver" ] && git diff --quiet HEAD origin/main; then
    c_ok "Already up to date. Nothing to do."
    exit 0
  fi
}

do_update() {
  backup_db
  # Roll back the DB if anything below fails.
  trap 'c_err "Update failed."; restore_db; exit 1' ERR

  c_info "Pulling latest code…"
  git pull origin main --ff-only

  c_info "Rebuilding and restarting services…"
  dc up -d --build

  c_info "Applying migrations…"
  dc run --rm web alembic upgrade head

  trap - ERR
  c_ok "Update complete (now at version $(cat VERSION))."
}

check_version
do_update
dc ps
