# AGENT CONTEXT — failure-first-job-queue

## Mission

This repository is **not** a generic job queue.

It is a **Failure-First Reliability Lab** designed to:

* model real distributed system failures
* define invariants explicitly
* reproduce failures deterministically
* implement minimal fixes
* prove correctness through tests

Primary target failure:

```
FM_001 — Duplicate execution caused by retry after timeout
```

Everything in this repository exists to explore failure modes.

No feature work unless it supports a failure.

---

## Engineering Philosophy

Failure is the default operating condition.

Agents must optimize for:

* correctness over availability
* explicit invariants over implicit behavior
* deterministic testing
* minimal implementation surface
* recovery logic over happy-path logic

Retries are assumed unsafe until proven idempotent.

---

## Current Architecture Snapshot

### Docs (source of truth)

```
docs/00_scope.md
docs/01_invariants.md
docs/02_state_model.md
docs/03_failure_modes.md
```

Reading order for any agent:

1. 00_scope
2. 01_invariants
3. 02_state-model
4. failure_modes/FM_XXX/spec.md

---

### Runtime Layer

```
runtime/
  queue.py
  worker.py
  store.py
  schema.py
  effects.py
  clock.py
```

Runtime is intentionally minimal.

No performance concerns.
No external services.
SQLite or in-memory store only.

---

### Failure Mode Layout

Each failure lives in:

```
failure_modes/FM_XXX_<name>/
  spec.md
  scenario.py
  tests/
    test_repro_*.py
    test_prevent_*.py
```

Rules:

* repro test shows failure exists
* prevent test shows invariant preserved

---

### Policies Layer

```
policies/
  commit.py
  reconcile.py
  circuit_breaker.py
  budget.py
```

Policies exist to:

* enforce invariants
* contain failures
* restore correctness

---

### Fault Injection

```
faults/injectors.py
```

All failures must be reproducible via deterministic injectors.

No random failures allowed.

---

## What Has Been Implemented Conceptually

* Scope defined
* Invariants defined (INV_001..)
* State model defined
* FM_001 specified
* Repo structured for failure-driven development
* TDD workflow established

We are currently in:

```
Stage 1 — Reproduce FM_001
```

---

## Current Goal (Immediate)

Build minimal runtime behavior so this test is meaningful:

```
test_repro_fm001.py
```

Expected baseline behavior:

```
Duplicate effects occur.
```

This is intentional.

We are **not fixing it yet**.

---

## Next Planned Evolution

After repro test is stable:

1. Introduce COMMITTED boundary
2. Enforce single logical execution
3. Implement idempotent commit policy
4. Make `test_prevent_fm001.py` pass

---

## Absolute Rules for Codex

1. Tests first. Always.
2. No new abstractions unless demanded by multiple failure modes.
3. No performance optimizations.
4. No wall-clock sleeps — use runtime.clock.
5. Every code change must reference an invariant or failure mode.
6. Do not broaden scope.

---

## What This Project Is Training

This repository exists to demonstrate:

* reliability engineering thinking
* failure-mode analysis
* invariant-driven design
* recovery-first architecture

The goal is to produce hiring-grade artifacts for reliability-focused roles.

---

## Agent Behavior Expectations

When editing:

* Read docs/01_invariants.md before coding.
* Modify runtime only to satisfy a failing test.
* Prefer smallest change possible.
* Do not “improve” code outside current failure mode.

---

## Current State of FM_001

FM_001 occurs when:

1. Worker A leases job.
2. Lease expires.
3. Worker B leases same job.
4. Both apply side effects.

Invariant violated:

```
INV_001 — logical idempotency
```

---

## Resume Anchor (Career Context)

Author is building a public reliability portfolio to:

* land infra/reliability roles
* reach ~$5k/month income
* attract crypto / AI infra companies
* demonstrate failure-mode engineering expertise

Artifacts must read like internal engineering work, not tutorials.

---

## If Codex Is Unsure

Default action order:

1. open failure_modes/FM_001/spec.md
2. open docs/01_invariants.md
3. inspect failing tests
4. implement minimal runtime change

Never add features proactively.

---

# END CONTEXT