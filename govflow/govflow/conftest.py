import os
import sys

# Add apps/api for app.* imports (logging, config, etc.)
api_path = os.path.join(os.path.dirname(__file__), "apps", "api")
if api_path not in sys.path:
    sys.path.insert(0, api_path)
