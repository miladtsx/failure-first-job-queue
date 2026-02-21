# PM_001 — Duplicate execution after retry timeout

## Summary
FM_001 was triggered when a lease expired and the same job was retried by a second
worker while the first worker was still completing work. Without an explicit
idempotent commit boundary, both attempts could apply logical effects.

## Impact
- Violated `INV_001` (logical idempotency) in baseline mode.
- Risked duplicate irreversible side effects.
- Introduced ambiguity in whether recovery had restored correctness.

## Timeline (deterministic scenario)
1. Worker A leases and starts execution.
2. Lease expires (`lease_seconds=1`, work duration `=2`).
3. Worker B leases same job as retry.
4. Baseline path allows both attempts to apply effects.

## Root cause
- Missing enforced COMMITTED boundary on logical side effects.
- Retry semantics existed without duplicate-commit containment.

## Detection
- `effects_count > 1` for one `job_id` in repro test.
- Multiple successful attempts for a single logical job.

## Corrective actions
1. Added idempotent commit boundary behavior (`enforce_idempotent_commit`).
2. Added prevention test proving one-effect semantics.
3. Added recovery test for crash-after-commit-before-done.
4. Added reconcile policy to finalize `COMMITTED` executions safely.

## Verification
- `test_repro_fm001.py`: reproduces baseline duplicate effect.
- `test_prevent_fm001.py`: proves duplicate retries no-op at commit boundary.
- `test_recover_fm001.py`: proves reconcile restores correctness after crash.

## Follow-ups
- Extend reconcile to richer observability counters (`INV_005`).
- Add FM_002 for torn/partial state updates.

