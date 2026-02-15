# Failure Mode Index

Map of failure modes to the invariants they threaten, the proving tests, and the recovery lever we exercise.
| Failure Mode | Description | Violated Invariants | Repro Test | Prevent Test | Recovery / Policy Lever |
| --- | --- | --- | --- | --- | --- |
| `FM_001` Duplicate Retry | Lease timeout causes duplicate execution of the same job. | [`INV_001`](./01_invariants.md) (logical idempotency) | [`test_repro_fm001.py`](../failure_modes/FM_001_duplicate_retry/tests/test_repro_fm001.py) | [`test_prevent_fm001.py`](../failure_modes/FM_001_duplicate_retry/tests/test_prevent_fm001.py) | Idempotent commit boundary in `Store.apply_effect(enforce_idempotent_commit=True)` (driven by `Faults.enforce_idempotent_commit`). |

> Add new rows as additional FM bundles are introduced. Each entry should link to the spec, tests, and the exact recovery/containment mechanism that preserves the referenced invariants.
