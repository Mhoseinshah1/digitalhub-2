# PLAN.md

Project roadmap for the multi-product Telegram sales bot (Apple ID + VPN)
with a web admin panel.

## Phases

### Phase 1 — Infrastructure & skeleton (current)

Goal: a project that **boots cleanly** end-to-end with the full database
schema in place, but **no sales/payment/x-ui business logic**.

Included in Phase 1:

1. Full folder structure + dependency manifest (`requirements.txt` /
   `pyproject.toml`).
2. `shared/config.py` (pydantic-settings) reading every key from `.env`.
   No hardcoded secrets.
3. `.env.example` documenting every key.
4. `shared/models/` — the **complete** database schema (all tables and
   relationships listed below), so future phases avoid costly migrations.
5. `shared/database.py` (async engine + session) and `shared/redis.py`.
6. Alembic configured + **one initial migration** creating the whole schema.
7. `bot/main.py` + `bot/core/`: the bot boots and answers **only `/start`**
   with a Persian welcome. Empty auth/throttling middleware stubs.
8. `web/main.py`: FastAPI login page (admin user/pass from `.env`, verified
   with bcrypt, JWT session) + an empty protected dashboard. No real CRUD.
9. `docker-compose.yml` + `Dockerfile.bot` + `Dockerfile.web` +
   `nginx.conf.template` (reverse proxy on `WEB_DOMAIN`). Bot and web share
   one image/codebase.
10. `install.sh` (interactive provisioning on Ubuntu).
11. `update.sh` (safe self-update with DB backup + rollback).
12. `manage.sh` (symlinked to `/usr/local/bin/appstore`).
13. `README.md` with the one-line install + update commands.

The complete schema defined now (tables): `user`, `product`, `plan`,
`server`, `apple_id_stock`, `order`, `transaction`, `payment`,
`vpn_account`, `discount`, `ticket`, `setting`.

**Explicitly NOT in Phase 1** (reserved for later phases):

- shop / wallet / payment / receipt-approval handlers,
- real implementation of `integrations/xui` and `gateways`
  (only empty interfaces/contracts now),
- real web panel CRUD,
- scheduler jobs.

### Phase 2 — Wallet & payments

- Wallet service backed by the `transactions` ledger (credit/debit with
  `balance_after`).
- Card-to-card + Zarinpal gateway implementations behind the Phase 1
  `gateways` interface.
- Receipt upload + admin approval flow (`payment`, `order` states).

### Phase 3 — Shop & ordering (Apple ID)

- Product/plan browsing handlers.
- Apple ID stock allocation and delivery on order approval.
- Order lifecycle: `pending → waiting_receipt → approved → delivered`.

### Phase 4 — VPN & x-ui integration

- Real `integrations/xui` client (multi-server) behind the Phase 1
  interface.
- VPN account provisioning (`vpn_account`: sub link, uuid, expiry, traffic).
- Plan-driven creation on x-ui inbounds.

### Phase 5 — Web admin CRUD

- Full CRUD for products, plans, servers, stock, orders, users, settings.
- Dashboards, reporting, manual wallet adjustments (via ledger).

### Phase 6 — Automation & polish

- APScheduler jobs (expiry reminders, traffic sync, stock alerts).
- Tickets/support, discounts, locale extraction, hardening.

## Current phase

**Phase 1.** When working in this repository, only build/modify what is
listed under Phase 1 above unless the active task explicitly advances a
later phase.
