"""Arm B: MCP server exposing the SAME business functions. Run via stdio."""
from mcp.server.fastmcp import FastMCP
from src.core import tools as t

mcp = FastMCP("research-tools")

@mcp.tool()
def get_project_status(project_id: str) -> dict:
    """Get status of a project."""
    return t.get_project_status(project_id)

@mcp.tool()
def get_experiment_results(experiment_id: str, limit: int = 10) -> dict:
    """Get results of an experiment."""
    return t.get_experiment_results(experiment_id, limit)

@mcp.tool()
def delete_experiment(experiment_id: str, confirm: bool) -> dict:
    """MOCK delete of an experiment."""
    return t.delete_experiment(experiment_id, confirm)

if __name__ == "__main__":
    mcp.run()
