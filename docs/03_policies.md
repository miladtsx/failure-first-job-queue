# Policies (Recovery & Containment)

Policies are small, explicit mechanisms that keep invariants intact when failures occur. They operate on the minimal runtime (queue, worker, store, deterministic clock).

## Commit boundary (idempotency)
- Enforces [INV_001](01_invariants.md#inv_001----job-execution-is-logically-idempotent): effects apply exactly once.
- Side effects happen only at/after `COMMITTED`.
- Duplicate attempts must detect an existing `COMMITTED` record and no-op (see [FM_001 duplicate retry](../failure_modes/FM_001_duplicate_retry/spec.md)).

## Reconcile
- Enforces [INV_002](01_invariants.md#inv_002----partial-execution-must-not-leave-irreversible-damage) and [INV_004](01_invariants.md#inv_004----recovery-restores-correctness-not-just-availability): restore correctness after crashes/timeouts.
- Scans executions whose lease expired before commit; marks them `ABORTED` and re-queues safely.
- Recomputes job state from durable execution records (monotonic, explicit).

## Retry budget / circuit breaker
- Protects [INV_005](01_invariants.md#inv_005----failure-must-be-detectable) (detectability) and limits retry storms.
- Caps retries per job/time window; surfaces signals instead of infinite looping.

## Audit & observability
- Supports [INV_003](01_invariants.md#inv_003----job-state-transitions-are-monotonic-and-explicit) and [INV_005](01_invariants.md#inv_005----failure-must-be-detectable).
- Every state transition is persisted and counted; duplicate attempts are visible metrics, not mysteries.

## How these map to artifacts
- Defined in `policies/` modules.
- Exercised by scenarios under `failure_modes/FM_XXX_*/scenario.py`.
- Proven by `tests/test_prevent_fmxxx.py` which asserts invariants stay satisfied even under injected faults.
- Glossary references: see `GLOSSARY.md` entries for commit boundary, reconcile, retry budget, and idempotency boundary.
