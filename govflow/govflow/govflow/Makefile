# GovFlow AI - repository level developer & CI commands.
#
# Backend targets are delegated to apps/api/Makefile; frontend targets use
# the npm workspaces already defined in package.json.

.DEFAULT_GOAL := help

.PHONY: help api-install api-test api-lint api-format api-format-check api-typecheck api-migrate api-dev

help:
	@echo "GovFlow AI commands:"
	@echo "  api-install      Create the Python 3.12 venv and install the API with dev extras"
	@echo "  api-test         Run the backend pytest suite (apps/api)"
	@echo "  api-lint         Run ruff check on the backend (apps/api)"
	@echo "  api-format       Format the backend with ruff (apps/api)"
	@echo "  api-format-check Verify backend formatting (apps/api)"
	@echo "  api-typecheck    Run mypy on the backend (apps/api)"
	@echo "  api-migrate      Apply alembic migrations against the configured database"
	@echo "  api-dev          Start the FastAPI dev server (apps/api)"

api-install:
	$(MAKE) -C apps/api install

api-test:
	$(MAKE) -C apps/api test

api-lint:
	$(MAKE) -C apps/api lint

api-format:
	$(MAKE) -C apps/api format

api-format-check:
	$(MAKE) -C apps/api format-check

api-typecheck:
	$(MAKE) -C apps/api typecheck

api-migrate:
	$(MAKE) -C apps/api migrate

api-dev:
	$(MAKE) -C apps/api dev