# CLAUDE.md

Reference document for the project. Read this first in every phase.

## Project goal

A multi-product **Telegram sales bot** (selling **Apple IDs** and **VPN**
accounts) with a **web admin panel**. Customers buy products through the
Telegram bot using a wallet balance; admins manage products, inventory,
orders, payments and users through both the bot (admin handlers) and a
FastAPI web panel.

This repository is developed in **phases**. See `PLAN.md` for the full
roadmap and the exact scope of the current phase.

> **Phase 1 = infrastructure & skeleton only.** No sales / payment / x-ui
> business logic is implemented yet. Do not add it until the relevant phase.

## Stack

- Python 3.11+
- Bot: **aiogram 3.x** (async)
- Web panel: **FastAPI** + **HTMX** + **Jinja2**
- Database: **PostgreSQL** + **SQLAlchemy 2.0** (async) + **Alembic**
- **Redis** (FSM storage, distributed locks, throttling)
- `httpx`, `APScheduler`, `pydantic-settings`, `passlib[bcrypt]`,
  `python-jose` (JWT)
- Deployment: **Docker Compose** (`db`, `redis`, `bot`, `web`, `nginx`) +
  `certbot` for SSL.

## Architecture rules (enforced strictly)

1. **Layered architecture:**
   `handlers/routers → services → repositories → models`.
2. **Business logic must NEVER live inside a handler or router.** Handlers
   parse input and render output; all decisions live in **services**.
3. `models`, `services`, and `repositories` live in the **`shared/`**
   package and are shared between the bot and the web panel. **Never
   duplicate logic** between bot and web.
4. **Code identifiers and comments are in English.** All **user-facing
   display text is in Persian**, written so it can later move into a locale
   system.
5. **Wallet balance is never mutated directly on the user row.** Every
   balance change goes through the **`transactions` ledger** and records a
   `balance_after`. The user's `balance` is a cached projection of the
   ledger and is only written by the wallet service in the same DB
   transaction that inserts the ledger row.
6. `.gitignore` must include `.env`. **Never commit secrets.**

## Folder structure

```
project/
├── bot/
│   ├── core/            # bot/dispatcher bootstrap, logging
│   ├── handlers/
│   │   ├── user/        # end-user handlers (Phase 1: /start only)
│   │   └── admin/       # admin handlers (later phases)
│   ├── keyboards/       # inline/reply keyboard builders
│   ├── states/          # aiogram FSM state groups
│   ├── middlewares/     # auth / throttling stubs (Phase 1)
│   └── main.py          # bot entrypoint
├── web/
│   ├── main.py          # FastAPI app
│   ├── auth.py          # bcrypt + JWT/session auth
│   ├── routers/         # FastAPI routers
│   ├── templates/       # Jinja2 templates
│   └── static/          # CSS/JS assets
├── shared/
│   ├── config.py        # pydantic-settings Settings
│   ├── database.py      # async engine + session factory
│   ├── redis.py         # async redis client
│   ├── models/          # SQLAlchemy ORM models (full schema)
│   ├── repositories/    # data-access layer
│   └── services/        # business logic layer
├── integrations/
│   ├── xui/             # x-ui panel client (interface only in Phase 1)
│   └── gateways/        # payment gateways (interface only in Phase 1)
├── migrations/          # Alembic environment + versions
├── docker/              # Dockerfile.bot, Dockerfile.web, nginx template
├── docker-compose.yml
├── .env.example
├── install.sh
├── update.sh
├── manage.sh
├── VERSION
└── README.md
```

## Conventions

- **Layers:** a handler/router calls a **service**; a service calls one or
  more **repositories**; a repository is the only place that builds SQL /
  touches the ORM session for its aggregate.
- **Sessions:** async `AsyncSession` from `shared.database.get_session()`.
  Repositories receive a session; they do not create their own.
- **Money:** stored as `Numeric(18, 0)` representing **Toman** (integer
  amounts, no decimals). Never use floats for money.
- **Enums:** status/type columns use Python `enum.Enum` subclasses defined
  next to their model and stored as strings.
- **Timestamps:** every table has `created_at`; mutable tables also have
  `updated_at`. Both are timezone-aware (`TIMESTAMP WITH TIME ZONE`) and
  default to `now()`.
- **Naming:** tables are singular snake_case (`user`, `apple_id_stock`).
  Foreign keys are `<table>_id`.
- **User-facing text:** Persian string literals grouped where possible so
  they can be extracted into a locale file later.
- **Settings:** runtime-tunable values (card number, etc.) live in the
  `setting` table, not in code.
- **Secrets:** only ever come from environment / `.env`. `.env.example`
  documents every key; `.env` is git-ignored.

## Phase boundaries (what NOT to do now)

In Phase 1 do **not** implement: shop/wallet/payment/receipt handlers, real
`integrations/xui` or `gateways` logic, real web CRUD, or scheduler jobs.
Leave typed interfaces / stubs so later phases can fill them in without
restructuring.
