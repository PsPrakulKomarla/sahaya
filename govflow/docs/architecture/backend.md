# Backend Architecture — Phase 0 Foundation

Status: Phase 0 (foundation only).

## Scope

Phase 0 establishes a clean, modular backend foundation:

- FastAPI application lifecycle (lifespan-managed DB + Redis).
- Pydantic v2 settings backed by an `.env` file.
- Async SQLAlchemy 2.0 engine + session dependency against PostgreSQL.
- Alembic migration pipeline.
- A typed Redis abstraction (`app/core/redis.py`) with JSON helpers and a
  dependency-injected singleton.
- Health endpoints mounted at both `/health` and `/api/v1/health`.
- Structured logging with structlog.
- pytest / Ruff / mypy configuration and CI-ready commands.

Explicitly **not** implemented in this phase: AI, browser automation, OCR,
government service adapters, application/grievance business logic. Those land
in later phases inside the corresponding `packages/` modules.

## Application layout

```
apps/api/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI app, CORS, router mounting, lifespan
│   ├── api/
│   │   ├── __init__.py
│   │   └── health.py     # /health, /health/live, /health/ready, /health/detailed
│   └── core/
│       ├── __init__.py   # public exports (settings, database, redis, logging)
│       ├── config.py     # pydantic-settings
│       ├── database.py   # async engine, session maker, Base, get_db
│       ├── redis.py      # RedisClient abstraction + get_redis + close_redis
│       ├── logging.py    # structlog + stdlib bootstrap
│       └── security.py   # password hashing + JWT helpers (foundation only)
├── alembic/               # migration environment + revisions
├── tests/
├── pyproject.toml
└── Makefile
```

Packages (monorepo):

```
packages/
├── shared/        # shared/typed schemas
├── services/      # service adapter interfaces + registry (existing)
├── applications/  # TODO later phase (placeholder)
├── grievances/    # TODO later phase (placeholder)
├── audit/         # TODO later phase (placeholder)
├── agent/         # TODO later phase (placeholder)
├── browser/       # TODO later phase (placeholder)
├── documents/     # TODO later phase (placeholder)
├── ai/            # TODO later phase (placeholder)
├── i18n/          # TODO later phase (placeholder)
## Configuration

Settings live in `app/core/config.py` (pydantic-settings, `case_sensitive=True`,
`extra="ignore"`) and are read from `.env` (see `.env.example` at the repo
root). Notable variables:

| Variable                     | Default                                                        | Purpose                |
|------------------------------|----------------------------------------------------------------|------------------------|
| `APP_NAME` / `APP_VERSION`   | GovFlow AI / 0.1.0                                             | Service identity       |
| `ENVIRONMENT` / `DEBUG`      | development / true                                             | Runtime profile        |
| `API_V1_PREFIX`              | /api/v1                                                        | Versioned route prefix |
| `HOST` / `PORT`              | 0.0.0.0 / 8000                                                 | Binding                |
| `DATABASE_URL`               | postgresql+asyncpg://postgres:postgres@localhost:5432/govflow  | SQLAlchemy async URL   |
| `DATABASE_POOL_SIZE`         | 10                                                             | Engine pool size       |
| `DATABASE_MAX_OVERFLOW`      | 20                                                             | Engine pool overflow   |
| `REDIS_URL`                  | redis://localhost:6379/0                                       | Redis connection       |
| `SECRET_KEY`, `ALGORITHM`    | dev default, HS256                                             | JWT (security layer)   |
| `CORS_ORIGINS`               | ["http://localhost:3000"]                                      | CORS allowlist         |
| `LOG_LEVEL` / `LOG_FORMAT`   | INFO / json                                                    | Logging                |

Sensitive variables (`SECRET_KEY`, API keys) must be overridden in real
environments — never commit `.env`.

## Database & migrations

- `app/core/database.py` builds an async engine / session maker from
  `DATABASE_URL`.
- `Base(DeclarativeBase)` is the single metadata source for Alembic.
- `alembic/env.py` derives its URL from settings so `.env` configuration
  applies to both offline (`--sql`) and online runs.
- Revision `001_initial` creates the `users`, `services`, `documents`,
  `applications`, `grievances`, and `agent_runs` tables.
- The FastAPI lifespan calls `init_db()` (a dev convenience using
  `metadata.create_all`) but tolerates failure so the API can still report
  health when PostgreSQL is down; Alembic is the schema source of truth.

## Health checks

| Endpoint           | Probes                  | Result                                   |
|--------------------|-------------------------|------------------------------------------|
| `/health`          | none (process)          | 200 + service metadata                   |
| `/health/live`     | none                    | 200 `{"status":"alive"}`                 |
| `/health/ready`    | DB `SELECT 1`, Redis ping | 200 `{"status":"ready"|"not_ready"}` |
| `/health/detailed` | DB + Redis + latency    | per-dependency; overall healthy/degraded/unhealthy |

All routes are mounted at the root and under `API_V1_PREFIX`.

## Dependency injection

- `get_db` — FastAPI dependency yielding an `AsyncSession`.
- `get_redis` — FastAPI dependency returning the shared `RedisClient`.
- Both are overridable in tests via `app.dependency_overrides`.

## Quality gates (CI-ready)

```bash
make -C apps/api install          # Python 3.12 venv + ".[dev]"
make -C apps/api lint             # ruff check
make -C apps/api format-check     # ruff format --check
make -C apps/api typecheck        # mypy app
make -C apps/api test             # pytest
make -C apps/api offline-migrate  # alembic upgrade head --sql
make -C apps/api migrate          # alembic upgrade head (needs PostgreSQL)
```

`apps/api/package.json` exposes equivalent npm scripts (`dev`, `test`, `lint`,
`typecheck`, `db:migrate`) that are wired into the root npm workspaces, and
`.github/workflows/backend-ci.yml` runs the quality gates on every push/PR.

Phase-0 gates cover the foundation modules owned by this phase
(`app/core`, `app/main.py`, `app/api/health.py`, `tests`, `alembic`).
Feature modules under active development by parallel tracks
(`app/models`, `app/schemas`, `app/api/services.py`, `app/repositories`,
`app/services`) are validated by their owning tracks.

## Known limitations (Phase 0)

- `001_initial.py` is a hand-written baseline migration; autogenerate will be
  used once ORM models exist in later phases.
- Redis pool-size tuning is not exposed yet; the client abstraction and its
  JSON helpers are in place.
- No request middleware (request IDs / audit) yet — reserved for the security
  phase.