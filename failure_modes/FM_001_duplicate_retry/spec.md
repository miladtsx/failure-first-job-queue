# FM_001 — Duplicate execution caused by retry after timeout

## Description

When the first worker exceeds lease timeout, the queue re-leases the same job to
another worker. Without an idempotent commit boundary, both workers can apply
the logical effect.

## Trigger

1. Worker A leases job `J`.
2. Worker A starts work and lease expires.
3. Worker B leases the same job `J` as retry.
4. Both workers finish and apply effects.

## Symptoms

- duplicate side effects for the same `job_id`
- two successful executions for one logical job

## Violated invariants

- `INV_001` (logical idempotency)
- `INV_002` (partial execution crash consistency risk)
- `INV_004` (recovery must restore correctness after crash)

## Detection

- count of side effects by `job_id` > 1
- more than one execution reaching terminal success semantics for the same job

## Recovery / prevention strategy

- enforce a durable `COMMITTED` boundary per `job_id`
- only first commit is accepted
- duplicate attempts must no-op safely

## Acceptance criteria

- `test_repro_fm001.py` proves duplicate effects in baseline mode
- `test_prevent_fm001.py` proves exactly one effect after commit boundary
- `test_recover_fm001.py` proves crash-after-commit reconciles to correct terminal state without duplicate effects
