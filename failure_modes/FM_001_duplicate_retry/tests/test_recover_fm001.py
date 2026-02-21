from faults.injectors import Faults
from policies.reconcile import reconcile_after_crash
from runtime.clock import Clock
from runtime.queue import Queue
from runtime.store import Store
from runtime.worker import Worker


def test_recover_fm001_crash_after_commit_reconcile_restores_correctness():
    """FM_001 recovery: crash after COMMITTED must reconcile to DONE without duplicate effects.

    Protects:
    - INV_002 (crash consistency)
    - INV_004 (recovery restores correctness)
    """
    clock = Clock(start=0.0)
    store = Store.in_memory(clock=clock)
    queue = Queue(store=store, clock=clock, lease_seconds=1)

    worker = Worker(
        worker_id="W1",
        store=store,
        queue=queue,
        clock=clock,
        faults=Faults(
            enforce_idempotent_commit=True,
            crash_after_commit_before_done=True,
        ),
    )

    job_id = queue.submit_job(payload={"fm": "FM_001", "case": "recovery"})
    lease = queue.lease(worker_id="W1")
    assert lease is not None

    worker.start(lease)
    worker.finish(lease)  # crashes after COMMITTED, before DONE

    assert store.count_effects(job_id) == 1
    assert store.executions[lease.exec_id].status == "COMMITTED"
    assert store.jobs[job_id]["state"] == "RUNNING"

    result = reconcile_after_crash(store=store, clock=clock)

    assert lease.exec_id in result.finalized_exec_ids
    assert store.executions[lease.exec_id].status == "DONE"
    assert store.jobs[job_id]["state"] == "SUCCEEDED"
    assert store.count_effects(job_id) == 1
