from mcp.server.fastmcp import FastMCP
from typing import Dict, Any, List, Optional
import time

mcp = FastMCP("Observer Server")

# Mock Live State (simulating GNS3)
# In reality, this would query devices via NAPALM
LIVE_STATE = {
    "core-router": {
        "interfaces": {
            "GigabitEthernet0/0": {"is_up": True, "ip": "192.168.1.1"},
            "GigabitEthernet0/1": {"is_up": True, "ip": "10.0.0.1"}
        }
    },
    "dist-switch-01": {
        "interfaces": {
            "Ethernet1": {"is_up": True, "ip": "192.168.1.2"},
            "Ethernet2": {"is_up": True, "ip": "10.0.0.2"} # Link to core
        }
    }
}

@mcp.tool()
def check_reachability(source_device: str, target_ip: str) -> str:
    """Checks ping reachability from source to target."""
    if source_device not in LIVE_STATE:
        return f"Error: Device {source_device} not known."
    
    # Mock Logic: If target_ip is in our mock state and 'is_up', it works
    # Real logic: nornir_napalm -> ping
    
    reachable = True
    # Simulate a broken link logic
    if target_ip == "10.0.0.2" and not LIVE_STATE["dist-switch-01"]["interfaces"]["Ethernet2"]["is_up"]:
        reachable = False

    if reachable:
        return f"SUCCESS: {source_device} can reach {target_ip}. RTT=2ms."
    else:
        return f"FAILURE: {source_device} cannot reach {target_ip}. Request timed out."

@mcp.tool()
def get_interface_health(device: str, interface: str) -> str:
    """Returns interface status and errors."""
    dev = LIVE_STATE.get(device)
    if not dev:
        return f"Error: Device {device} not found."
    
    if interface not in dev["interfaces"]:
        return f"Error: Interface {interface} not found on {device}."
        
    state = dev["interfaces"][interface]
    status = "UP" if state["is_up"] else "DOWN"
    return f"Interface {interface}: {status}. Errors: 0. Drops: 0."

@mcp.tool()
def simulate_link_failure(device: str, interface: str):
    """(Simulation Tool) Cuts a wire in GNS3 (mocks it)."""
    if device in LIVE_STATE and interface in LIVE_STATE[device]["interfaces"]:
        LIVE_STATE[device]["interfaces"][interface]["is_up"] = False
        return f"Simulated cut on {device} {interface}."
    return "Interface not found."

@mcp.tool()
def detect_link_failures(topology_definition: str) -> List[str]:
    """
    Compares live state against expected topology.
    topology_definition: The YAML string from Librarian.
    """
    failures = []
    # logic to parse topology vs LIVE_STATE
    # For demo, just check if ANY interface in LIVE_STATE is down
    for dev_name, data in LIVE_STATE.items():
        for iface_name, iface_data in data["interfaces"].items():
            if not iface_data["is_up"]:
                failures.append(f"CRITICAL: {dev_name} {iface_name} is DOWN (Expected: UP)")
                
    if not failures:
        return ["All systems nominal. No deviation from topology."]
    return failures

@mcp.resource("observer://alerts/active")
def get_active_alerts() -> str:
    """Returns list of currently detected network issues."""
    alerts = detect_link_failures("") # We'd pass real topology here
    return "\n".join(alerts)

@mcp.prompt()
def monitor_critical_links() -> str:
    """Workflow: Monitor network health."""
    return """
1. Call `librarian` to get `topology/definition`.
2. Call `detect_link_failures` with that definition.
3. If failures found, analyze impact.
4. If no failures, wait and poll again.
    """

if __name__ == "__main__":
    mcp.run()
