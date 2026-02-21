from __future__ import annotations

from faults.injectors import Faults
from runtime.clock import Clock
from runtime.queue import Lease, Queue
from runtime.store import Store


class Worker:
    """Minimal worker that can reproduce or prevent FM_001 based on fault flags."""

    def __init__(
        self,
        *,
        worker_id: str,
        store: Store,
        queue: Queue,
        clock: Clock,
        faults: Faults,
    ) -> None:
        self.worker_id = worker_id
        self.store = store
        self.queue = queue
        self.clock = clock
        self.faults = faults

    def start(self, lease: Lease) -> None:
        self.store.mark_started(lease.exec_id)

    def finish(self, lease: Lease) -> None:
        if self.faults.crash_before_commit:
            return

        self.store.apply_effect(
            exec_id=lease.exec_id,
            enforce_idempotent_commit=self.faults.enforce_idempotent_commit,
        )

        if self.faults.crash_after_commit_before_done:
            return

        self.store.mark_finished(lease.exec_id)

