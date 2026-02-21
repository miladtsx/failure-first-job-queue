from faults.injectors import Faults
from runtime.clock import Clock
from runtime.queue import Queue
from runtime.store import Store
from runtime.worker import Worker


def test_happy_path_single_worker_commits_once_and_succeeds():
    """Single-worker baseline with guardrails enabled.

    Why keep `enforce_idempotent_commit=True` in a naive happy path?
    - We want the baseline to run under the same safety policy used in real runs.
    - This proves the guardrail does not break normal success flow.
    - FM_001 tests separately prove the guardrail matters under retry/failure.
    """
    clock = Clock(start=0.0)
    store = Store.in_memory(clock=clock)
    queue = Queue(store=store, clock=clock, lease_seconds=5)

    # Use policy-on configuration even in happy path; safety should be default.
    guarded_faults = Faults(enforce_idempotent_commit=True)
    worker = Worker(
        worker_id="W1",
        store=store,
        queue=queue,
        clock=clock,
        faults=guarded_faults,
    )

    # 1) Submit one job. The queue/store begin in a strict happy-path state (PENDING).
    job_id = queue.submit_job(payload={"kind": "happy-path"})
    assert store.jobs[job_id]["state"] == "PENDING"

    # 2) W1 receives the lease. Leasing is the boundary where state flips to RUNNING and the execution record is created.
    lease = queue.lease(worker_id="W1")
    assert lease is not None
    assert lease.job_id == job_id
    assert store.jobs[job_id]["state"] == "RUNNING"

    # 3) Lease exclusivity verification: the queue denies W2 while W1 still holds the lease because the latest execution is not DONE.
    assert queue.lease(worker_id="W2") is None

    # 4) W1 begins work. The worker marks the execution IN_PROGRESS before touching any side effects.
    worker.start(lease)
    assert store.executions[lease.exec_id].status == "IN_PROGRESS"

    worker.finish(lease)

    # 5) INV_001 enforcement: apply_effect runs once and records the committed exec_id, guaranteeing idempotent side effects.
    assert store.count_effects(job_id) == 1
    assert store.get_committed_exec_id(job_id) == lease.exec_id

    # 6) INV_003 projection: execution DONE causes the job aggregate to become SUCCEEDED, not the other way around.
    assert store.executions[lease.exec_id].status == "DONE"
    assert store.jobs[job_id]["state"] == "SUCCEEDED"

    # 7) The job is terminal, so future leases are denied even if another worker asks for work.
    assert queue.lease(worker_id="W2") is None


def test_happy_path_two_workers_second_worker_cannot_lease_after_success():
    """Two-worker readability test for the non-failure flow.

    Story:
    - W1 leases and completes the job.
    - W2 is present, but cannot lease during active work or after terminal success.
    - Outcome still preserves one-effect semantics.

    We enable idempotent-commit policy for *both* workers intentionally:
    policy is a system-wide guardrail, not a per-worker special case.
    """
    clock = Clock(start=0.0)
    store = Store.in_memory(clock=clock)
    queue = Queue(store=store, clock=clock, lease_seconds=5)

    guarded_faults = Faults(enforce_idempotent_commit=True)
    worker_1 = Worker(
        worker_id="W1",
        store=store,
        queue=queue,
        clock=clock,
        faults=guarded_faults,
    )
    worker_2 = Worker(
        worker_id="W2",
        store=store,
        queue=queue,
        clock=clock,
        faults=guarded_faults,
    )

    # 1) Submit job and let W1 claim it. The queue enforces FIFO and state transitions, so the job gets LEASED.
    job_id = queue.submit_job(payload={"kind": "happy-path-two-workers"})
    lease_w1 = queue.lease(worker_id=worker_1.worker_id)

    assert lease_w1 is not None
    assert lease_w1.job_id == job_id

    # 2) W2 is ready but must not steal the lease; the queue must still honor the current RUNNING execution until it finishes.
    assert queue.lease(worker_id=worker_2.worker_id) is None

    # 3) W1 walks the happy path (start → apply effect → finish). The guardrail ensures duplicate commits would short-circuit.
    worker_1.start(lease_w1)
    worker_1.finish(lease_w1)

    # 4) INV_001: we still expect a single logical effect and one committed exec_id no matter how many workers exist.
    assert store.count_effects(job_id) == 1
    assert store.get_committed_exec_id(job_id) == lease_w1.exec_id

    # 5) INV_003: DONE → SUCCEEDED projection is deterministic (Job state follows execution state).
    assert store.executions[lease_w1.exec_id].status == "DONE"
    assert store.jobs[job_id]["state"] == "SUCCEEDED"

    # 6) After the job reaches SUCCEEDED, W2 sees a non-leasable terminal job and cannot record another effect.
    assert queue.lease(worker_id=worker_2.worker_id) is None
    assert store.count_effects(job_id) == 1
