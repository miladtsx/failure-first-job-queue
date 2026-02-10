# State Model 

This document defines the minimum state required to enforce the invariants in `01-invariants.md` and to model failures like `FM-001`.

The system assumes **at-least-once delivery**. Duplicate delivery is expected.

--- 

## Entities 

### Job 
A unit of work identified by `job_id`.

Minimum fields:

- `job_id` (string, unique)
- `payload` (unknown)
- `state` (enum, see below)
- `attempt` (int, monotonically increasing)
- `created_at`, `updated_at` (timestamps)

### Execution
A single attempt to run a job, identified by `exec_id`.

Minimum fields:

- `exec_id` (string, unique)
- `job_id` (string, foreign key)
- `attempt` (int)
- `lease_owner` (worker_id)
- `lease_expires_at` (timestamp)
- `status` (enum, see below)
- `started_at`, `finished_at` (timestamps, nullable)

Executions are durable records used for:
- idempotency (INV-001)
- crash consistency (INV-002)
- auditability (INV-003)
- recovery (INV-004)

--- 

## Job States 

Job state is a coarse, user-facing view:

- `PENDING` : created, not yet leased 
- `RUNNING` : leased by some execution 
- `SUCCEEDED` : completed successfully
- `FAILED` : terminal failure 

Job state must be derived from durable execution state, not assumed.

--- 

## Execution Status (source of truth)

Execution status is the internal, durable source of truth:

- `LEASED`      : worker owns the lease until `lease_expires_at`
- `IN_PROGRESS` : worker started performing work 
- `COMMITTED`  : logical effect applied (idempotent boundary)
- `DONE`        : execution finished after commit  
- `ABORTED`     : lease expired or worker crashed before commit 

**COMMITTED** is the key boundary:
- Side effects are allowed only at or after COMMITTED.
- Duplicate executions must short-circuit if a COMMITTED record already exists.

--- 

## Allowed Transactions 

### Execution transactions 

- `LEASED` -> `IN_PROGRESS`
- `IN_PROGRESS` -> `COMMITTED`
- `COMMITTED` -> `DONE`

Failure paths:

- `LEASED` -> `ABORTED` (lease expires before start)
- `IN_PROGRESS` -> `ABORTED` (crash/timeout before commit)

A worker may only progress an execution it currently leases.


### Job transitions (derived) 

- `PENDING` -> `RUNNING` when an execution is LEASED 
- `RUNNING` -> `SUCCEEDED` when any execution reaches DONE (after COMMITTED)
- `RUNNING` -> `PENDING` when lease expires and no execution is COMMITTED

--- 

## Idempotency rule (INV-001)

For a given `job_id`: 

- At most one execution may reach `COMMITTED`.
- Any later execution attempt must detect the committed record and no-op.

Implementation options (later):
- unique constraint on `(job_id, committed=true)`
- compare-and-set on `commit_record`
- dedicated `job_effects` table keyed by `job_id`

--- 

## Crash consistency rule (INV-002)

Work must be structured into two phases:

1. **Prepare phase** (safe to repeat)
  - compute results 
  - validate preconditions 
  - stage output

2. **Commit phase** (idempotent boundary)
  - atomically mark `COMMITTED`
  - apply logical effect exactly once 

If crash happens before COMMITTED:
- system may retry safely

If crash happens after COMMITTED but before DONE:
- recovery must finalize / reconcile to DONE without duplicating effects.

--- 

## How FM-001 happens in this model 

- Worker A leases `exec_id=A1` and starts work 
- Lease expires (timeout), system creates `exec_id=B1`
- Worker B leases `B1` and runs the same job 
- without the COMMITTED idempotency boundary, both apply effects 

FM-001 is prevented by enforcing:
- single COMMITTED execution per job_id 
- duplicate executions short-circuit at commit time 

--- 

## Minimal Implementation target (v0)

To keep scope tight, v0 requires only: 

- durable execution records 
- leasing with timeouts 
- a committed marker 
- a worker that can be killed mid-job 
- tests that reproduce FM-001 and prove the fix 
