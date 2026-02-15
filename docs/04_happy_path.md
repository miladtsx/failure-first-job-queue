# Baseline Happy Path

Concise reference for the non-failure flow. Rules live in `docs/01_invariants.md`; state transitions live in `docs/02_state_model.md`. This page only pins the happy-path ordering and where we check the boundaries.

---

## Canonical sequence

```mermaid
flowchart TD
  %% agenda helps readers orient the boundary checks


  A["Create job<br/>(PENDING)"] --> B["Lease to worker W1<br/>(LEASED)<br/>set <i>lease_expires_at</i>"]
  B --> C[Mark IN_PROGRESS]
  C --> D{Prior COMMITTED?}
  D -->|no| E["Apply effect once<br/>+ mark COMMITTED"]
  D -->|yes| E2[Short-circuit, no effect]
  E --> F[Mark DONE]
  E2 --> F
  F --> G[Derive job SUCCEEDED]
  G --> H[Record audit: effects_count=1]
  H --> I[Release lease]
  I --> J[No retries issued]

  %% boundary highlighting (opaque group boxes)
  subgraph LeaseBoundary[Lease boundary]
    B
  end
  subgraph CommitBoundary[Commit boundary]
    D
    E
    E2
  end
  subgraph AuditBoundary[Audit & release]
    H
    I
  end

  classDef boundary stroke:#d97706,stroke-width:3px,color:#1f2937,fill:#fef3c7;
  classDef audit stroke:#2563eb,stroke-width:3px,color:#0f172a,fill:#e0f2fe;
  class LeaseBoundary boundary;
  class CommitBoundary boundary;
  class AuditBoundary audit;

  %% legend (agenda already shows order of boundary checks)
```

- Output constraints:
  - one logical effect
  - one committed execution
  - zero retries.
- Idempotency boundary
  - sits at `COMMITTED`
  - side effects are illegal before it ([INV_001/INV_002](./01_invariants.md)).
- Transition order mirrors the execution machine from [`02_state_model.md`](./02_state_model.md)
  - jobs stay derived.

---

## Lease eligibility (summary)

- **Leasable**: never leased, or lease expired with no terminal success.
- **Not leasable**: latest execution `DONE`, or an unexpired lease exists.

This is the minimum needed for `at-least-once` delivery while avoiding duplicate effects.

---

## Invariant touchpoints

- Lease grant asserts INV_003 (explicit states) and sets up INV_004 (recoverable retries).
- Commit boundary enforces INV_001 / INV_002 (single effect, crash-safe).
- Audit after `DONE` keeps INV_005 observable.

Details stay centralized in `docs/01_invariants.md` to avoid drift.

---

## Failure hook for FM_001

Injection point: between `IN_PROGRESS` and `COMMITTED`.  
Scenario: 
  - Worker A times out before commit; 
  - Worker B retries and would double-apply unless the commit boundary short-circuits.
