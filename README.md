# AppStore Bot

A multi-product **Telegram sales bot** (Apple ID + VPN) with a **FastAPI web
admin panel**. This repository is built in phases — see
[`PLAN.md`](PLAN.md). **Phase 1 is infrastructure & skeleton only**: the bot
boots and answers `/start`, the web panel has a login + empty dashboard, and
the complete database schema is in place. No sales/payment/x-ui logic yet.

For architecture rules and conventions, read [`CLAUDE.md`](CLAUDE.md).

## Stack

Python 3.11+ · aiogram 3 · FastAPI + HTMX + Jinja2 · PostgreSQL + SQLAlchemy 2
(async) + Alembic · Redis · Docker Compose + nginx + certbot.

## One-line install (Ubuntu server)

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/Mhoseinshah1/digitalhub-2/main/install.sh)
```

The installer checks prerequisites, installs Docker/Compose/Git if needed,
clones into `/opt/appstore-bot`, prompts for configuration (bot token, admin
id, domain, web admin credentials, DB password, optional log group), writes a
`chmod 600` `.env` (secrets are never printed), builds the stack, runs
migrations, creates the main admin, and provisions nginx + SSL.

## Update

```bash
appstore update
```

`update.sh` backs up the database first, pulls the latest code, rebuilds,
runs migrations, and rolls back the database automatically on error. It never
touches `.env` or the database volume.

## Management CLI

After install, `manage.sh` is symlinked to `/usr/local/bin/appstore`:

```bash
appstore start | stop | restart | update | logs | backup | restore | admin-reset | status
```

## Project layout

```
bot/          aiogram bot (handlers, keyboards, states, middlewares, main.py)
web/          FastAPI panel (auth, routers, templates, static)
shared/       config, database, redis, models, repositories, services
integrations/ xui + payment gateway interfaces (contracts only in Phase 1)
migrations/   Alembic environment + versions
docker/       Dockerfiles + nginx template
```

## Local development without Docker (SQLite)

You can run both apps against a local SQLite database — no Postgres/Redis/Docker
required for a smoke test.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Minimal .env for local testing (SQLite + dummy values):
cat > .env <<'EOF'
BOT_TOKEN=123:dummy
MAIN_ADMIN_ID=1
WEB_DOMAIN=localhost
WEB_ADMIN_USERNAME=admin
WEB_ADMIN_PASSWORD_HASH=$(python -c "from passlib.hash import bcrypt; print(bcrypt.hash('admin'))")
DB_PASSWORD=local
DATABASE_URL=sqlite+aiosqlite:///./local.db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=local-dev-secret
EOF

# Create the schema:
alembic upgrade head

# Run the web panel (login: admin / admin):
uvicorn web.main:app --reload
# open http://127.0.0.1:8000/login
```

> The bot itself needs a real `BOT_TOKEN` and a reachable Redis to poll
> Telegram; the web panel and the database schema can be exercised entirely
> offline with SQLite as shown above.

## Phases

See [`PLAN.md`](PLAN.md). Current: **Phase 1**.
