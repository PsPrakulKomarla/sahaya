# GovFlow AI - Backend (apps/api) developer & CI commands.
#
# Usage: make <target>   (e.g. `make install`, `make test`)
# Python 3.12+ is required. CI sets PYTHON to the 3.12 interpreter.
#
# Phase-0 quality gates cover the foundation modules; feature modules being
# developed in parallel tracks (app/models, app/schemas, app/api/services.py,
# app/repositories, app/services) are linted/typed by their owning track.

PYTHON ?= python

# Files owned and validated by the Phase-0 backend foundation.
FOUNDATION := app/core app/main.py app/api/health.py tests alembic

ifeq ($(OS),Windows_NT)
VENV_PY := venv/Scripts/python.exe
VENV_CREATE := py -3.12 -m venv venv || $(PYTHON) -m venv venv
else
VENV_PY := venv/bin/python
VENV_CREATE := $(PYTHON) -m venv venv
endif

.PHONY: venv install dev start test lint format format-check typecheck migrate revision downgrade offline-migrate clean

venv:
	$(VENV_CREATE)

install: venv
	$(VENV_PY) -m pip install --upgrade pip
	$(VENV_PY) -m pip install -e ".[dev]"

dev:
	$(VENV_PY) -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

start:
	$(VENV_PY) -m uvicorn app.main:app --host 0.0.0.0 --port 8000

test:
	$(VENV_PY) -m pytest

lint:
	$(VENV_PY) -m ruff check $(FOUNDATION)

format:
	$(VENV_PY) -m ruff format $(FOUNDATION)

format-check:
	$(VENV_PY) -m ruff format --check $(FOUNDATION)

typecheck:
	$(VENV_PY) -m mypy $(FOUNDATION)

migrate:
	$(VENV_PY) -m alembic upgrade head

revision:
	$(VENV_PY) -m alembic revision --autogenerate -m "$(m)"

downgrade:
	$(VENV_PY) -m alembic downgrade -1

# Validate migrations without a live database (writes SQL to stdout).
offline-migrate:
	$(VENV_PY) -m alembic upgrade head --sql

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage
	rm -rf venv