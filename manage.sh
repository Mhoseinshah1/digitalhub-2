#!/usr/bin/env bash
#
# AppStore Bot — management CLI.
# Symlinked to /usr/local/bin/appstore by install.sh.
#
#   appstore {start|stop|restart|update|logs|backup|restore|admin-reset|status}
#
set -euo pipefail

INSTALL_DIR="${INSTALL_DIR:-/opt/appstore-bot}"
BACKUP_DIR="$INSTALL_DIR/backups"
COMPOSE_ENV_FILE="$INSTALL_DIR/compose.env"

c_info() { printf '\033[1;34m[*]\033[0m %s\n' "$*"; }
c_ok()   { printf '\033[1;32m[+]\033[0m %s\n' "$*"; }
c_err()  { printf '\033[1;31m[x]\033[0m %s\n' "$*" >&2; }
die()    { c_err "$*"; exit 1; }

cd "$INSTALL_DIR" || die "Install dir $INSTALL_DIR not found."

# Ensure compose.env exists (older installs only had .env). It holds just
# DB_PASSWORD for Compose interpolation; the app reads ./.env via a mount.
ensure_compose_env() {
  [ -f "$COMPOSE_ENV_FILE" ] && return 0
  [ -f "$INSTALL_DIR/.env" ] || die ".env not found; run install.sh first."
  local pw
  pw="$(grep -E '^DB_PASSWORD=' "$INSTALL_DIR/.env" | head -n1 | cut -d= -f2-)"
  ( umask 077; printf 'DB_PASSWORD=%s\n' "${pw//\$/\$\$}" > "$COMPOSE_ENV_FILE" )
  chmod 600 "$COMPOSE_ENV_FILE"
}
ensure_compose_env

# docker compose wrapper using our dedicated env file (never auto-loads ./.env).
dc() { docker compose --env-file "$COMPOSE_ENV_FILE" "$@"; }

usage() {
  cat <<EOF
Usage: appstore <command>

Commands:
  start         Start all services
  stop          Stop all services
  restart       Restart all services
  update        Pull latest, back up DB, rebuild, migrate (rollback on error)
  logs [svc]    Tail logs (optionally for one service: bot|web|db|redis|nginx)
  backup        Dump the database to backups/
  restore FILE  Restore the database from a backup file
  admin-reset   Reset the web admin password (prompts for a new one)
  status        Show service status
EOF
}

cmd_start()   { dc up -d; c_ok "Started."; }
cmd_stop()    { dc down; c_ok "Stopped."; }
cmd_restart() { dc restart; c_ok "Restarted."; }
cmd_status()  { dc ps; }

cmd_logs() {
  if [ "${1:-}" = "" ]; then dc logs -f --tail=200
  else dc logs -f --tail=200 "$1"; fi
}

cmd_update() { bash "$INSTALL_DIR/update.sh"; }

cmd_backup() {
  mkdir -p "$BACKUP_DIR"
  local f="$BACKUP_DIR/manual_$(date +%Y%m%d_%H%M%S).sql"
  dc exec -T db pg_dump -U appstore appstore > "$f"
  c_ok "Backup written to $f"
}

cmd_restore() {
  local f="${1:-}"
  [ -n "$f" ] && [ -f "$f" ] || die "Provide a valid backup file: appstore restore <file>"
  c_info "Restoring database from $f…"
  dc exec -T db psql -U appstore -d appstore < "$f"
  c_ok "Restore complete."
}

cmd_admin_reset() {
  local pw1 pw2
  while :; do
    read -rsp "New web admin password: " pw1; echo
    read -rsp "Confirm password: " pw2; echo
    [ -n "$pw1" ] && [ "$pw1" = "$pw2" ] && break
    c_err "Passwords empty or do not match; try again."
  done
  c_info "Hashing password…"
  local hash
  hash="$(dc run --rm --no-deps -e PW="$pw1" web \
    python -c 'import os; from passlib.hash import bcrypt; print(bcrypt.hash(os.environ["PW"]))' \
    2>/dev/null | tr -d "\r" | tail -n 1)"
  [ -n "$hash" ] || die "Failed to hash password."
  # Replace the hash line in .env in place (preserves chmod 600).
  if grep -q '^WEB_ADMIN_PASSWORD_HASH=' .env; then
    sed -i "s|^WEB_ADMIN_PASSWORD_HASH=.*|WEB_ADMIN_PASSWORD_HASH=${hash}|" .env
  else
    echo "WEB_ADMIN_PASSWORD_HASH=${hash}" >> .env
  fi
  unset pw1 pw2
  dc up -d web
  c_ok "Admin password updated. Web service restarted."
}

main() {
  local cmd="${1:-}"; shift || true
  case "$cmd" in
    start)        cmd_start ;;
    stop)         cmd_stop ;;
    restart)      cmd_restart ;;
    update)       cmd_update ;;
    logs)         cmd_logs "${1:-}" ;;
    backup)       cmd_backup ;;
    restore)      cmd_restore "${1:-}" ;;
    admin-reset)  cmd_admin_reset ;;
    status)       cmd_status ;;
    ""|-h|--help) usage ;;
    *)            c_err "Unknown command: $cmd"; usage; exit 1 ;;
  esac
}

main "$@"
