from __future__ import annotations

from dataclasses import dataclass

from runtime.store import Store


@dataclass(frozen=True)
class CommitResult:
    """Outcome of trying to cross the COMMITTED boundary for one execution."""

    committed: bool
    committed_exec_id: str | None


def commit_effect_idempotent(*, store: Store, exec_id: str) -> CommitResult:
    """Enforce INV_001 by allowing at most one logical commit per job."""
    committed = store.apply_effect(exec_id=exec_id, enforce_idempotent_commit=True)
    job_id = store.executions[exec_id].job_id
    return CommitResult(committed=committed, committed_exec_id=store.get_committed_exec_id(job_id))

