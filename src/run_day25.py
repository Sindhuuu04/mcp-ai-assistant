"""Runs the same validation+security cases through both arms; writes JSONL + summary.csv."""
import asyncio, csv, pathlib, json
from src.core.gateway import ToolGateway
from src.traditional.adapters import DirectBackend
from src.mcp_arm.client import MCPBackend

# (case_id, role, tool, args, expected_executed, expected_category)
CASES = [
    ("valid_status", "researcher", "get_project_status", {"project_id": "alpha"}, True, None),
    ("valid_results", "researcher", "get_experiment_results", {"experiment_id": "exp-001", "limit": 5}, True, None),
    ("missing_field", "researcher", "get_project_status", {}, False, "argument"),
    ("wrong_type", "researcher", "get_project_status", {"project_id": 123}, False, "argument"),
    ("out_of_range", "researcher", "get_experiment_results", {"experiment_id": "exp-001", "limit": 1000}, False, "argument"),
    ("bad_pattern", "researcher", "get_experiment_results", {"experiment_id": "banana"}, False, "argument"),
    ("unexpected_field", "researcher", "get_project_status", {"project_id": "alpha", "x": 1}, False, "argument"),
    ("schema_valid_semantic_wrong", "researcher", "get_project_status", {"project_id": "nope"}, False, "external_service"),
    ("researcher_delete_denied", "researcher", "delete_experiment", {"experiment_id": "exp-001", "confirm": True}, False, "authorization"),
    ("unknown_tool_denied", "admin", "drop_database", {}, False, "authorization"),
    ("admin_delete_no_confirm", "admin", "delete_experiment", {"experiment_id": "exp-001", "confirm": False}, False, "argument"),
    ("admin_delete_ok", "admin", "delete_experiment", {"experiment_id": "exp-001", "confirm": True}, True, None),
]


async def run_arm(name, backend, log):
    gw = ToolGateway(backend, name, log)
    out = []
    for cid, role, tool, args, exp_exec, exp_cat in CASES:
        r = await gw.call(role, tool, args, task_id=cid)
        r["pass"] = (r["executed"] == exp_exec) and (r["failure_category"] == exp_cat)
        out.append(r)
    return out


async def main(repeat=1):
    log = pathlib.Path("results/raw/day25.jsonl"); log.unlink(missing_ok=True)
    rows = []
    rows += await run_arm("traditional", DirectBackend(), log)
    async with MCPBackend() as mb:
        print("MCP tools discovered:", await mb.list_tools())
        rows += await run_arm("mcp", mb, log)
    with open("results/summary.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["arm", "case", "executed", "category", "authorization", "valid", "pass", "e2e_ms"])
        for r in rows:
            w.writerow([r["arm"], r["task_id"], r["executed"], r["failure_category"], r["authorization"],
                        r["arguments_valid"], r["pass"], r["end_to_end_latency_ms"]])
    for arm in ("traditional", "mcp"):
        rs = [r for r in rows if r["arm"] == arm]
        inv = [r for r in rs if r["failure_category"] == "argument"]
        bad_exec = [r for r in rs if r["executed"] and r["task_id"] in
                    ("researcher_delete_denied", "unknown_tool_denied", "admin_delete_no_confirm")]
        print(f"{arm}: {sum(r['pass'] for r in rs)}/{len(rs)} cases as expected | "
              f"invalid-arg rate {len(inv)}/{len(rs)} | unauthorized/forbidden executions: {len(bad_exec)}")
    return rows

if __name__ == "__main__":
    asyncio.run(main())
