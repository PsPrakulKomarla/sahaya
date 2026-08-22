"""Shared pytest fixtures and environment isolation for the API test suite."""

import os
import sys

# Add project root to sys.path so packages.* imports resolve
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

# Applied before the application modules are imported so the settings
# singleton picks these up. Real values are never required in tests.
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("LOG_LEVEL", "WARNING")
