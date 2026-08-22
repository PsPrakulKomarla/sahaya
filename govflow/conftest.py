import os
import sys

# Add govflow root for app.* imports
govflow_root = os.path.join(os.path.dirname(__file__), "..", "..")
if govflow_root not in sys.path:
    sys.path.insert(0, govflow_root)

# Add apps/api for app.* imports (logging, config, etc.)
api_path = os.path.join(os.path.dirname(__file__), "apps", "api")
if api_path not in sys.path:
    sys.path.insert(0, api_path)

# Add packages for agent/* imports
packages_path = os.path.join(os.path.dirname(__file__), "packages")
if packages_path not in sys.path:
    sys.path.insert(0, packages_path)

# Add packages/agent for sub-agent imports
agent_path = os.path.join(os.path.dirname(__file__), "packages", "agent")
if agent_path not in sys.path:
    sys.path.insert(0, agent_path)

# Add packages/agent/recovery for recovery imports
recovery_path = os.path.join(os.path.dirname(__file__), "packages", "agent", "recovery")
if recovery_path not in sys.path:
    sys.path.insert(0, recovery_path)

# Add packages/agent/safety for safety imports
safety_path = os.path.join(os.path.dirname(__file__), "packages", "agent", "safety")
if safety_path not in sys.path:
    sys.path.insert(0, safety_path)