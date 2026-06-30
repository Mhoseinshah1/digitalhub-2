#!/usr/bin/env bash
#
# AppStore Bot — interactive installer (Ubuntu).
#
#   bash <(curl -fsSL https://raw.githubusercontent.com/Mhoseinshah1/digitalhub-2/main/install.sh)
#
# Installs Docker/Compose/Git if missing, clones the repo into /opt/appstore-bot,
# collects configuration interactively, writes a chmod 600 .env (no plaintext
# secrets ever printed), builds the stack, runs migrations, creates the main
# admin and provisions nginx + SSL.
#
set -euo pipefail

REPO_URL="https://github.com/Mhoseinshah1/digitalhub-2"
INSTALL_DIR="/opt/appstore-bot"
APP_NAME="appstore"

# --- helpers -----------------------------------------------------------------
c_info()  { printf '\033[1;34m[*]\033[0m %s\n' "$*"; }
c_ok()    { printf '\033[1;32m[+]\033[0m %s\n' "$*"; }
c_warn()  { printf '\033[1;33m[!]\033[0m %s\n' "$*"; }
c_err()   { printf '\033[1;31m[x]\033[0m %s\n' "$*" >&2; }
die()     { c_err "$*"; exit 1; }

require_root() {
  [ "$(id -u)" -eq 0 ] || die "Please run as root (sudo)."
}

require_ubuntu() {
  [ -f /etc/os-release ] || die "Cannot detect OS."
  . /etc/os-release
  [ "${ID:-}" = "ubuntu" ] || c_warn "Tested on Ubuntu; detected '${ID:-unknown}'. Continuing."
}

# Repoint apt at old-releases.ubuntu.com for End-Of-Life Ubuntu releases whose
# regular mirrors have been retired (e.g. oracular). Backs up sources first.
fix_eol_apt_sources() {
  local codename ts backup_dir
  codename="$(. /etc/os-release && echo "${VERSION_CODENAME:-}")"
  ts="$(date +%Y%m%d_%H%M%S)"
  # Keep backups OUT of sources.list.d/ so apt doesn't warn about them.
  backup_dir="/var/backups/appstore-apt-${ts}"
  mkdir -p "$backup_dir"
  c_warn "apt update failed — your Ubuntu release ('${codename:-unknown}') looks End-Of-Life."
  printf '    Repoint apt to old-releases.ubuntu.com so packages can be installed? [y/N] '
  read -r reply
  case "$reply" in
    y|Y|yes|YES) ;;
    *) return 1 ;;
  esac

  # deb822 format (Ubuntu 24.x default): /etc/apt/sources.list.d/ubuntu.sources
  if [ -f /etc/apt/sources.list.d/ubuntu.sources ]; then
    cp -a /etc/apt/sources.list.d/ubuntu.sources "$backup_dir/"
    sed -i -E \
      -e 's#https?://[a-zA-Z0-9._-]*archive\.ubuntu\.com/ubuntu#http://old-releases.ubuntu.com/ubuntu#g' \
      -e 's#https?://security\.ubuntu\.com/ubuntu#http://old-releases.ubuntu.com/ubuntu#g' \
      /etc/apt/sources.list.d/ubuntu.sources
  fi
  # classic format: /etc/apt/sources.list
  if [ -f /etc/apt/sources.list ]; then
    cp -a /etc/apt/sources.list "$backup_dir/"
    sed -i -E \
      -e 's#https?://[a-zA-Z0-9._-]*archive\.ubuntu\.com/ubuntu#http://old-releases.ubuntu.com/ubuntu#g' \
      -e 's#https?://security\.ubuntu\.com/ubuntu#http://old-releases.ubuntu.com/ubuntu#g' \
      /etc/apt/sources.list
  fi
  c_info "Sources repointed (backups saved in ${backup_dir}). Retrying apt update…"
  apt-get update -y >/dev/null 2>&1
}

install_prereqs() {
  c_info "Checking prerequisites…"

  # apt update may fail on EOL releases; tolerate it and offer a repair.
  if ! apt-get update -y >/dev/null 2>&1; then
    fix_eol_apt_sources || c_warn "Continuing without a working apt index; \
already-installed tools will still be used."
  fi

  apt_install() {  # install a package, surfacing a clear error on failure
    apt-get install -y "$1" >/dev/null 2>&1 \
      || die "Could not install '$1' (apt is unavailable). Install it manually and re-run."
  }

  command -v git  >/dev/null 2>&1 || { c_info "Installing git…";  apt_install git; }
  command -v curl >/dev/null 2>&1 || { c_info "Installing curl…"; apt_install curl; }

  if ! command -v docker >/dev/null 2>&1; then
    c_info "Installing Docker…"
    curl -fsSL https://get.docker.com | sh >/dev/null \
      || die "Docker installation failed. Install Docker Engine manually and re-run."
  fi

  if ! docker compose version >/dev/null 2>&1; then
    c_info "Installing Docker Compose plugin…"
    apt-get install -y docker-compose-plugin >/dev/null 2>&1 || true
  fi
  docker compose version >/dev/null 2>&1 \
    || die "Docker Compose plugin not available. Install 'docker-compose-plugin' and re-run."
  c_ok "Prerequisites ready."
}

clone_repo() {
  if [ -d "$INSTALL_DIR/.git" ]; then
    c_info "Repo already present at $INSTALL_DIR; pulling latest…"
    git -C "$INSTALL_DIR" pull --ff-only
  else
    c_info "Cloning into $INSTALL_DIR…"
    git clone "$REPO_URL" "$INSTALL_DIR"
  fi
}

prompt_inputs() {
  # Reuse secrets from an existing .env so re-runs don't break the already
  # initialized Postgres volume (its password is fixed at first init) or
  # invalidate existing JWT sessions.
  local env_file="$INSTALL_DIR/.env"
  EXISTING_DB_PASSWORD=""
  EXISTING_SECRET_KEY=""
  if [ -f "$env_file" ]; then
    EXISTING_DB_PASSWORD="$(grep -E '^DB_PASSWORD=' "$env_file" | head -n1 | cut -d= -f2- || true)"
    EXISTING_SECRET_KEY="$(grep -E '^SECRET_KEY=' "$env_file" | head -n1 | cut -d= -f2- || true)"
    [ -n "$EXISTING_DB_PASSWORD" ] && c_info "Existing .env found — reusing the current database password unless you enter a new one."
  fi

  c_info "Configuration (input is not stored until written to a chmod 600 .env):"
  read -rp "  BOT_TOKEN: " BOT_TOKEN
  read -rp "  MAIN_ADMIN_ID (numeric Telegram id): " MAIN_ADMIN_ID
  read -rp "  WEB_DOMAIN (e.g. panel.example.com): " WEB_DOMAIN
  read -rp "  Web admin username: " WEB_ADMIN_USERNAME

  local pw1 pw2
  while :; do
    read -rsp "  Web admin password: " pw1; echo
    read -rsp "  Confirm password: " pw2; echo
    [ -n "$pw1" ] && [ "$pw1" = "$pw2" ] && break
    c_warn "Passwords empty or do not match; try again."
  done
  WEB_ADMIN_PASSWORD="$pw1"

  # The Postgres password is fixed when its data volume is first initialized
  # and cannot be changed by editing .env. So if a prior install exists, reuse
  # it unconditionally (no prompt) to guarantee app credentials match the
  # volume. Only ask on a genuinely fresh install.
  if [ -n "${EXISTING_DB_PASSWORD:-}" ]; then
    DB_PASSWORD="$EXISTING_DB_PASSWORD"
    c_info "  Reusing existing database password (change requires resetting the DB volume)."
  else
    read -rsp "  Database password (Enter to auto-generate): " DB_PASSWORD; echo
    [ -n "$DB_PASSWORD" ] || DB_PASSWORD="$(openssl rand -hex 16)"
  fi

  read -rp "  LOG_GROUP_ID (optional, Enter to skip): " LOG_GROUP_ID || true

  [ -n "$BOT_TOKEN" ] && [ -n "$MAIN_ADMIN_ID" ] && [ -n "$WEB_DOMAIN" ] \
    && [ -n "$WEB_ADMIN_USERNAME" ] || die "Required fields missing."
}

write_env() {
  local env_file="$INSTALL_DIR/.env"
  local secret_key db_url hash
  secret_key="${EXISTING_SECRET_KEY:-$(openssl rand -hex 48)}"
  db_url="postgresql+asyncpg://appstore:${DB_PASSWORD}@db:5432/appstore"

  # Write .env FIRST with a placeholder hash. The web service mounts .env via
  # env_file, and compose also reads .env for ${DB_PASSWORD} interpolation, so
  # it must exist before any `docker compose build/run` call below.
  c_info "Writing $env_file (chmod 600)…"
  umask 077
  cat > "$env_file" <<EOF
# Generated by install.sh — do not commit. Contains secrets.
BOT_TOKEN=${BOT_TOKEN}
MAIN_ADMIN_ID=${MAIN_ADMIN_ID}
LOG_GROUP_ID=${LOG_GROUP_ID}

WEB_DOMAIN=${WEB_DOMAIN}
WEB_ADMIN_USERNAME=${WEB_ADMIN_USERNAME}
WEB_ADMIN_PASSWORD_HASH=PENDING

DB_PASSWORD=${DB_PASSWORD}
DATABASE_URL=${db_url}

REDIS_URL=redis://redis:6379/0

SECRET_KEY=${secret_key}
EOF
  chmod 600 "$env_file"

  c_info "Building the web image (used to hash the admin password securely)…"
  ( cd "$INSTALL_DIR" && docker compose build web >/dev/null )

  c_info "Hashing admin password with bcrypt…"
  hash="$(cd "$INSTALL_DIR" && docker compose run --rm --no-deps \
    -e PW="$WEB_ADMIN_PASSWORD" web \
    python -c 'import os; from passlib.hash import bcrypt; print(bcrypt.hash(os.environ["PW"]))' \
    2>/dev/null | tr -d '\r' | tail -n 1)"
  [ -n "$hash" ] || die "Failed to hash admin password."

  # Patch the real hash into .env (preserves chmod 600).
  sed -i "s|^WEB_ADMIN_PASSWORD_HASH=.*|WEB_ADMIN_PASSWORD_HASH=${hash}|" "$env_file"

  # Clear plaintext password from shell memory.
  unset WEB_ADMIN_PASSWORD pw1 pw2 2>/dev/null || true
  c_ok ".env written."
}

start_stack() {
  c_info "Starting the stack…"
  ( cd "$INSTALL_DIR" && docker compose up -d --build db redis web bot )

  c_info "Waiting for the database to become healthy…"
  local tries=0
  until ( cd "$INSTALL_DIR" && docker compose exec -T db pg_isready -U appstore >/dev/null 2>&1 ); do
    tries=$((tries + 1)); [ "$tries" -gt 30 ] && die "Database did not become ready."
    sleep 2
  done

  c_info "Running database migrations…"
  if ! ( cd "$INSTALL_DIR" && docker compose run --rm web alembic upgrade head ); then
    c_err "Migrations failed."
    c_err "If this is 'password authentication failed for user \"appstore\"', the"
    c_err "Postgres data volume was initialized with a different password than the"
    c_err "current .env. With no real data yet (Phase 1) you can reset it safely:"
    c_err "    cd $INSTALL_DIR && docker compose down -v && bash install.sh"
    die "Aborting after migration failure."
  fi

  c_info "Creating the main admin user…"
  ( cd "$INSTALL_DIR" && docker compose run --rm web python -m scripts.create_admin )
  c_ok "Application services are up."
}

setup_nginx_ssl() {
  c_info "Configuring nginx for ${WEB_DOMAIN}…"
  mkdir -p "$INSTALL_DIR/nginx/conf.d" \
           "$INSTALL_DIR/certbot/www" \
           "$INSTALL_DIR/certbot/conf"

  # Phase 1 of nginx: HTTP-only so certbot can solve the ACME challenge.
  cat > "$INSTALL_DIR/nginx/conf.d/appstore.conf" <<EOF
server {
    listen 80;
    server_name ${WEB_DOMAIN};
    location /.well-known/acme-challenge/ { root /var/www/certbot; }
    location / { proxy_pass http://web:8000; proxy_set_header Host \$host; }
}
EOF

  ( cd "$INSTALL_DIR" && docker compose up -d nginx )

  c_info "Requesting an SSL certificate via certbot…"
  if ( cd "$INSTALL_DIR" && docker compose run --rm certbot certonly \
        --webroot -w /var/www/certbot \
        -d "$WEB_DOMAIN" --register-unsafely-without-email \
        --agree-tos --non-interactive ); then
    # Swap in the full TLS config from the template and reload.
    WEB_DOMAIN="$WEB_DOMAIN" envsubst '${WEB_DOMAIN}' \
      < "$INSTALL_DIR/docker/nginx.conf.template" \
      > "$INSTALL_DIR/nginx/conf.d/appstore.conf"
    ( cd "$INSTALL_DIR" && docker compose up -d certbot \
      && docker compose exec -T nginx nginx -s reload || docker compose restart nginx )
    c_ok "SSL configured."
  else
    c_warn "Certbot failed (check DNS/ports). Panel is reachable over HTTP for now."
  fi
}

install_cli() {
  ln -sf "$INSTALL_DIR/manage.sh" "/usr/local/bin/${APP_NAME}"
  chmod +x "$INSTALL_DIR/manage.sh"
  c_ok "CLI installed: run '${APP_NAME} status'."
}

print_summary() {
  echo
  c_ok "Installation complete."
  echo "  Panel URL : https://${WEB_DOMAIN}"
  echo "  Admin user: ${WEB_ADMIN_USERNAME}"
  echo "  Manage    : ${APP_NAME} {start|stop|restart|update|logs|backup|restore|admin-reset|status}"
  echo
  ( cd "$INSTALL_DIR" && docker compose ps )
}

main() {
  require_root
  require_ubuntu
  install_prereqs
  clone_repo
  prompt_inputs
  write_env
  start_stack
  setup_nginx_ssl
  install_cli
  print_summary
}

main "$@"
