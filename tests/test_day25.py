import asyncio, pytest
from src.run_day25 import CASES
from src.core.gateway import ToolGateway
from src.traditional.adapters import DirectBackend
from src.mcp_arm.client import MCPBackend


@pytest.mark.parametrize("case", CASES, ids=[c[0] for c in CASES])
def test_direct_arm(case):
    cid, role, tool, args, exp_exec, exp_cat = case
    r = asyncio.run(ToolGateway(DirectBackend(), "traditional").call(role, tool, args, cid))
    assert r["executed"] == exp_exec and r["failure_category"] == exp_cat


def test_mcp_arm_matches_direct():
    async def go():
        async with MCPBackend() as mb:
            for cid, role, tool, args, exp_exec, exp_cat in CASES:
                r = await ToolGateway(mb, "mcp").call(role, tool, args, cid)
                d = await ToolGateway(DirectBackend(), "traditional").call(role, tool, args, cid)
                assert (r["executed"], r["failure_category"]) == (exp_exec, exp_cat), cid
                assert r["result"] == d["result"], cid   # equivalence of outputs
    asyncio.run(go())


def test_invalid_args_never_reach_backend():
    class Spy:
        called = False
        async def call(self, *a): Spy.called = True
    asyncio.run(ToolGateway(Spy(), "x").call("researcher", "get_project_status", {}, "t"))
    assert Spy.called is False
