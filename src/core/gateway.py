"""Identical guard pipeline for both arms: authorize -> validate -> (semantic) -> execute via backend."""
import time, uuid, json, pathlib


class ToolGateway:
    def __init__(self, backend, arm: str, log_path=None):
        self.backend, self.arm, self.log_path = backend, arm, log_path

    async def call(self, role: str, tool: str, args: dict, task_id: str = "adhoc") -> dict:
        from src.security.policy import authorize
        from src.core.schemas import validate_args
        t_start = time.perf_counter()
        rec = {"run_id": str(uuid.uuid4()), "arm": self.arm, "task_id": task_id, "role": role,
               "selected_tool": tool, "authorization": None, "arguments_valid": None,
               "executed": False, "tool_latency_ms": None, "validation_latency_ms": None,
               "failure_category": None, "error": None, "result": None}
        allowed, reason = authorize(role, tool)                      # 1. authorize first
        rec["authorization"] = "allow" if allowed else f"deny:{reason}"
        if not allowed:
            rec["failure_category"] = "authorization"
            return self._finish(rec, t_start)
        ok, errs, v_ms = validate_args(tool, args)                    # 2. schema validation
        rec["arguments_valid"], rec["validation_latency_ms"] = ok, round(v_ms, 4)
        if not ok:
            rec.update(failure_category="argument", error="; ".join(errs))
            return self._finish(rec, t_start)
        if tool == "delete_experiment" and args.get("confirm") is not True:  # 3. semantic check
            rec.update(failure_category="argument", error="semantic: confirm must be true")
            return self._finish(rec, t_start)
        t0 = time.perf_counter()                                      # 4. execute
        try:
            rec["result"] = await self.backend.call(tool, args)
            rec["executed"] = True
        except Exception as e:
            rec.update(failure_category="external_service", error=f"{type(e).__name__}: {e}")
        rec["tool_latency_ms"] = round((time.perf_counter() - t0) * 1000, 3)
        return self._finish(rec, t_start)

    def _finish(self, rec, t_start):
        rec["end_to_end_latency_ms"] = round((time.perf_counter() - t_start) * 1000, 3)
        if self.log_path:
            p = pathlib.Path(self.log_path); p.parent.mkdir(parents=True, exist_ok=True)
            with p.open("a") as f:
                f.write(json.dumps(rec) + "\n")
        return rec
