import os
import sys

# Add govflow root for packages.* imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
# Add apps/api for app.* imports (logging, config, etc.)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "apps", "api"))
