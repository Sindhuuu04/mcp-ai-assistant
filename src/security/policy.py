"""Day 24: local policy. SIMULATED identities -- not production authentication."""
TOOL_PERMISSIONS = {
    "get_project_status": "research:read",
    "get_experiment_results": "research:read",
    "delete_experiment": "research:write",
}
ROLE_SCOPES = {
    "researcher": {"research:read"},
    "admin": {"research:read", "research:write"},
}


def authorize(role: str, tool: str):
    """Deny by default: unknown tool or unknown role -> deny. Returns (allowed, reason)."""
    needed = TOOL_PERMISSIONS.get(tool)
    if needed is None:
        return False, "unknown_tool"
    if needed not in ROLE_SCOPES.get(role, set()):
        return False, f"missing_scope:{needed}"
    return True, "ok"
