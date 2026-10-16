"""Arm A: direct function adapter."""
from src.core.tools import REGISTRY


class DirectBackend:
    async def call(self, tool: str, args: dict):
        return REGISTRY[tool](**args)
