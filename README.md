# GovFlow AI

GovFlow is a full-stack government service automation platform that combines a FastAPI backend, a Next.js frontend, and a set of reusable domain packages for workflow orchestration, browser automation, grievance handling, and AI-assisted service resolution.

## Overview

This repository contains the application code for a multi-service government workflow platform. The goal is to help citizens navigate public-service tasks through an AI-assisted interface with structured workflows, safety checks, and human approval steps.

## Repository structure

```bash
.
├── apps/
│   ├── api/          # FastAPI backend
│   └── web/          # Next.js frontend
├── packages/
│   ├── agent/        # orchestration and planning logic
│   ├── ai/           # AI client/provider abstractions
│   ├── applications/ # application lifecycle logic
│   ├── audit/        # audit and traceability
│   ├── browser/      # browser automation support
│   ├── grievances/   # grievance handling
│   ├── services/     # service registry and workflow services
│   └── shared/       # shared frontend/backend utilities
├── infra/
│   └── docker/       # local infrastructure config
├── govflow/          # nested legacy project directory
├── package.json      # root workspace scripts
├── .env.example      # example environment file
├── README.md         # project documentation
└── LICENSE           # if present in your repo
```

## Tech stack

- Frontend: Next.js, React, TypeScript, Tailwind CSS
- Backend: FastAPI, Python 3.11+
- Data/API validation: Pydantic
- Browser automation: Playwright and browser wrappers
- Package management: npm workspaces
- Local infrastructure: Docker Compose

## Prerequisites

- Node.js 20+
- Python 3.11+
- npm
- Docker (for local infrastructure)

## Quick start

### 1) Install dependencies

```bash
cd "C:\Users\prakul\Desktop\projects\sahaya"
npm install
cd apps/web
npm install
cd ..\api
pip install -e ".[dev]"
```

### 2) Configure environment variables

```bash
cp .env.example .env
```

Then update the values in `.env` to match your local setup, such as API base URLs, secrets, and service configuration.

### 3) Start local infrastructure

```bash
cd ../../infra/docker
docker compose up -d
```

### 4) Run the app

From the repository root:

```bash
npm run dev
```

This starts the web frontend and API together according to the root workspace scripts.

## Useful scripts

```bash
npm run dev
npm run dev:web
npm run dev:api
npm run build
npm run test
npm run lint
npm run db:migrate
```

## Development notes

- The root workspace is the canonical entry point for running the project.
- Subdirectories under `govflow/` appear to be duplicate or legacy copies and are not meant to be the primary source of documentation.
- Keep environment variables in `.env` and avoid committing secrets.

## Contributing

1. Create a focused change.
2. Run the relevant tests or checks.
3. Keep documentation up to date.
4. Avoid leaving duplicate project docs in nested folders.

## License

Check the repository license file if one is present in your project. If no license file exists, add one before publishing the project externally.