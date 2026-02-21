### Coding approach

* Decided on **Python + uv + pytest**
* Started **TDD flow**: reproduce FM_001 first, then fix it

### FM_001 reproduction test (planned / partially implemented)

* First test demonstrates the bug exists:

  * lease expires
  * job is retried
  * two workers apply side effect
  * side effect duplicates

This makes FM_001 concrete and measurable.

---


### Stage 1 — Make FM_001 reproducible in code (v0)

1. Implement minimal Store + Queue (SQLite or in-memory SQLite)
2. Implement leasing with `lease_expires_at`
3. Implement naive non-idempotent effect application
4. Ensure the “FM_001 happens” test passes

**Deliverable:** A passing test that shows the bug is real.

---

### Stage 2 — Fix FM_001 with a COMMITTED boundary (core)

5. Write a second test that asserts **correct behavior**:

   * even with duplicate leases, only one logical effect is applied
6. Extend schema/state:

   * add a durable “commit record” for `job_id`
   * enforce “only one commit per job”
7. Implement `commit_effect_idempotent()`:

   * first committer wins
   * duplicates no-op
8. Make the correctness test pass
9. Keep the FM_001 reproduction test as a “pre-fix demonstration” (or mark it as showing the buggy baseline in a separate test module)

**Deliverable:** Regression-proof prevention of FM_001.

---

### Stage 3 — Recovery mechanics (what makes it “real”)

10. Simulate crash:

* crash after COMMITTED but before DONE

11. Add reconciler:

* detects committed-but-not-done executions
* finalizes safely

12. Tests proving recovery restores correctness

**Deliverable:** Recovery is correct, not just availability.

---

### Stage 4 — Add FM_002 and FM_003 (depth, not breadth)

Pick next failure modes that are adjacent:

* FM_002: partial write / torn state update
* FM_003: retry storm causing resource exhaustion + duplicate pressure

Each new FM includes:

* test that reproduces it
* doc entry
* fix
* regression test

**Deliverable:** A growing “failure-mode suite”.

---

### Stage 5 — Postmortems + one publishable walkthrough

13. Write 2 simulated incident reports in `postmortems/`
14. Write one Medium post that links to:

* invariants
* FM_001 test
* the commit/idempotency fix

**Deliverable:** Hiring-grade narrative backed by code.
