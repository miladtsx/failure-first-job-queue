from __future__ import annotations

from dataclasses import dataclass

from runtime.clock import Clock
from runtime.store import Store


@dataclass(frozen=True)
class Lease:
    exec_id: str
    job_id: str
    worker_id: str


class Queue:
    """Minimal queue with at-least-once lease semantics for FM_001."""

    def __init__(self, *, store: Store, clock: Clock, lease_seconds: int) -> None:
        self.store = store
        self.clock = clock
        self.lease_seconds = lease_seconds

    def submit_job(self, *, payload: dict) -> str:
        return self.store.create_job(payload=payload)

    def lease(self, *, worker_id: str) -> Lease | None:
        now = self.clock.now()
        for job_id in self.store.job_order:
            if self.store.can_lease(job_id=job_id, now=now):
                exec_id = self.store.create_lease(
                    job_id=job_id,
                    worker_id=worker_id,
                    lease_seconds=self.lease_seconds,
                )
                return Lease(exec_id=exec_id, job_id=job_id, worker_id=worker_id)
        return None

