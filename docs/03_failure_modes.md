# Failure Modes Index
> Failures aren’t “features,” they’re conditions. Each FM links to a spec, scenario, and tests.

## Catalog (growing)
- **FM_001 – Duplicate Retry (Retry Amplification of Side Effects)**  
  - Trigger: lease expires; queue reissues job while original execution may still commit.  
  - Violated invariants: INV_001 (logical idempotency), INV_002 (crash consistency).  
  - Artifacts: `failure_modes/FM_001_duplicate_retry/spec.md`, `scenario.py`, `tests/test_repro_fm001.py`, `tests/test_prevent_fm001.py`.

## FM_001 details (baseline focus)

### Definition
Ambiguous completion under autonomous retry logic causes duplicate or inconsistent side effects because there is no enforceable commit boundary.

### Trigger
- Worker exceeds processing timeout; job re-queued.
- Second worker picks up same job before the first commits.

### Observable symptoms
- Duplicate side effects (double writes/charges).
- Conflicting state updates; downstream divergence.

### Invariants violated
- INV_001 — Job execution is logically idempotent.
- INV_002 — Partial execution must not cause irreversible damage.

### Detection strategy
- Durable execution IDs per attempt.
- Duplicate attempts logged and counted.
- Mismatch between commit count and effect count alarms.

### Recovery strategy
- Enforce idempotent commit boundary keyed by `job_id` + execution attempt.
- Short-circuit duplicates on seeing a prior COMMITTED record.
- Reconcile state using committed execution records.

### Why this is commonly missed
- Tests assume success and ignore timeouts.
- Retries treated as harmless.
- Idempotency implied rather than enforced.
