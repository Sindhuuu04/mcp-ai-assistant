"""Shared business logic. BOTH arms call exactly these functions (equivalence control)."""

_PROJECTS = {
    "alpha": {"status": "on_track", "progress_pct": 72},
    "beta": {"status": "at_risk", "progress_pct": 35},
}
_EXPERIMENTS = {
    "exp-001": {"accuracy": 0.91, "runs": 5},
    "exp-002": {"accuracy": 0.84, "runs": 3},
}


def get_project_status(project_id: str) -> dict:
    if project_id not in _PROJECTS:
        raise KeyError(f"unknown project: {project_id}")
    return {"project_id": project_id, **_PROJECTS[project_id]}


def get_experiment_results(experiment_id: str, limit: int = 10) -> dict:
    if experiment_id not in _EXPERIMENTS:
        raise KeyError(f"unknown experiment: {experiment_id}")
    return {"experiment_id": experiment_id, "limit": limit, **_EXPERIMENTS[experiment_id]}


def delete_experiment(experiment_id: str, confirm: bool) -> dict:
    """Write-like MOCK tool: records intent only, mutates nothing real."""
    return {"experiment_id": experiment_id, "deleted": True, "mock": True}


REGISTRY = {
    "get_project_status": get_project_status,
    "get_experiment_results": get_experiment_results,
    "delete_experiment": delete_experiment,
}
