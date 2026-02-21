This repository is a **Failure-First Reliability Lab**.

Optimize for:
- **correctness under failure**
- **explicit invariants**
- **reproducible failure modes**
- **recovery that restores correctness (not just availability)**

If you cannot connect your change to those goals, do not make the change.

---

## Mission

Build a minimal job-processing system where each failure mode is:
1) reproducible,
2) detectable,
3) preventable or recoverable,
4) proven by tests.

Primary outcome: a growing suite of failure-mode scenarios + proofs.

---

## Non-negotiable rules

### 1) 100% TDD for behavior changes
- For any new behavior: **add/modify tests first**
- Tests must be deterministic and isolated

### 2) Invariants are the source of truth
- All behavior must trace back to `docs/01_invariants.md`
- Every failure mode must reference violated invariants (INV_XXX)

### 3) One failure mode at a time
- Do not introduce multiple new failure modes in one change set
- Avoid scope creep (see `docs/00_scope.md`)

### 4) No performance work unless it is a failure mode
- “Optimize” only if it prevents a failure mode (e.g., retry storm budget)
- No refactors that don’t change failure behavior or test clarity

### 5) Determinism
- Use `runtime/clock.py` (or test-controlled time) instead of real `time.sleep`
- Avoid flaky timing assumptions

### 6) Minimal surface area
- Prefer the smallest implementation that satisfies the invariant
- Add abstractions only when demanded by multiple failure modes

---

## Repository map (where things go)

- `docs/`
  - specifications: scope, invariants, state model, failure modes

- `failure_modes/FM_XXX_*`
  - `spec.md` : single-page description of FM_XXX
  - `scenario.py` : reproducible steps and setup
  - `tests/` : two tests minimum (repro + prevent)

- `runtime/`
  - production-like minimal system (queue, store, worker, schema, effects, clock)

- `faults/`
  - reusable fault injectors used by scenarios/tests

- `policies/`
  - containment + recovery mechanisms (commit, reconcile, circuit breaker, budget)

- `postmortems/`
  - incident writeups linked to FM tests and fixes

- `baselines/`
  - reference implementations or “known broken” baselines (if needed)

---

## Required workflow for any new failure mode (FM_XXX)

For each new FM:

1) Create folder:
   `failure_modes/FM_XXX_short_name/`

2) Write `spec.md` containing:
   - Description
   - Trigger
   - Symptoms
   - Violated invariants (INV_XXX)
   - Detection
   - Recovery / prevention strategy
   - Acceptance criteria

3) Add two tests:
   - `test_repro_fmxxx.py` → demonstrates the failure (baseline or broken variant)
   - `test_prevent_fmxxx.py` → proves the fix preserves invariants

4) Implement minimal runtime/policy changes to satisfy the prevention test.

5) Add a postmortem if it teaches something reusable.

---

## FM_001 guidance (current priority)

FM_001 is duplicate execution due to retry after timeout.

Agent expectations:
- The prevention mechanism must enforce an **idempotency boundary** (COMMITTED)
- Duplicate attempts must no-op safely
- Tests must prove “at least once delivery does not imply double effects”

---

## Test standards

- Prefer `pytest`
- No real wall-clock sleeps unless explicitly unavoidable
- All tests should use:
  - in-memory SQLite per test (fresh schema)
  - deterministic clock
  - explicit fault injectors

---

## Change acceptance checklist

Before submitting a change, ensure:

- [ ] A new/updated test exists and is the reason the change exists
- [ ] The change references the invariant(s) it protects
- [ ] The failure mode spec is updated (if applicable)
- [ ] No unrelated refactors
- [ ] No new abstractions unless required by at least 2 failure modes
- [ ] Tests are deterministic and fast

---

## Naming conventions

- Invariants: `INV_XXX`
- Failure modes: `FM_XXX`
- Postmortems: `PM_XXX`
- Policy modules should be nouns: `commit.py`, `reconcile.py`, `budget.py`

---

## If uncertain

If you are unsure where something belongs, default to:
1) write/adjust the test
2) update the relevant `docs/` spec
3) implement the smallest change in `runtime/` or `policies/`

Do not broaden scope. Do not add features for completeness.
