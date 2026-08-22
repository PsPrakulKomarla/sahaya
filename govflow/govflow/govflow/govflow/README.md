# GovFlow AI

Universal Government Service Browser Agent - An AI-powered browser agent that helps citizens interact with government services through real government websites.

## Architecture

```
govflow/
├── apps/
│   ├── web/                 # Next.js 14 Frontend
│   └── api/                 # FastAPI Backend
├── packages/
│   ├── shared/              # Shared TypeScript types (Zod schemas)
│   ├── agent/               # AI Agent core (planner, executor, recovery, memory, safety)
│   ├── browser/             # Browser automation abstraction (webcmd, playwright)
│   ├── services/            # Service registry and adapters
│   ├── documents/           # OCR, validation, extraction
│   ├── ai/                  # AI providers, prompts, structured output
│   ├── i18n/                # Multilingual support (en, kn, hi)
│   ├── security/            # Security utilities
│   └── shared/              # Shared utilities
├── workers/
│   ├── agent_worker/        # Background agent tasks
│   └── status_worker/       # Application status polling
├── infra/
│   ├── docker/              # Docker Compose for local dev
│   └── database/            # Database migrations
└── docs/                    # Documentation
```

## Quick Start

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

## Development

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

### Project Structure Details

#### Frontend (Next.js 14)

- **App Router** with TypeScript
- **Tailwind CSS** + shadcn/ui components
- **React 18** with Server Components
- **Vitest** + Testing Library for tests

#### Backend (FastAPI)

- **Async SQLAlchemy 2.0** with PostgreSQL
- **Alembic** for migrations
- **Pydantic v2** for validation
- **JWT** authentication
- **Structured logging** with structlog
- **pytest** for testing

#### Shared Types

- **Zod schemas** for runtime validation
- **TypeScript types** inferred from Zod
- Used by both frontend and backend

## Core Features

1. **Service Discovery** - AI identifies government services from natural language
2. **Pre-Application Assistant** - Explains requirements, eligibility, documents
3. **Document Intelligence** - OCR for Aadhaar, PAN, Passport, etc.
4. **Browser Agent** - Real browser automation via webcmd + Playwright
5. **Self-Learning Workflows** - Learns from successful executions
6. **Recovery Engine** - Handles website changes gracefully
7. **Human-in-the-Loop** - Mandatory approval for sensitive actions
8. **Multilingual** - English, Kannada, Hindi
9. **Application Tracking** - Unified dashboard
10. **Grievance System** - Raise complaints for delayed services

## Security

- All citizen data treated as sensitive
- No hardcoded secrets
- Encryption at rest for sensitive data
- Prompt injection defense
- Audit logging with redaction
- HTTPS in production

## License

MIT