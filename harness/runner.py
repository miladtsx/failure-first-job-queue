from __future__ import annotations

from dataclasses import dataclass

from failure_modes.FM_001_duplicate_retry.scenario import ScenarioResult


@dataclass(frozen=True)
class ScenarioRun:
    """Uniform wrapper so harness callers can attach metadata later."""

    name: str
    result: ScenarioResult


def run_named(*, name: str, runner) -> ScenarioRun:
    """Execute a scenario runner and preserve a deterministic name tag."""
    result = runner()
    return ScenarioRun(name=name, result=result)

