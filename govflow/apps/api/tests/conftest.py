"""Shared pytest fixtures and environment isolation for the API test suite."""

import os

# Applied before the application modules are imported so the settings
# singleton picks these up. Real values are never required in tests.
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("LOG_LEVEL", "WARNING")
