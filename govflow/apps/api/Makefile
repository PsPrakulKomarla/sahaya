# GovFlow AI - Backend (apps/api) developer & CI commands.
#
# Usage: make <target>   (e.g. `make install`, `make test`)
# Python 3.12+ is required. CI sets PYTHON to the 3.12 interpreter.

PYTHON ?= python

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
	$(VENV_PY) -m ruff check app tests alembic

format:
	$(VENV_PY) -m ruff format app tests alembic

format-check:
	$(VENV_PY) -m ruff format --check app tests alembic

typecheck:
	$(VENV_PY) -m mypy app

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