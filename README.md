# GovFlow AI

**Universal Government Service Browser Agent** — An AI-powered browser agent that helps citizens interact with government services through real government websites. Built for the **SLAB Hackathon** with production-grade security, reliability, and observability.

## 🏗️ Architecture

```
govflow/
├── apps/
│   ├── web/                 # Next.js 14 Frontend (Dashboard + Demo UI)
│   └── api/                 # FastAPI Backend (REST API + Agent Orchestration)
├── packages/
│   ├── shared/              # Shared TypeScript types (Zod schemas)
│   ├── agent/               # AI Agent core (planner, executor, recovery, memory, safety, audit)
│   ├── browser/             # Browser automation abstraction (webcmd, playwright, secure wrapper)
│   ├── services/            # Service registry, adapters, intent engine, resolver
│   ├── documents/           # OCR, validation, extraction, storage
│   ├── grievances/          # Grievance composition, tracking, status
│   ├── applications/        # Application lifecycle, preparation, tracking
│   └── audit/               # Audit logging service
├── infra/
│   ├── docker/              # Docker Compose for local dev
│   └── database/            # Database migrations (Alembic)
└── docs/                    # Documentation
```

## 🚀 Quick Start

### Prerequisites

- Node.js 20+
- Python 3.11+
- PostgreSQL 16+
- Redis 7+
- Docker (optional, for local services)

### Installation

```bash
# Clone and enter directory
cd govflow

# Install frontend dependencies
cd apps/web && npm install

# Install backend dependencies
cd ../api && pip install -e ".[dev]"

# Start infrastructure (PostgreSQL, Redis, MinIO)
cd ../../infra/docker && docker-compose up -d

# Run database migrations
cd ../api && alembic upgrade head

# Start development servers
cd ../..
npm run dev
```

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
# Edit .env with your settings
```

**Critical security settings (must be set in production):**
```env
SECRET_KEY=your-256-bit-secret-key  # Required in production
ALLOWED_DOMAINS=service.karnataka.gov.in,seva.sindh.gov.in  # Domain allowlist
ENVIRONMENT=production
DEBUG=false
```

## 🛠️ Development

### Available Scripts

```bash
# From root
npm run dev           # Start both frontend and backend
npm run dev:web       # Start frontend only
npm run dev:api       # Start backend only
npm run build         # Build all packages
npm run test          # Run all tests
npm run lint          # Lint all packages
npm run db:generate   # Generate database migration
npm run db:push       # Push schema changes
npm run db:migrate    # Run migrations
npm run db:studio     # Open Prisma Studio
```

### Running Tests

```bash
# Backend tests
cd apps/api
python -m pytest tests/ -v
python -m pytest tests/test_security.py -v  # Security tests
python -m pytest tests/test_health.py -v    # Health check tests

# Frontend tests
cd ../web
npm run test
```

## 🔐 Phase 14 — Security & Reliability Hardening

### Authentication & Authorization
- **JWT-based authentication** with access/refresh tokens
- **Role-based access control** (citizen, admin, support)
- **Resource ownership verification** on all user endpoints
- **Password hashing** with bcrypt (no plaintext storage)

### API Security
- **Rate limiting** (Redis-backed sliding window, 100 req/min default)
- **Input validation** via Pydantic v2 schemas on all endpoints
- **Structured error responses** — no stack traces or internal details leaked
- **Correlation IDs** (X-Request-ID) on all requests/responses
- **Global exception handlers** for validation, HTTP, and unexpected errors

### URL & Browser Security
- **Domain allowlist** — only configured government domains accessible
- **SSRF protection** — blocks localhost, private IPs, cloud metadata endpoints
- **Scheme enforcement** — HTTPS only in production
- **Port blocking** — common internal service ports blocked
- **Redirect validation** — max 5 redirects, cross-domain redirect detection
- **Secure browser wrapper** — all navigation validated before execution

### Audit & Observability
- **Structured audit logging** with automatic PII redaction
- **Comprehensive health checks**: `/health`, `/health/live`, `/health/ready`, `/health/detailed`, `/health/browser`, `/health/ai`, `/health/storage`
- **Prometheus-compatible metrics** via structured logging
- **Security event tracking** (rate limit exceeded, URL blocked, SSRF attempts)

### Security Tests
```bash
python -m pytest tests/test_security.py -v
```
Covers: authentication, authorization, rate limiting, URL validation, SSRF protection, input validation, CORS, security headers, error handling, cross-user access prevention, audit logging, prompt injection defense.

## 🎭 Phase 15 — Hackathon Demo System

### Demo Dashboard (`/demo`)

The demo dashboard provides a complete, interactive demonstration of GovFlow's capabilities:

| Section | Features |
|---------|----------|
| **Ask GovFlow** | Natural language interface — "I want to apply for an income certificate" |
| **Agent Activity Stream** | Live step-by-step visualization of agent reasoning |
| **Workflow Visualization** | NEW vs LEARNED workflow states, promotion pipeline |
| **Live Browser View** | Real browser session with URL bar, security indicators, screenshots |
| **Recovery Visualization** | Shows website change detection, semantic recovery, workflow update |
| **Approval UI** | Human-in-the-loop review before sensitive actions |
| **Document UI** | Required docs checklist, OCR processing, field extraction, verification |
| **Application UI** | Status, reference number, timeline, next actions |
| **Grievance UI** | Raise grievances for delayed applications with tracking |
| **Multilingual Support** | English, ಕನ್ನಡ, हिन्दी (UI + intent parsing) |
| **Metrics Panel** | Real-time: workflows learned, reuse rate, recovery success, task duration |
| **Architecture View** | Technical depth diagram for judges |

### Demo Scenarios

1. **First Run** — Complete end-to-end: understanding → service resolution → documents → browser exploration → workflow learning → human approval → submission
2. **Second Run (Reuse)** — "Learned workflow found" → direct reuse, no re-exploration
3. **Recovery Demo** — Simulated website change ("Start Application" → "Begin New Application") → semantic recovery → workflow update
4. **Grievance Demo** — Delayed application → grievance composition → approval → submission → tracking

### Demo Controls
- **Demo Mode** — Uses safe test data, clearly marked mock operations
- **Demo Reset** — `POST /api/v1/demo/reset` — resets only demo resources
- **Demo Seed Data** — Synthetic user, documents, workflows, applications
- **Controlled Failures** — Toggle website changes, portal unavailability

## 🌐 Multilingual Support

- **Languages**: English, Kannada (ಕನ್ನಡ), Hindi (हिन्दी)
- **UI switching** with persistent preference
- **Intent parsing** in all three languages
- **Document OCR** supports all three languages
- **Government form labels** localized

## 📊 Core Features

| Feature | Description |
|---------|-------------|
| **Service Discovery** | AI identifies government services from natural language queries |
| **Pre-Application Assistant** | Explains requirements, eligibility, required documents |
| **Document Intelligence** | OCR for Aadhaar, PAN, Passport, income proof, address proof |
| **Browser Agent** | Real browser automation via webcmd + Playwright with security wrapper |
| **Self-Learning Workflows** | Learns from successful executions, promotes through DRAFT→LEARNING→VALIDATED→ACTIVE |
| **Recovery Engine** | Handles website changes via semantic matching (element role + text similarity) |
| **Human-in-the-Loop** | Mandatory approval for SUBMIT, PAYMENT, UPDATE_RECORD, etc. |
| **Application Tracking** | Unified dashboard with timeline, status normalization |
| **Grievance System** | Raise complaints for delayed services with tracking |
| **Multilingual** | English, Kannada, Hindi throughout the stack |

## 🧪 Testing Strategy

### Test Coverage
- **Unit tests**: Domain models, schemas, configuration, security utilities
- **Integration tests**: Health checks, database, Redis, workflow memory
- **Security tests**: Authentication, authorization, SSRF, rate limiting, input validation
- **Agent tests**: Planner, executor, state machine, safety engine, recovery
- **E2E tests**: Complete workflows, browser automation, learning/reuse/recovery

### Running Full Test Suite
```bash
# Backend (excludes broken browser tests)
cd apps/api
python -m pytest tests/test_config.py tests/test_health.py tests/test_schemas.py \
  tests/test_domain_models.py tests/test_redis.py tests/test_workflow_memory.py \
  tests/test_security.py -v

# Frontend
cd ../web
npm run test
```

## 🔧 Configuration

### Key Settings (`apps/api/app/core/config.py`)

| Setting | Description | Default |
|---------|-------------|---------|
| `SECRET_KEY` | JWT signing key (REQUIRED in prod) | Auto-generated in dev |
| `ALLOWED_DOMAINS` | Domain allowlist for browser | [] (dev allows all) |
| `BLOCKED_DOMAINS` | Explicitly blocked domains | [] |
| `BROWSER_ALLOW_PRIVATE_IPS` | Allow private IP navigation | false |
| `BROWSER_MAX_REDIRECTS` | Max redirects before blocking | 5 |
| `RATE_LIMIT_ENABLED` | Enable rate limiting | true |
| `RATE_LIMIT_REQUESTS` | Requests per window | 100 |
| `RATE_LIMIT_WINDOW_SECONDS` | Rate limit window | 60 |
| `CORS_ORIGINS` | Allowed CORS origins | ["http://localhost:3000"] |

## 🏥 Health Check Endpoints

| Endpoint | Purpose |
|----------|---------|
| `GET /health` | Basic liveness |
| `GET /health/live` | Kubernetes liveness probe |
| `GET /health/ready` | Kubernetes readiness probe (DB + Redis) |
| `GET /health/detailed` | Full dependency status with latency |
| `GET /health/browser` | Playwright/Chromium availability |
| `GET /health/ai` | AI provider configuration |
| `GET /health/storage` | S3/MinIO configuration |

## 📈 Metrics (via Structured Logs)

All metrics emitted as structured JSON logs:
- `task_success_rate`, `task_failure_rate`
- `browser_success_rate`, `workflow_reuse_rate`
- `workflow_recovery_rate`, `recovery_success_rate`
- `ocr_success_rate`, `application_preparation_success`
- `submission_success`, `tracking_success`
- `average_task_duration_ms`

## 🛡️ Security Checklist (Pre-Demo)

- [ ] `SECRET_KEY` set via environment variable
- [ ] `ALLOWED_DOMAINS` configured with target government portals
- [ ] `ENVIRONMENT=production` and `DEBUG=false`
- [ ] No real user data in demo database
- [ ] Demo documents are synthetic
- [ ] Approval cannot be bypassed
- [ ] Domain allowlist enforced in browser wrapper
- [ ] Sensitive logs redacted (passwords, tokens, IDs)
- [ ] Prompt injection handled in intent engine
- [ ] Cross-user access blocked on all endpoints
- [ ] Duplicate submission prevented via idempotency keys

## 🚢 Deployment

### Docker (Recommended)
```bash
cd infra/docker
docker-compose -f docker-compose.prod.yml up -d
```

### Manual
```bash
# Backend
cd apps/api
pip install -e ".[prod]"
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Frontend
cd ../web
npm run build
npm start
```

## 📚 Documentation

- `docs/architecture.md` — System architecture diagrams
- `docs/security.md` — Security model and threat analysis
- `docs/api.md` — REST API reference
- `docs/demo-script.md` — 5-7 minute hackathon demo script
- `docs/agent.md` — Agent internals (planner, executor, memory, recovery)

## 🏆 Hackathon Judging Alignment

| Criterion (Weight) | Demo Demonstration |
|---|---|
| **Live Reliability (30%)** | Actual browser execution, real government portal, safe failure handling |
| **Real-World Usefulness (25%)** | Income certificate end-to-end, grievance for delays, multilingual |
| **Technical Depth (20%)** | Workflow memory + recovery + OCR + safety + browser abstraction |
| **Creativity (15%)** | Universal government-service agent, learn-once-reuse-many |
| **Demo/Storytelling (10%)** | Clear before/after: Manual process → GovFlow |

## 📝 License

MIT