"""
Scenario driver for FM_XXX.

Rules:
- Must be deterministic.
- Must be runnable from tests without global state.
- Must use the project's clock / fault injection facilities.
"""

from __future__ import annotations

from dataclasses import dataclass

from runtime.clock import Clock
from runtime.store import Store
from runtime.queue import Queue
from runtime.worker import Worker
from faults.injectors import Faults


@dataclass(frozen=True)
class ScenarioResult:
    """
    Keep this minimal and explicit.
    Tests should assert on these fields, not on incidental internals.
    """

    job_id: str
    effects_count: int
    committed_exec_id: str | None
    notes: str = ""


def run(
    *,
    lease_seconds: int,
    work_duration_seconds: int,
    faults: Faults,
) -> ScenarioResult:
    """
    Execute the smallest steps required to reproduce FM_XXX.
    The caller controls time and faults.

    Parameters:
      - lease_seconds: lease duration used by the queue
      - work_duration_seconds: how long the worker "works" before trying to commit
      - faults: configured fault injectors for this scenario
    """
    clock = Clock(start=0.0)
    store = Store.in_memory(clock=clock)
    queue = Queue(store=store, clock=clock, lease_seconds=lease_seconds)
    effects = store.effects  # or store.list_effects(), depending on your design

    # Worker should accept faults and clock.
    worker_a = Worker(
        worker_id="A", store=store, queue=queue, clock=clock, faults=faults
    )
    worker_b = Worker(
        worker_id="B", store=store, queue=queue, clock=clock, faults=faults
    )

    job_id = queue.submit_job(payload={"scenario": "FM_XXX"})

    # 1) Worker A leases and begins work.
    exec_a = queue.lease(worker_id="A")
    assert exec_a is not None

    worker_a.start(exec_a)

    # 2) Advance time to trigger the failure condition (e.g., lease expiry).
    clock.advance(float(work_duration_seconds))

    # 3) Worker B leases (retry) if applicable.
    exec_b = queue.lease(worker_id="B")

    # 4) Apply the scenario-specific sequence.
    # Replace with the exact steps for FM_XXX.
    worker_a.finish(exec_a)

    if exec_b is not None:
        worker_b.start(exec_b)
        worker_b.finish(exec_b)

    # 5) Collect explicit outputs for tests.
    effects_count = store.count_effects(job_id=job_id)
    committed_exec_id = store.get_committed_exec_id(job_id=job_id)

    return ScenarioResult(
        job_id=job_id,
        effects_count=effects_count,
        committed_exec_id=committed_exec_id,
    )
