# Failure Modes 

--- 

## FM-001 -- Duplicate execution caused by retry after timeout 

### Description 

A worker processes a job but exceeds its visibility timeout.
The queue retries the job while the original execution continues or later commits its result.

This leads to **duplicate logical execution**.

--- 

### Trigger 

- Worker exceeds processing timeout 
- Job is re-queued 
- A second worker picks up the same job 

--- 

### Observable symptoms 

- Duplicate side effects (e.g. double writes, double payments)
- Conflicting state updates 
- Inconsistent downstream behavior 

--- 

### Invariants violated 

- INV-001 -- Job execution is logically idempotent 
- INV-002 -- Partial execution must not cause irreversible damage 

--- 

### Why this is commonly missed 

- Tests assume successful completion 
- Timeouts are treated as rare 
- Retries are assumed to be safe 
- Idempotency is implied but not enforced

--- 

### Detection Strategy 

- Job execution IDs recorded in durable state 
- Duplicate execution attempts logged and counted 
- Mismatch between job completion count and side effects 

--- 

### Recovery strategy 

- Enforce idempotency using a durable execution key 
- Reject or short-circuit duplicate executions 
- Reconcile state based on committed execution records 

--- 

### Notes 

This failure mode exists in nearly all async systems.
If it is not explicitly handled, it will eventually cause data corruption.
