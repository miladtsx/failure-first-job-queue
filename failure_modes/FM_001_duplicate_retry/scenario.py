from __future__ import annotations

from dataclasses import dataclass

from faults.injectors import Faults
from runtime.clock import Clock
from runtime.queue import Queue
from runtime.store import Store
from runtime.worker import Worker


@dataclass(frozen=True)
class ScenarioResult:
    job_id: str
    effects_count: int
    committed_exec_id: str | None


def _run_internal(*, lease_seconds: int, work_duration_seconds: int, faults: Faults) -> ScenarioResult:
    """Core deterministic FM_001 executor used by explicit baseline/guarded entrypoints."""
    clock = Clock(start=0.0)
    store = Store.in_memory(clock=clock)
    queue = Queue(store=store, clock=clock, lease_seconds=lease_seconds)

    worker_a = Worker(worker_id="A", store=store, queue=queue, clock=clock, faults=faults)
    worker_b = Worker(worker_id="B", store=store, queue=queue, clock=clock, faults=faults)

    job_id = queue.submit_job(payload={"fm": "FM_001"})

    # Step 1: A leases and starts.
    exec_a = queue.lease(worker_id="A")
    assert exec_a is not None
    worker_a.start(exec_a)

    # Step 2: advance deterministic clock to expire lease.
    clock.advance(float(work_duration_seconds))

    # Step 3: B retries after timeout.
    exec_b = queue.lease(worker_id="B")
    assert exec_b is not None

    # Step 4: both workers finish and attempt logical effect.
    worker_a.finish(exec_a)
    worker_b.start(exec_b)
    worker_b.finish(exec_b)

    return ScenarioResult(
        job_id=job_id,
        effects_count=store.count_effects(job_id),
        committed_exec_id=store.get_committed_exec_id(job_id),
    )


def run_known_broken_baseline(*, lease_seconds: int, work_duration_seconds: int) -> ScenarioResult:
    """Explicit baseline path: no commit-boundary guardrail (expected INV_001 violation)."""
    return _run_internal(
        lease_seconds=lease_seconds,
        work_duration_seconds=work_duration_seconds,
        faults=Faults.none(),
    )


def run_guarded_with_commit_boundary(*, lease_seconds: int, work_duration_seconds: int) -> ScenarioResult:
    """Explicit prevention path: commit boundary enabled (expected INV_001 preservation)."""
    return _run_internal(
        lease_seconds=lease_seconds,
        work_duration_seconds=work_duration_seconds,
        faults=Faults(enforce_idempotent_commit=True),
    )


def run(*, lease_seconds: int, work_duration_seconds: int, faults: Faults) -> ScenarioResult:
    """Backward-compatible runner for templates and existing tests."""
    return _run_internal(
        lease_seconds=lease_seconds,
        work_duration_seconds=work_duration_seconds,
        faults=faults,
    )

