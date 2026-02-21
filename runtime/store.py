from __future__ import annotations

from dataclasses import dataclass

from runtime.clock import Clock


@dataclass
class ExecutionRecord:
    exec_id: str
    job_id: str
    attempt: int
    lease_owner: str
    lease_expires_at: float
    status: str = "LEASED"


class Store:
    """Minimal in-memory durable model used by FM_001 scenario tests."""

    def __init__(self, *, clock: Clock) -> None:
        self.clock = clock
        self._job_seq = 0
        self._exec_seq = 0
        self.jobs: dict[str, dict] = {}
        self.job_order: list[str] = []
        self.executions: dict[str, ExecutionRecord] = {}
        self.execs_by_job: dict[str, list[str]] = {}
        self.effects: list[tuple[str, str, float]] = []
        self._committed_by_job: dict[str, str] = {}

    @classmethod
    def in_memory(cls, *, clock: Clock) -> "Store":
        return cls(clock=clock)

    def create_job(self, *, payload: dict) -> str:
        self._job_seq += 1
        job_id = f"job-{self._job_seq}"
        self.jobs[job_id] = {"job_id": job_id, "payload": payload, "state": "PENDING"}
        self.job_order.append(job_id)
        self.execs_by_job[job_id] = []
        return job_id

    def can_lease(self, *, job_id: str, now: float) -> bool:
        exec_ids = self.execs_by_job[job_id]
        if not exec_ids:
            return True

        latest = self.executions[exec_ids[-1]]
        if latest.status == "DONE":
            return False
        return latest.lease_expires_at <= now

    def create_lease(self, *, job_id: str, worker_id: str, lease_seconds: int) -> str:
        self._exec_seq += 1
        exec_id = f"exec-{self._exec_seq}"
        attempt = len(self.execs_by_job[job_id]) + 1
        record = ExecutionRecord(
            exec_id=exec_id,
            job_id=job_id,
            attempt=attempt,
            lease_owner=worker_id,
            lease_expires_at=self.clock.now() + float(lease_seconds),
        )
        self.executions[exec_id] = record
        self.execs_by_job[job_id].append(exec_id)
        self.jobs[job_id]["state"] = "RUNNING"
        return exec_id

    def mark_started(self, exec_id: str) -> None:
        self.executions[exec_id].status = "IN_PROGRESS"

    def apply_effect(self, *, exec_id: str, enforce_idempotent_commit: bool) -> bool:
        record = self.executions[exec_id]
        job_id = record.job_id

        if enforce_idempotent_commit and job_id in self._committed_by_job:
            return False

        if job_id not in self._committed_by_job:
            self._committed_by_job[job_id] = exec_id

        record.status = "COMMITTED"
        self.effects.append((job_id, exec_id, self.clock.now()))
        return True

    def mark_finished(self, exec_id: str) -> None:
        record = self.executions[exec_id]
        record.status = "DONE"
        self.jobs[record.job_id]["state"] = "SUCCEEDED"

    def count_effects(self, job_id: str) -> int:
        return sum(1 for effect_job_id, _, _ in self.effects if effect_job_id == job_id)

    def get_committed_exec_id(self, job_id: str) -> str | None:
        return self._committed_by_job.get(job_id)

    def list_exec_ids_by_status(self, status: str) -> list[str]:
        return [exec_id for exec_id, record in self.executions.items() if record.status == status]

