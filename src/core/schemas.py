"""Day 25: JSON Schemas + validation. Schema validity != semantic correctness."""
import time
from jsonschema import Draft202012Validator

TOOL_SCHEMAS = {
    "get_project_status": {
        "type": "object",
        "properties": {"project_id": {"type": "string", "minLength": 1, "maxLength": 64}},
        "required": ["project_id"],
        "additionalProperties": False,
    },
    "get_experiment_results": {
        "type": "object",
        "properties": {
            "experiment_id": {"type": "string", "pattern": "^exp-[0-9]{3}$"},
            "limit": {"type": "integer", "minimum": 1, "maximum": 100},
        },
        "required": ["experiment_id"],
        "additionalProperties": False,
    },
    "delete_experiment": {
        "type": "object",
        "properties": {
            "experiment_id": {"type": "string", "pattern": "^exp-[0-9]{3}$"},
            "confirm": {"type": "boolean"},
        },
        "required": ["experiment_id", "confirm"],
        "additionalProperties": False,
    },
}
_VALIDATORS = {k: Draft202012Validator(v) for k, v in TOOL_SCHEMAS.items()}


def validate_args(tool: str, args: dict):
    """Returns (ok, errors, latency_ms). Semantic checks (e.g. confirm must be True) live elsewhere."""
    t0 = time.perf_counter()
    errors = [f"{'/'.join(map(str, e.path)) or '<root>'}: {e.message}"
              for e in _VALIDATORS[tool].iter_errors(args)]
    return (not errors, errors, (time.perf_counter() - t0) * 1000)
