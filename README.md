# Train reliability habits

Build predictable software: define each failure mode, reproduce it, and neutralize it with tests and policy. Work one failure at a time, tied to invariants, proving both the break and the fix. Disciplined retries, idempotency, and recovery keep a small queue system correct even when it misbehaves.

## Why it is critical

- Prevent costly mistakes: duplicate charges, partial writes, stuck queues, silent data drift.
- Show reliability practice in a controlled, minimal, inspectable system.
- Target correctness under failure; **recovery must restore correctness, not just uptime**.

## How this repo is organized

- Everything traces to invariants in [`docs/01_invariants.md`](./docs/01_invariants.md).
- One failure mode at a time: each lives in `failure_modes/FM_XXX_*` with a `spec`, `scenario`, and two `tests` (repro + prevent).
- Scope stays small: see [`docs/00_scope.md`](./docs/00_scope.md);

## What system we’re exercising

- A minimal job processor (queue + worker + store + deterministic clock) kept small so failures are easy to see and reason about.
- Policies (commit, reconcile, budgets) exist only to protect invariants.

## Happy path reference

- Story: [`docs/04_happy_path.md`](./docs/04_happy_path.md)
- Proof: [`tests/test_happy_path.py`](./tests/test_happy_path.py)

## How to see and prove failures

- Run the suite:
  ```bash
  make sync
  make test
  ```
- Watch the current focus (FM_001: duplicate retry → double execution):
  ```bash
  make test-fm1       # reproduces the failure
  make test-fm1-fix   # proves the idempotent boundary holds
  ```
- Index of all failure modes and their invariants: [`docs/failure_mode_index.md`](./docs/failure_mode_index.md).

## How to add a failure mode (contribute)

1. Create `failure_modes/FM_XXX_name/`.
2. Write `spec.md`: trigger, symptoms, violated invariants (`INV_XXX`), detection, recovery/prevention, acceptance.
3. Add two tests: `test_repro_fmxxx.py` (shows the break) and `test_prevent_fmxxx.py` (proves the fix).
4. Implement the smallest runtime/policy change to satisfy the prevention test, tied to the stated invariant.
5. Keep it deterministic (use `runtime/clock.py`), one failure mode per change set.
