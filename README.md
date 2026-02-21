# Predictable Job Queue (correctness under stress)

A minimal job queue built to demonstrate how to ship **fast and reliable** backends: clear invariants, disciplined retries, and recovery paths that preserve correctness when things go wrong.

This is a small, inspectable system you can study and fork to avoid common startup mistakes like duplicate execution, partial writes, and stuck queues.

## Why this matters (startup reality)

- **Protect money & trust:** avoid duplicate charges, inconsistent state, and silent drift
- **Move faster safely:** ship with guardrails (idempotency, retries, replay, reconciliation)
- **Debug in minutes:** deterministic scenarios you can reproduce and fix with tests

## Design principles

- Invariants first: correctness is defined explicitly
- Reliability is a *feature*: recovery must restore correctness, not just uptime
- Small scope on purpose: easier to reason about, easier to copy

## Repo map

- Invariants: [`docs/01_invariants.md`](./docs/01_invariants.md)
- Scope: [`docs/00_scope.md`](./docs/00_scope.md)
- Failure-mode exercises: `failure_modes/FM_XXX_*` with:
  - `spec.md` (what breaks, why it matters, which invariant)
  - `scenario.py` (how to trigger it)
  - tests: one to reproduce, one to prevent

## The system

- A minimal job processor (queue + worker + store + deterministic clock)
- Policies (commit, reconcile, budgets) exist only to protect invariants

## Happy path (baseline)

- Story: [`docs/04_happy_path.md`](./docs/04_happy_path.md)
- Proof: [`tests/test_happy_path.py`](./tests/test_happy_path.py)

## Run it

```bash
make sync
make test
```

## Current focus

**FM_001 — retry duplication → double execution**

```bash
make test-fm1       # reproduces the issue
make test-fm1-fix   # proves the boundary holds
```

Index: [`docs/failure_mode_index.md`](./docs/failure_mode_index.md)

## Contributing: add a reliability exercise

1. Create `failure_modes/FM_XXX_name/`
2. Write `spec.md`: trigger, symptoms, violated invariants (`INV_XXX`), detection, recovery/prevention, acceptance
3. Add two tests:
   - `test_repro_fmxxx.py` (shows the break)
   - `test_prevent_fmxxx.py` (proves the fix)
4. Implement the smallest change that satisfies the prevention test (tied to the invariant)
5. Keep it deterministic (use `runtime/clock.py`), one failure mode per change set
