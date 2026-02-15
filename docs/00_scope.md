# Scope 

We intentionally models a *narrow class of systems** in order to study failure, state corruption, and recovery behavior with precision.

Breadth is explicitly rejected in favor of depth.

--- 

## In scope 

This system models (see [`state_model`](./02_state_model.md) for structure): 

- Asynchronous job processing
- At-least-once delivery semantics 
- Duplicate job execution
- Partial execution and partial writes 
- Worker crashes during execution 
- Retry behavior and retry storms 
- Recovery after downtime 
- State reconciliation after failure 

The focus is on **correctness under failure** (see invariants in [`invariants`](./01_invariants.md)), not performance or scale.

--- 

## Out of scope 

The following are intentionally excluded:

- Performance optimization
- Horizontal scaling 
- High availability guarantees 
- Load balancing strategies 
- UI or dashboards 
- Authorization and authentication 
- Network-level participations (initially)
- Consensus algorithms
- Exactly-once delivery claims 

These concerns are excluded because they **obscure failure behavior** rather than clarify it.

--- 

## Design constraints 

Every failure added to this system must satisfy **at least one** of the following:

- Introduce a new failure mode 
- Detect an existing failure mode 
- Prevent state corruption 
- Enable safe recovery 

--- 

## Guiding assumption

Failure is not an exception.

Failure is the **normal operating condition** under which the system must remain correct.
