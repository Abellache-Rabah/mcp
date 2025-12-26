from mcp.server.fastmcp import FastMCP
from typing import Dict, Any, Optional
import time
import difflib

# In a real implementation:
# from nornir import InitNornir
# from nornir_scrapli.tasks import send_config, send_command
# from nornir_utils.plugins.functions import print_result

mcp = FastMCP("Deployer Server")

# Mock State for demonstration
CONFIG_STORE = {
    "core-router": "hostname core-router\n!",
    "dist-switch-01": "hostname dist-switch-01\n!"
}

@mcp.tool()
def get_config_diff(device: str, new_config: str) -> str:
    """Calculates diff between current running config (simulated) and candidate."""
    current = CONFIG_STORE.get(device, "")
    
    diff = difflib.unified_diff(
        current.splitlines(keepends=True),
        new_config.splitlines(keepends=True),
        fromfile=f"running-config@{device}",
        tofile="candidate-config"
    )
    return "".join(diff)

@mcp.tool()
def deploy_config(device: str, config: str, dry_run: bool = True, auto_rollback: bool = True) -> str:
    """
    Deploys configuration to a device.
    
    Args:
        device: Target device hostname.
        config: Configuration commands/content.
        dry_run: If True, only simulates the deploy (default: True).
        auto_rollback: If True, requires verification or it reverts (simulated).
    """
    if device not in CONFIG_STORE:
        return f"Error: Device {device} not found/reachable."

    if dry_run:
        return f"[DRY-RUN] Would push the following config to {device} via Scrapli/Nornir:\n{config}"

    # Simulation of real deploy
    backup = CONFIG_STORE[device]
    try:
        # "Push" config
        CONFIG_STORE[device] = config
        
        if auto_rollback:
            # Simulate a health check (mock)
            # In real life, we would call the Observer server here or run local checks
            # For demo, if config contains "bad", we fail
            if "bad" in config.lower():
                raise Exception("Health check failed post-deploy")
        
        return f"SUCCESS: Config deployed to {device}. Verification passed."

    except Exception as e:
        # Rollback
        CONFIG_STORE[device] = backup
        return f"FAILURE: Deploy failed. Rolled back to previous state. Error: {str(e)}"

@mcp.tool()
def rollback(device: str, revision_id: str = "last") -> str:
    """Manually rollback configuration."""
    # Mock implementation
    return f"Rolled back {device} to revision {revision_id}."

@mcp.prompt()
def plan_deployment(device: str) -> str:
    """Workflow: Plan a safe deployment."""
    return f"""To safely deploy to {device}, please follows these steps:
1. Retrieve current config.
2. Generate candidate config.
3. Call `get_config_diff` to review changes.
4. Verify config with `verifier` server.
5. Call `deploy_config` with dry_run=True.
6. If all good, call `deploy_config` with dry_run=False and auto_rollback=True.
"""

if __name__ == "__main__":
    mcp.run()
