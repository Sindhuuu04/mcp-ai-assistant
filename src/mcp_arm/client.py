import json, sys, os
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPBackend:
    """Async context manager: spawns the MCP server over stdio and calls tools."""
    async def __aenter__(self):
        self._stack = AsyncExitStack()
        params = StdioServerParameters(command=sys.executable, args=["-m", "src.mcp_arm.server"],
                                       env={**os.environ, "PYTHONPATH": os.getcwd()})
        r, w = await self._stack.enter_async_context(stdio_client(params))
        self.session = await self._stack.enter_async_context(ClientSession(r, w))
        await self.session.initialize()
        return self

    async def __aexit__(self, *a):
        await self._stack.aclose()

    async def list_tools(self):
        return [t.name for t in (await self.session.list_tools()).tools]

    async def call(self, tool: str, args: dict):
        res = await self.session.call_tool(tool, args)
        if res.isError:
            raise RuntimeError(res.content[0].text if res.content else "mcp error")
        if res.structuredContent is not None:
            return res.structuredContent.get("result", res.structuredContent)
        return json.loads(res.content[0].text)
