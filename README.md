# MCP vs Traditional Integration — prototype (through Day 25)
Both arms share `src/core/` (tools, schemas, gateway). Only the backend differs:
`src/traditional/adapters.py` (direct call) vs `src/mcp_arm/` (MCP stdio server + client).
Run: `pip install -r requirements.txt && python -m src.run_day25 && pytest -q`
Note: package is `mcp_arm` (not `mcp`) to avoid shadowing the official SDK.
Pin `mcp<2`: v2 renamed FastMCP -> MCPServer.
